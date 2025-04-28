
from .base import LMFunction

class RecurrentLM():
    def __init__(self, f: LMFunction, g: LMFunction):
        """A recurrent LM Program, (a la RNN)
        
        Args:
            f: An LM Function expecting keyword arguments `input` and `prev_hidden`. Computes the new hidden state h[t] given the previous hidden state h[t-1] and the input x[t].
            g: An LM Function expecting a keyword argument `hidden`. Computes the output y[t] given the hidden state h[t].
        """
        self.f = f
        self.g = g
        self.hidden = None

    def __call__(self, input):
        """Compute the output given the input and the previous hidden state"""
        self.hidden = self.f(input=input, prev_hidden=self.hidden)
        output = self.g(hidden=self.hidden)
        return output

    def reset(self):
        """Reset the hidden state"""
        self.hidden = None


class MapReduce():
    def __init__(self, map_fn: LMFunction, reduce_fn: LMFunction, rf=2):
        """
        A (very simplified) MapReduce Program
        
        Args:
            map_fn: An LM Function (A -> B) expecting keyword arguments `input` (of type A).
            reduce_fn: An LM Function (list[B] -> B) expecting a keyword argument `args` (list[B]).
            rf: Reduction factor, the number of elements to reduce at a time at most. Default is 2.
        """
        self.map_fn = map_fn
        self.reduce_fn = reduce_fn

    def __call__(self, inputs):
        """
        Args:
            inputs: list[A]
        Returns:
            output: B
        """
        results = [self.map_fn(input=input) for input in inputs]

        while len(results) > 1:
            results = [self.reduce_or_not(results[i:i+self.rf]) for i in range(0, len(results), self.rf)]
        output = results[0]
        return output

    def reduce_or_not(self, args):
        if len(args) == 1:
            return args[0]
        else:
            return self.reduce_fn(args=args)


        # NOTE: maybe not mem-efficient

