from types import NoneType
from llm_programs.programs.base import LMFunction, LMProgram


from functools import reduce
from collections.abc import Iterable

from typing import Callable, TypeVar

import concurrent.futures

InputType = TypeVar('InputType')
StateType = TypeVar('StateType')
OutputType = TypeVar('OutputType')

T = TypeVar('T')

class RecurrentLM(LMProgram):
    def __init__(self,
                 f: Callable[[InputType, StateType], StateType],
                 g: Callable[[StateType], OutputType]):
        """A recurrent LM Program, (a la RNN)
        
        Args:
            f: An (LM) Function expecting two positional arguments `input` and `prev_hidden`. Computes the new hidden state h[t] given the previous hidden state h[t-1] and the input x[t].
            g: An (LM) Function expecting one argument `hidden`. Computes the output y[t] given the hidden state h[t].
        """
        self.f = f
        self.g = g
        self.hidden = None

    def __call__(self, input: InputType) -> OutputType:
        """Compute the output given the input and the previous hidden state"""
        self.hidden = self.f(input, self.hidden)
        output = self.g(self.hidden)
        return output

    def reset(self):
        """Reset the hidden state"""
        self.hidden = None


class MapReduce(LMProgram):
    def __init__(self,
                 map_fn: Callable[[InputType], OutputType],
                 reduce_fn: Callable[[Iterable[OutputType]], OutputType],
                 rf: int = 2,
                 parallel = False,
                 max_workers: int | NoneType = None):
        """
        A (very simplified) MapReduce Program
        
        Args:
            map_fn: An (LM) Function (A -> B) expecting one argument `input` (of type A).
            reduce_fn: An (LM) Function (Iterable[B] -> B) expecting one argument `inputs` (of type Iterable[B]).
            rf: Reduction factor, the number of elements to reduce at a time at most. Default is 2.

        NOTE: maybe not mem-efficient
        """
        if rf < 2:
            raise ValueError("Reduction factor (rf) must be at least 2")
        self.map_fn = map_fn
        self.reduce_fn = reduce_fn
        self.max_workers = max_workers
        self.rf = rf
        if parallel:
            self.mapper = lambda *args: parallel_mapper(*args, max_workers=self.max_workers)
        else:
            self.mapper = simple_mapper

    def __call__(self, inputs: Iterable[InputType], debug=False) -> OutputType:
        """
        Args:
            inputs: list[A]
        Returns:
            output: B
        """
        results = self.mapper(self.map_fn, inputs)
        if debug: self.aux = {'mapped': list(results), 'reductions': []}

        while len(results) > 1:
            results = self.mapper(self.reduce_or_not, self.group_by_rf(results))
            if debug: self.aux['reductions'].append(results)

        output = results[0]
        return output

    def reduce_or_not(self, inputs: Iterable[InputType]) -> OutputType:
        if len(inputs) == 1:
            return inputs[0]
        else:
            return self.reduce_fn(inputs)

    def group_by_rf(self, inputs: Iterable[InputType]) -> Iterable[OutputType]:
        """Group by reduction factor"""
        return (inputs[i:i+self.rf] for i in range(0, len(inputs), self.rf))


class LeftReduce(LMProgram):
    """
    Reduce a sequence from left to right
    
    Args:
        f: An (LM) Function (T,T -> T) accepting two positional arguments (of type T).
    """
    def __init__(self, f: Callable[[T, T], T]):
        self.f = f
    
    def __call__(self, inputs):
        return reduce(self.f, inputs)


def mk_unary(fn):
    """Make an (LM) function expecting one kw argument `input` positional"""
    return lambda input: fn(input=input)


def mk_binary(fn):
    """Make an (LM) function expecting two kw arguments `inputa` and `inputb` positional"""
    return lambda inputa, inputb: fn(inputa=inputa, inputb=inputb)


def simple_mapper(fn, inputs):
    return [fn(input) for input in inputs]


def parallel_mapper(fn, inputs, max_workers=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fn, inputs))

