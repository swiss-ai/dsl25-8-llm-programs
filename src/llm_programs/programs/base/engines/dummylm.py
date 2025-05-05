from time import sleep
import logging
from llm_programs.utils import debug_wrap

logger = logging.getLogger(__name__)

class DummyLM:
    def __init__(self, latency=0):
        self.latency = latency
        self.n_llm_calls = 0

    @debug_wrap
    def __call__(self, prompt):
        logger.debug("DummyLM.__call__")
        sleep(self.latency)
        self.n_llm_calls += 1
        return prompt
