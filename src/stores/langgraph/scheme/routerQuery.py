from pydantic import BaseModel, Field
from typing import Literal

# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search", "external"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )