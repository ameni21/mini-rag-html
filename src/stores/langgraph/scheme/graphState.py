from typing import List, Optional

from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """

    project_id: int
    question: str
    generation: Optional[str]
    documents: Optional[List[str]]