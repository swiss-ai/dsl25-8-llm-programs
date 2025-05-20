import fire
import logging
import sys

from pathlib import Path
from functools import partial, reduce
from typing import Callable

from llm_programs.programs.base.engines import Gemini, DummyLM, LocalLM
from llm_programs.programs.base.parsers import lines_parser
from llm_programs.programs.base.prompters import AutoPrompter, ArgsPrompter

from llm_programs.utils import DocumentDirectory, Document, flat, unionize, save
from llm_programs.tasks.contract_generation.redaction.generate import generate_contract_aux
from llm_programs.programs.base import LMFunction, LMProgram, TemplatedFunction

from .templates import TEMPLATE_FILTER_ALL, REDACTION_TEMPLATES
from .metrics import measure_naive_precision_recall, measure_redaction_precision_recall

import logging
logger = logging.getLogger(__name__)

results_dir = Path("./results/redaction/synth/")

# engine = Gemini(model_name="gemma-3-27b-it", rpm=30, debug=True)
# engine = DummyLM()
engine = LocalLM(model_name="gemma-3-27b-it")

one_call_one_prompt_fn = LMFunction(prompter=AutoPrompter(TEMPLATE_FILTER_ALL), engine=engine, parser=lines_parser)

m_fns = [LMFunction(prompter=AutoPrompter(template), engine=engine, parser=lines_parser)
         for template in REDACTION_TEMPLATES.values()]


def one_call_m_prompts_fn(content: str) -> list[str]:
    return list(set(flat(fn(content) for fn in m_fns)))

## TODO Amplifier Pattern

def n_calls_m_prompts_fn(content: str, n = 4, aggr_fn: Callable[[set[str], set[str]], set[str]] = set.union) -> list[str]:
    outputs = [one_call_m_prompts_fn(content) for _ in range(n)]
    return list( reduce(lambda a, b: aggr_fn(set(a), set(b)), outputs ) )

n_calls_m_prompts_fn_or = partial(n_calls_m_prompts_fn, aggr_fn=set.union)
n_calls_m_prompts_fn_and = partial(n_calls_m_prompts_fn, aggr_fn=set.intersection)


def unionize_windows(method: Callable[[str], list[str]], doc: Document, **win_kw) -> set[str]:
    return unionize(method(window) for window in doc.windows(**win_kw))


class RedactionExperiment:
    def __init__(self):
        pass

    def full_synth_eval(self):
        n_samples = 10
        seed = 42
        window_size = 10_000
        window_offset = 100
        window_stride = window_size - window_offset
        # LMPrograms should accept str (window content) and return list[str] (redacted substrings)
        methods: dict[str, Callable[[str], list[str]]] = {
            "1 call, 1 prompt": one_call_one_prompt_fn,
            "1 call, M prompts": one_call_m_prompts_fn,
            "N calls, M prompts, OR": n_calls_m_prompts_fn_or,
            "N calls, M prompts, AND": n_calls_m_prompts_fn_and,
            # "1 calls, double-checked" : ...
        }
        data_dd: DocumentDirectory = self.get_or_gen_synth_contracts(n_samples=n_samples, seed=seed)
        results = {}
        for method_name, method in methods.items():
            logger.debug(f"evaluating method: {method_name}")
            results[method_name] = {}
            for doc in data_dd.docs():
                logger.debug(f"evaluating document: {doc.name}")
                contract = doc.read()
                true_keywords = eval(doc.read_aux("info"))
                true_keywords = [v for k in true_keywords for v in true_keywords[k]]
                pred_keywords = unionize_windows(method, doc, size=window_size, stride=window_stride)
                naive_precision, naive_recall = measure_naive_precision_recall(contract, true_keywords, pred_keywords)
                red_precision, red_recall = measure_redaction_precision_recall(contract, true_keywords, pred_keywords)
                results[method_name][doc.name] = {
                    "naive_precision": naive_precision,
                    "naive_recall": naive_recall,
                    "red_precision": red_precision,
                    "red_recall": red_recall,
                    "pred_keywords": pred_keywords,
                }
        save(results, (results_dir / f"eval_n{n_samples}_seed{seed}.pkl"))
        logger.debug(f"{engine.n_llm_calls=}")
       
    def eval(self):
        pass

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
    Usage:
        python -m src.llm_programs.tasks.redaction.eval full_synth_eval
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout)
    fire.Fire(RedactionExperiment)

