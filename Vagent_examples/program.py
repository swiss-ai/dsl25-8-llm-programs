from vagent.core import VContext, llm_program


@llm_program(model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.6)
def say_hello(ctx: VContext):
    """You are a helpful assistant, and you always say `Welcome to the world!` as the last sentence."""
    return f"Hello, I'm {ctx.get('name', 'unknown')}, Nice to meet you!"


if __name__ == "__main__":
    ctx = VContext()
    ctx.put("name", "John")
    print(say_hello(ctx))
