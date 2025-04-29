from llm_programs.programs.types import Prompter, Engine, Parser

from .prompters.prompters import KeywordPrompter
from .engines import LocalLM

from typing import Any, TypeVar, Callable, Iterable, List, Optional


IDENTITY = lambda x: x

LMProgram = Callable[..., Any]


class LMFunction:
    def __init__(
            self,
            prompter: Prompter = KeywordPrompter(),
            engine: Engine = LocalLM(),
            parser: Parser = IDENTITY):
        self.prompter = prompter
        self.engine = engine
        self.parser = parser

    def __call__(self, *args, **kwargs):
        prompt = self.prompter(*args, **kwargs)
        response = self.engine(prompt)
        output = self.parser(response)
        return output


class TemplatedFunction(LMFunction):
    """A special case of LMFunction with a pre-set prompt template"""
    def __init__(self, template, engine=LocalLM(), parser=IDENTITY):
        super().__init__(engine=engine, parser=parser)
        self.template = template
    
    def __call__(self, **kwargs):
        kwargs["template"] = self.template
        return super().__call__(**kwargs)

