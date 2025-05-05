from llm_programs.programs.types import Prompter

import re
from typing import List


class ArgsPrompter(Prompter):
    def __init__(self, template: str, order: list[str]):
        self.template = template
        self.order = order
        self.n_args = len(order)

    def __call__(self, *args) -> str:
        print(f"{self.template=}")
        print(f"{self.n_args=}")
        print("ARGS:", args)
        assert len(args) == self.n_args, f"Expected {self.n_args} args, got {len(args)}"
        ctx = {self.order[i]: args[i] for i in range(self.n_args)}
        return self.template.format_map(ctx)


class AutoPrompter(ArgsPrompter):
    def __init__(self, template: str):
        super().__init__(template, order=extract_variables(template))


class KeywordPrompter(Prompter):
    def __call__(self, *args, **ctx) -> str:
        # if args: print(f"args: {args}")
        # if ctx: print(f"ctx: {ctx}")
        template = None
        if args:
            template = args[0]
        else:
            template = ctx.get("template", None)
        if template is None:
            return ' '.join(list(ctx.values()))
        elif ctx:
            return template.format_map(ctx)
        else:
            return template


class JoinPrompter():
    def __init__(self, template, sep='\n\n', rm_newlines=True):
        self.template = template
        self.sep = sep
        self.rm_newlines = rm_newlines

    def __call__(self, inputs):
        if self.rm_newlines:
            inputs = [v.replace('\n', ' ').strip() for v in inputs]
        return self.sep.join(inputs)


def extract_variables(template_string: str) -> List[str]:
  """
  Args:
    template_string: The string containing placeholders like {variable}.

  Returns:
    A list of variable names found in the template, in order of appearance.
    NOTE: Duplicates are included if they appear multiple times.
    Includes full identifier (e.g., 'person.name', 'value:0.2f').
  """
  # Regular expression breakdown:
  # \{     : Matches the literal opening curly brace.
  # (      : Starts a capturing group (this is what findall returns).
  # [^{}]+ : Matches one or more characters that are NOT curly braces.
  #          This captures the variable name inside the braces.
  # )      : Ends the capturing group.
  # \}     : Matches the literal closing curly brace.
  pattern = r'\{([^{}]+)\}'

  variables = re.findall(pattern, template_string)
  return variables

