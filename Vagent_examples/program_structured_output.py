from vagent.core import VContext, llm_program
from pydantic import BaseModel, Field


class Summary(BaseModel):
    title: str = Field(..., title="Title of the summary")
    content: str = Field(..., title="Content of the summary")


@llm_program(model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.6)
def say_hello(ctx: VContext) -> Summary:
    """You are a helpful assistant"""
    return f"Hello, I'm {ctx.get('name', 'unknown')}, Nice to meet you!"


if __name__ == "__main__":
    ctx = VContext()
    ctx.put("name", "John")
    output = say_hello(ctx)
    print(type(output))
    print(output)
