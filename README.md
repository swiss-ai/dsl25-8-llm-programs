# LLM Program Blueprints
## ETH Zurich Data Sc. Lab Spring 2025 Team #8

## LM Functions

In our realisation, LM Function is a function composed of three parts: a prompter, an LM engine, and a parser:
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

## LM Programs

LM Programs build upon LM Functions. This repository features:
- LM MapReduce
- Recurrent LM (a la RNN)
- Generalized Information Extraction Program (Map + Filter)
- ... and more

## Development Installation

```sh
git clone git@github.com:swiss-ai/dsl25-8-llm-programs.git
cd dsl25-8-llm-programs.git
pip install -e .
```
