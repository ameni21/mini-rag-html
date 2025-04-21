import logging
from services.NLPService import NLPService
from models.db_schemes.minirag.schemes.project import Project
from typing import Dict, Any

logger = logging.getLogger("uvicorn")

class GraphFlow:
    def __init__(self, state: dict, nlp_service: NLPService):
        self.state = state
        self.nlp_service = nlp_service
    
    # Core NLP Actions
    async def search_documents(self, state):
        logger.info("🔍 Searching vectorstore for relevant documents.")
        documents = await self.nlp_service.search_vector_db_collection(project_id=state["project_id"], text=state["question"])
        logger.info(f"🔍 {documents} ")
        return {"documents": documents}
    
    async def run_web_search(self, state):
        logger.info("🌐 Performing web search.")
        docs = await self.nlp_service.web_search_question(query=state["question"])
        return {"documents": docs}
    
    async def generate_with_context(self, state):
        logger.info("🤖 Generating answer with retrieved documents (RAG).")
        answer = await self.nlp_service.answer_rag_question(
            query=state["question"],
            retrieve_documents=state["documents"]
        )
        return {"generation": answer[0]}
    
    async def generate_with_llm_only(self, state):
        logger.info("🧠 Generating answer using only LLM (no external context).")
        answer = await self.nlp_service.answer_llm_question(query=state["question"])
        return {"generation": answer[0]}
    
    # Quality Control Nodes - Include the decision in the state update
    async def evaluate_document_relevance(self, state):
        logger.info("🧪 Evaluating document relevance to the question.")
        score_tuple = await self.nlp_service.gard_documents_retrieval(
            query=state["question"],
            retrieve_documents=state["documents"]
        )
        
        # Handle case where score_tuple is None or score_tuple[0] is None
        if not score_tuple or not score_tuple[0]:
            logger.warning("No document relevance score returned, defaulting to transform_query")
            return {"decision": "transform_query"}
            
        grade = score_tuple[0].binary_score
        logger.info(f"📊 Document Relevance Score: {grade}")
        
        # Return a dict with the decision
        return {"decision": "generate" if grade == "yes" else "transform_query"}
    
    async def validate_answer_quality(self, state):
        logger.info("🧠 Checking hallucinations and answer validity.")
        hallucination_score = await self.nlp_service.GradeHallucinations(
            retrieve_documents=state["documents"],
            generation=state["generation"]
        )
        
        # Handle case where hallucination_score is None or hallucination_score[0] is None
        if not hallucination_score or not hallucination_score[0]:
            logger.warning("No hallucination score returned, defaulting to retry_generation")
            return {"decision": "retry_generation"}
            
        if hallucination_score[0].binary_score != "yes":
            return {"decision": "retry_generation"}
            
        quality_score = await self.nlp_service.gradeAnswer(
            query=state["question"],
            generation=state["generation"]
        )
        
        # Handle case where quality_score is None or quality_score[0] is None
        if not quality_score or not quality_score[0]:
            logger.warning("No quality score returned, defaulting to reformulate_query")
            return {"decision": "reformulate_query"}
            
        logger.info(f"🧪 Answer Quality Score: {quality_score[0].binary_score}")
        
        # Return a dict with the decision
        return {"decision": "useful" if quality_score[0].binary_score == "yes" else "reformulate_query"}
    
    # Decision Nodes
    async def route_question_to_source(self, state):
        logger.info("🧭 Routing question to data source...")
        route = await self.nlp_service.llm_router(state["question"])
        
        # Handle case where route is None or route[0] is None
        if not route or not route[0]:
            logger.warning("No routing decision returned, defaulting to internal")
            return {"decision": "internal"}
            
        logger.info(f"➡️ Routed to: {route[0].datasource}")
        
        # Return a dict with the decision
        return {"decision": route[0].datasource}  # one of: "web_search", "vectorstore", "internal"
    
    async def reformulate_question(self, state):
        logger.info("🛠️ Reformulating the question for better results.")
        better_question = await self.nlp_service.question_re_writer(query=state["question"])
        return {"question": better_question[0]}