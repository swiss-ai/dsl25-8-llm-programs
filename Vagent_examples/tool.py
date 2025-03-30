import pandas as pd
from vagent.executor import LocalFuncExecutor
from vagent.core import llm_program, VContext
from vagent.builtins import execute_sql_on_dataframe


@llm_program(
    model="meta-llama/Llama-3.3-70B-Instruct", tools=[execute_sql_on_dataframe]
)
def generate_sql(ctx: VContext, prompt: str):
    """You are an expert in generating SQL statements to answer particular queries expressed in natural language."""
    return f"{prompt}."


if __name__ == "__main__":
    ctx = VContext()
    df = pd.read_csv(
        "https://raw.githubusercontent.com/pandas-dev/pandas/refs/heads/main/doc/data/titanic.csv"
    )
    res = generate_sql(
        ctx,
        f"Given the first row of a dataframe called `df`: {df.head(n=1)}, and the query: 'How many passengers survived?', please write the SQL statement that would answer the query.",
    )
    print(res)
    executor = LocalFuncExecutor(tools=[execute_sql_on_dataframe])
    output = executor(res, df=df)
    print(output)
