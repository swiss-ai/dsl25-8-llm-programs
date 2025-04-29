from typing import Callable, Any

Prompter = Callable[..., str]
Engine = Callable[[str], str]
Parser = Callable[[str], Any]

