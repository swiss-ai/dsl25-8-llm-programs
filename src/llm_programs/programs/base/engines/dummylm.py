from time import sleep
import logging

logger = logging.getLogger(__name__)

class DummyLM:
    def __init__(self, latency=0):
        self.latency = latency

    def __call__(self, prompt):
        logger.debug("DummyLM.__call__")
        sleep(self.latency)
        return prompt
