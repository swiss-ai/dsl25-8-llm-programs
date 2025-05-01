import fire
import logging
import sys

from pathlib import Path

from llm_programs.programs.base.engines import Gemini, DummyLM
from llm_programs.utils import DocumentDirectory
from llm_programs.tasks.contract_generation.redaction.generate import generate_contract_aux

class Experiment:
    def __init__(self):
        pass

    def full_eval(self):
        print("hello full_eval")
        data = self.get_or_gen_synth_contracts(n_samples=10)
        
    def eval(self):
        pass

    def get_or_gen_synth_contracts(self, n_samples, seed=42) -> DocumentDirectory:
        path = Path("./data/contracts/synth/") / f"docs_n{n_samples}_seed{seed}"
        print(f"get_or_gen_synth_contracts: {path}")
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
        python src/llm_programs/tasks/redaction/eval.py full_eval
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout)
    fire.Fire(Experiment)