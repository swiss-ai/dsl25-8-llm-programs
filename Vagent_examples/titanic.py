from vagent.core import VContext, VModule, llm_program
from vagent.builtins import execute_sql_on_dataframe, summarize
from vagent.executor import LocalFuncExecutor
import pandas as pd


class Text2SQL(VModule):
    def __init__(self):
        super().__init__()
        self.tools = [execute_sql_on_dataframe]
        self.executor = LocalFuncExecutor(tools=self.tools)

        @llm_program(
            model="meta-llama/Llama-3.3-70B-Instruct",
            temperature=0.3,
            max_tokens=1024,
            tools=[execute_sql_on_dataframe],
        )
        def generate_sql(ctx: VContext, df: pd.DataFrame, query: str) -> str:
            """You are an expert in generating SQL statements to answer particular queries expressed in natural language."""
            return f"Given the first row of a dataframe called `df`: {df.head(n=1)}, and the query: {query}, please write the SQL statement that would answer the query."

        self.generate_sql = generate_sql
        self.summarize = summarize

    def forward(self, df: "pd.DataFrame", query: str) -> str:
        sql = self.generate_sql(self.ctx, df, query)
        func_output = self.executor(sql, df=df)
        summarized_output = self.summarize(
            self.ctx,
            f"Given the df: {df.head(n=1)}, to answer the question '{query}', I executed the following SQL statement: {sql}. The result is: {func_output}. ",
        )
        return summarized_output


if __name__ == "__main__":
    df = pd.read_csv(
        "https://raw.githubusercontent.com/pandas-dev/pandas/refs/heads/main/doc/data/titanic.csv"
    )
    module = Text2SQL()
    result = module.forward(df=df, query="How many passengers survived?")
    print(result)
