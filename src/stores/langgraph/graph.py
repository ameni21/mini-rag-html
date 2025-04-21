from langgraph.graph import StateGraph, START, END
from stores.langgraph.scheme.graphState import GraphState
from typing import Callable, Dict, Any

class Graph:
    def __init__(self, handlers):
        self.handlers = handlers
        self.graph = StateGraph(GraphState)
        
    # Define conditional edge handlers that correctly return the routing decision
    async def route_to_source(self, state):
        # Call the original handler and get the state update
        new_state = await self.handlers["route_question_to_source"](state)
        # Return just the decision string
        return new_state["decision"]
        
    async def evaluate_relevance_decision(self, state):
        # Call the original handler and get the state update
        new_state = await self.handlers["evaluate_document_relevance"](state)
        # Return just the decision string
        return new_state["decision"]
        
    async def validate_quality_decision(self, state):
        # Call the original handler and get the state update
        new_state = await self.handlers["validate_answer_quality"](state)
        # Return just the decision string
        return new_state["decision"]

    def build(self):
        # First add all nodes
        self.graph.add_node("web_search", self.handlers["web_search"])
        self.graph.add_node("search_documents", self.handlers["search_documents"])
        self.graph.add_node("evaluate_relevance", self.handlers["evaluate_document_relevance"])
        self.graph.add_node("generate_rag", self.handlers["generate_with_context"])
        self.graph.add_node("generate_llm", self.handlers["generate_with_llm_only"])
        self.graph.add_node("validate_generation", self.handlers["validate_answer_quality"])
        self.graph.add_node("reformulate_query", self.handlers["reformulate_question"])

        # Start routing - use the wrapper function that returns just the decision
        self.graph.add_conditional_edges(
            START,
            self.route_to_source,
            {
                "web_search": "web_search",
                "vectorstore": "search_documents",
                "internal": "generate_llm",
            }
        )

        # direct with LLM
        self.graph.add_edge("generate_llm", END) 

        # Web Search path
        self.graph.add_edge("web_search", "generate_rag")
        

        # Vectorstore path
        self.graph.add_edge("search_documents", "evaluate_relevance")
        
        # From evaluate_relevance, either generate or reformulate
        self.graph.add_conditional_edges(
            "evaluate_relevance",
            self.evaluate_relevance_decision,
            {
                "generate": "generate_rag",
                "transform_query": "reformulate_query",
            },
        )

        # Reformulate query leads back to search
        self.graph.add_edge("reformulate_query", "search_documents")
        
        # Validate generation leads to end or reformulation or retry
        self.graph.add_conditional_edges(
            "validate_generation",
            self.validate_quality_decision,
            {
                "useful": END,
                "reformulate_query": "reformulate_query",
                "retry_generation": "generate_rag",
            }
        )

        return self.graph.compile()