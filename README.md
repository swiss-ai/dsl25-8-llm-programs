# LLM Program Blueprints
## ETH Zurich Data Sc. Lab Spring 2025 Team #8

LLM Programs (also known as *compound LLM systems*, *LLM workflows and agents*, or *LLM-based algorithms*) are classical programs with some subroutines implemented via LLM calls.
The aim of our project was two-fold:
1. to draft a collection of blueprints and lessons-learned for LLM Programs,
2. to write LLM Programs to redact and search through the paragraphs of several hundred contracts for a specific subject (*"AI compliance"*).

### Aim 1: Blueprints

To effectively develop LLM programs, we have found it most convenient to wrap LLM calls into *"LLM Functions"* (functions in the sense of subroutines), as this allows us to employ them in standard, idiomatic ways.
For instance, if we have an unary predicate LLM function (that is, LLM-implemented subroutine of one argument that returns a boolean, type signature `Callable[[Any], bool]`), we may use it the built-in higher-order functions `map` or `filter`, or as a condition in an `if`-statement or a `while`-loop.
Or, for instance, we may apply a generic evolutionary search algorithm (e.g. within the DEAP framework) on a population of strings, with a binary LM function implementing the cross-over operator.

The code for LLM Functions and Programs is in the `llm_programs.programs` subpackage at `src/llm_programs/programs`.
The `llm_programs.programs.base` subpackage contains definitions of the LM Function, some prompters, engines, and parsers, notably prompters for n-ary functions, and parsers for predicate functions (for clarifications see the *LM Functions* section below).
The `llm_programs.programs.collection` subpackage contains some LLM Programs building on `base`.
We have *not* implemented every single LLM program we have encountered in the literature review, but only those that promised to be useful in the contract processing tasks.
However, given the functional abstraction, writing any particular LLM programming pattern (e.g. *Vote* or *Filter-Vote*) becomes fairly easy with use of built-in or standard-library primitives.

### Aim 2: Processing contracts

Code related to our practical tasks is in the `llm_programs.tasks` subpackage. It includes code for cleaning, redaction, synthetic contract generation and paragraph retrieval (TODO add).

### TLDR: The most important .py files

- [`src/llm_programs/programs/base/base.py`](http://github.com/swiss-ai/dsl25-8-llm-programs/blob/main/src/llm_programs/programs/base/base.py): LM Function blueprint
- [`src/llm_programs/programs/collection/collection.py`](https://github.com/swiss-ai/dsl25-8-llm-programs/blob/main/src/llm_programs/programs/collection/collection.py): Select LM Programs
- [`src/llm_programs/tasks/complete_pipeline.py`](https://github.com/swiss-ai/dsl25-8-llm-programs/blob/main/src/llm_programs/tasks/complete_pipeline.py): The contracts processing pipeline: cleaning and redaction
- TODO add code link for paragraph retrieval

## LM Functions

In our implementation, an LM Function is a function composed of three parts: a prompter, an LM engine, and a parser:
- The prompter takes in arguments and formats them into a prompt.
- The engine calls an LM (local or otherwise) with the prompt, and returns the response.
- The parser (optionally) transforms the response.

```py
Prompter = Callable[..., str]
Engine = Callable[[str], str]
Parser = Callable[[str], Any]

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
```

Note: other realisations of LM-based functions are possible, for instance involving logits, or evaluating conditioned probabilities of specific strings, like `Yes` or `No`.

### LM Function showcase

The below code shows how to construct a simple factchecking LM function that can easily be used with a higher-order function like `filter`:

```py
from llm_programs.programs import LMFunction, AutoPrompter, Gemini, YesNoPredicateParser

# There is only *one* placeholder in the prompt template,
# so AutoPrompter will result in a *unary* function.
template = '''Is the following statement true? \'{statement}\'
Begin your answer with "Yes" or "No".'''
prompter = AutoPrompter(template)

engine = Gemini(debug=True)

# The parser will return a boolean value (True for Yes, False for No)
parser = YesNoPredicateParser()

# We have a Gemini-powered unary predicate function! 
factcheck = LMFunction(prompter=prompter, engine=engine, parser=parser)

statements = [
    "Bats are the only mammals capable of sustained flight.", # True
    "A group of flamingos is called a flamboyance.", # True
    "Koalas are bears.", # False
    "Penguins live in the Arctic.", # False
]

# Using an LLM function with built-in `filter`
print("True statements:", list(filter(factcheck, statements)))
```

An example of the [*evaluator-optimizer*](https://www.anthropic.com/engineering/building-effective-agents) workflow in a mere couple of lines (`while`-loop):

```py
prompt = '''Invent a new plausible realistic fact about penguins that sounds true
but is actually subtly false. State it in one very brief sentence.'''

generate = LMFunction(
    prompter=AutoPrompter(prompt),
    engine=engine,
)

# Search for a bogus fact that can fool Gemini
fact = generate()
while not factcheck(fact):
    fact = generate()
print("Bogus fact that fooled Gemini:", fact)
```

## LM Programs

LM Programs build upon LM Functions. This repository features:
- LM MapReduce
- Recurrent LM (a la RNN)
- Generalized Information Extraction Program (Map + Filter)

## Development Installation

```sh
git clone git@github.com:swiss-ai/dsl25-8-llm-programs.git
cd dsl25-8-llm-programs
conda create -n env3.12-dsl-repr python=3.12 -y
conda activate env3.12-dsl-repr
uv pip install -e '.[dev]'
```

## Running examples

Please see the notebook [sample.py](https://github.com/swiss-ai/dsl25-8-llm-programs/blob/main/notebooks/sample.ipynb). \
It contains:
- The LM Function examples from this README
- Synthetic document redaction
