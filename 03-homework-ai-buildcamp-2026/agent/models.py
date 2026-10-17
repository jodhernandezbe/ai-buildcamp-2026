from pydantic import BaseModel, Field


class SQLResult(BaseModel):
    sql_query: str = Field(description="The final SQL query that produced the answer")
    result_text: str = Field(description="The query result, or a short answer based on it")
    row_count: int = Field(description="Number of rows returned by the final query")
