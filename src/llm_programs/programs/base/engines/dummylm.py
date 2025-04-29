from time import sleep

class DummyLM:
    def __init__(self, latency=0):
        self.latency = latency

    def __call__(self, prompt):
        sleep(self.latency)
        return prompt