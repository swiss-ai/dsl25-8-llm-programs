from pydantic import BaseModel, Field
from vagent.core import LLMEngine


class Summary(BaseModel):
    title: str = Field(..., title="Title of the summary")
    content: str = Field(..., title="Content of the summary")


if __name__ == "__main__":
    engine = LLMEngine("meta-llama/Llama-3.3-70B-Instruct")
    res = engine(
        [{"role": "user", "content": "What's the weather like in New York?"}],
        response_format=Summary,
    )
    print(res)
