import fire
import logging
import sys
import time

from pathlib import Path
from functools import partial, reduce
from typing import Any, Callable

from rich.logging import RichHandler

from llm_programs.programs.base.engines import Gemini, DummyLM, LocalLM
from llm_programs.programs.base.parsers import lines_parser
from llm_programs.programs.base.prompters import AutoPrompter, ArgsPrompter

from llm_programs.utils import DocumentDirectory, Document, flat, unionize, save, load
from llm_programs.tasks.contract_generation.redaction.generate import generate_contract_aux
from llm_programs.programs.base import LMFunction, LMProgram, TemplatedFunction

from .templates import TEMPLATE_FILTER_ALL, REDACTION_TEMPLATES
from .metrics import measure_naive_precision_recall, measure_redaction_precision_recall

import logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger("rich")
logger.setLevel(logging.DEBUG)

results_dir = Path("./results/redaction/synth/")

PREFER_LOCAL = False
DEBUG = False


if PREFER_LOCAL:
    engine = LocalLM(model_name="gemma-3-27b-it")
else:
    engine = Gemini(model_name="gemma-3-27b-it", rpm=30, debug=DEBUG)
# engine = DummyLM()


one_call_one_prompt_fn = LMFunction(prompter=AutoPrompter(TEMPLATE_FILTER_ALL), engine=engine, parser=lines_parser)

m_fns = [LMFunction(prompter=AutoPrompter(template), engine=engine, parser=lines_parser)
         for template in REDACTION_TEMPLATES.values()]


def one_call_m_prompts_fn(content: str) -> list[str]:
    return list(set(flat(fn(content) for fn in m_fns)))


def n_calls_m_prompts_fn(content: str, n = 4, aggr_fn: Callable[[set[str], set[str]], set[str]] = set.union) -> list[str]:
    outputs = [one_call_m_prompts_fn(content) for _ in range(n)]
    return list( reduce(lambda a, b: aggr_fn(set(a), set(b)), outputs ) )


n_calls_m_prompts_fn_or = partial(n_calls_m_prompts_fn, aggr_fn=set.union)
n_calls_m_prompts_fn_and = partial(n_calls_m_prompts_fn, aggr_fn=set.intersection)


def unionize_windows(method: Callable[[str], list[str]], doc: Document, **win_kw) -> set[str]:
    return unionize(method(window) for window in doc.windows(**win_kw))


def compare(xs, ys):
    return tuple(y - x for x, y in zip(xs, ys))


class RedactionExperiment:
    def __init__(self):
        # method_key -> method_fn
        # LMPrograms should accept str (window content) and return list[str] (redacted substrings)
        self.methods: dict[str, Callable[[str], list[str]]] = {
            "1 call, 1 prompt": one_call_one_prompt_fn,
            "1 call, M prompts": one_call_m_prompts_fn,
            "N calls, M prompts, OR": n_calls_m_prompts_fn_or,
            "N calls, M prompts, AND": n_calls_m_prompts_fn_and,
            # "1 call, M prompts, double-checked" : ...
        }
        self.results = {}

    def eval_method(self,
                    key: Any,
                    method_fn: Callable[[str], list[str]],
                    data_dd: DocumentDirectory,
                    window_size: int,
                    window_stride: int,
                    save_path: str | Path
                    ) -> None:
        # logger.debug(f"Evaluating method: {key}")
        self.results[key] = {}
        for doc in data_dd.docs():
            if key in self.results and doc.name in self.results[key]:
                logger.debug(f"Skipping: [key = {key}] [doc = {doc.name}]")
                continue
            logger.debug(f"Evaluating document: {doc.name}")
            contract = doc.read()
            true_keywords = eval(doc.read_aux("info"))
            true_keywords = [v for k in true_keywords for v in true_keywords[k]]
            time_before = time.perf_counter_ns()
            counters_before = engine.counters # type: ignore
            pred_keywords = unionize_windows(method_fn, doc, size=window_size, stride=window_stride)
            elapsed_ms = (time.perf_counter_ns() - time_before) // 1_000_000 # in milliseconds
            counters_diff = compare(counters_before, engine.counters) # type: ignore
            n_calls, n_in_chars, n_out_chars = counters_diff
            logger.debug(f"Method `{key}` evaluated on `{doc.name}` in {elapsed_ms // 1000} s, "
                         f"{n_calls} calls, {n_in_chars} input chars, {n_out_chars} output chars.")
            naive_precision, naive_recall = measure_naive_precision_recall(contract, true_keywords, pred_keywords)
            red_precision, red_recall = measure_redaction_precision_recall(contract, true_keywords, pred_keywords)
            self.results[key][doc.name] = {
                "naive_precision": naive_precision,
                "naive_recall": naive_recall,
                "red_precision": red_precision,
                "red_recall": red_recall,
                "pred_keywords": pred_keywords,
                "time_ms": elapsed_ms,
                "n_calls": n_calls, 
                "n_in_chars": n_in_chars,
                "n_out_chars": n_out_chars,
            }
            save(self.results, save_path)
    
    def eval_with_different_window_sizes(self):
        window_size_range = [100, 200, 400, 800, 1600, 3200, 6400, 12_800][::-1] #  25_600, 51_200, 102_400]
        window_stride_range = [window_size - 50 for window_size in window_size_range]
        n_document_samples = 10
        seed = 42
        save_path = results_dir / f"eval_windows_ndocs{n_document_samples}_seed{seed}.pkl"
        self.results = load(save_path) if save_path.exists() else {}
        data_dd: DocumentDirectory = self.get_or_gen_synth_contracts(n_samples=n_document_samples, seed=seed)
        for window_size, window_stride in zip(window_size_range, window_stride_range):
            for method_key, method_fn in self.methods.items():
                key = (method_key, window_size)
                if key in self.results:
                    logger.debug(f"Skipping: [key = {key}]")
                    continue
                logger.debug(f"Evaluating method: {method_key} with window size {window_size} and stride {window_stride}")
                self.eval_method(key, method_fn, data_dd, window_size=window_size, window_stride=window_stride, save_path=save_path)
                logger.debug(f"Evaluated  method: {method_key} with window size {window_size} and stride {window_stride}")
                save(self.results, save_path)

    def get_or_gen_synth_contracts(self, n_samples, seed=42) -> DocumentDirectory:
        path = Path("./data/contracts/synth/") / f"docs_n{n_samples}_seed{seed}"
        logger.debug(f"get_or_gen_synth_contracts: {path}")
        return DocumentDirectory.find_or_make(path,
                                              lambda path: self.gen_synth_contracts(path, n_samples=n_samples, seed=seed))
            
    def gen_synth_contracts(self, path: Path, n_samples: int, seed: int = 42) -> DocumentDirectory:
        # Note: LLM API calls do not support seeding
        return DocumentDirectory.from_md_texts_aux(path, (self.gen_contract_entry(i) for i in range(n_samples)))

    def gen_contract_entry(self, i):
        # engine = DummyLM()
        engine = Gemini(debug=True)
        info, descr, contract = generate_contract_aux(engine=engine)
        name = f"synth_contract_{i:03}"
        aux = {
            "info": repr(info),
            "descr": descr,
        }
        return name, contract, aux


if __name__ == "__main__":
    """
    Example usage:
        python -m src.llm_programs.tasks.redaction.eval eval_with_different_window_sizes
    """
    fire.Fire(RedactionExperiment)

