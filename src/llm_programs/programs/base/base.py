from .locallm import LocalLM


class FormatMap():
    def __call__(self, *args, **kwargs):
        # print(f"args: {args}")
        # print(f"kwargs: {kwargs}")
        template = None
        if args:
            template = args[0]
        else:
            template = kwargs.get("template", None)
        if template is None:
            return ' '.join(list(kwargs.values()))
        elif kwargs:
            return template.format_map(kwargs)
        else:
            return template


class LMFunction():
    def __init__(self, prompter=FormatMap(), engine=LocalLM(), parser=lambda x: x):
        self.prompter = prompter
        self.engine = engine
        self.parser = parser

    def __call__(self, *args, **kwargs):
        prompt = self.prompter(*args, **kwargs)
        response_raw = self.engine(prompt)
        output = self.parser(response_raw)
        return output


class TemplatedFunction(LMFunction):
    def __init__(self, template, engine=LocalLM(), parser=lambda x: x):
        super().__init__(engine=engine, parser=parser)
        self.template = template
    
    def __call__(self, **kwargs):
        kwargs["template"] = self.template
        return super().__call__(**kwargs)


def lines_parser(response):
    """
    Parse the response into a list of lines
    """
    return [line.strip() for line in response.split("\n") if line.strip()]