from llm_programs.programs.types import Prompter


class ArgsPrompter(Prompter):
    def __init__(self, template: str, order: list[str]):
        self.template = template
        self.order = order
        self.n_args = len(order)

    def __call__(self, *args) -> str:
        assert len(args) == self.n_args, f"Expected {self.n_args} args, got {len(args)}"
        ctx = {self.order[i]: args[i] for i in range(self.n_args)}
        return self.template.format_map(ctx)


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

