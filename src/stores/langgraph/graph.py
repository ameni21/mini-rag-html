from langgraph.graph import StateGraph, START, END

from stores.langgraph.scheme.graphState import GraphState

class Graph:
    def __init__(self, handlers):
        self.handlers = handlers
        self.graph = StateGraph(GraphState)

    def build(self):
        self.graph.add_node("web_search", self.handlers["web_search"])
        self.graph.add_node("search_documents", self.handlers["search_documents"])
        self.graph.add_node("evaluate_relevance", self.handlers["evaluate_document_relevance"])
        self.graph.add_node("generate_rag", self.handlers["generate_with_context"])
        self.graph.add_node("generate_llm", self.handlers["generate_with_llm_only"])
        self.graph.add_node("validate_generation", self.handlers["validate_answer_quality"])
        self.graph.add_node("reformulate_query", self.handlers["reformulate_question"])

        # Start routing
        self.graph.add_conditional_edges(
            START,
            self.handlers["route_question_to_source"],
            {
                "web_search": "web_search",
                "vectorstore": "search_documents",
                "internal": "generate_llm",
            },
        )

        # Web Search path
        self.graph.add_edge("web_search", "generate_rag")

        # Vectorstore path
        self.graph.add_edge("search_documents", "evaluate_relevance")

        self.graph.add_conditional_edges(
            "evaluate_relevance",
            self.handlers["evaluate_document_relevance"],
            {
                "generate": "generate_rag",
                "transform_query": "reformulate_query",
            },
        )

        self.graph.add_edge("reformulate_query", "search_documents")

        # Generation validation
        self.graph.add_conditional_edges(
            "generate_rag",
            self.handlers["validate_answer_quality"],
            {
                "useful": END,
                "reformulate_query": "reformulate_query",
                "retry_generation": "generate_rag",
            },
        )

        return self.graph.compile()
