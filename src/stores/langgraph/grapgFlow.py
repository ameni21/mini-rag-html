import logging
from services.NLPService import NLPService
from models.db_schemes.minirag.schemes.project import Project

logger = logging.getLogger("uvicorn")

class GraphFlow:
    def __init__(self, state:dict, nlp_service: NLPService ):
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
        docs =  await self.nlp_service.web_search_question(query=state["question"])
        return {"documents": docs}

    async def generate_with_context(self, state):
        logger.info("🤖 Generating answer with retrieved documents (RAG).")
        answer = await self.nlp_service.answer_rag_question(
            query=state["question"],
            retrieve_documents=state["documents"]
        )
        return {"generation": answer}

    async def generate_with_llm_only(self, state):
        logger.info("🧠 Generating answer using only LLM (no external context).")
        answer = await self.nlp_service.answer_llm_question(query=state["question"])
        return {"generation": answer}

    # Quality Control Nodes
    async def evaluate_document_relevance(self, state):
        logger.info("🧪 Evaluating document relevance to the question.")
        score = await self.nlp_service.gard_documents_retrieval(
            query=state["question"],
            retrieve_documents=state["documents"]
        )
        grade = score.binary_score
        logger.info(f"📊 Document Relevance Score: {grade}")
        return "generate" if grade == "yes" else "transform_query"

    async def validate_answer_quality(self, state):
        logger.info("🧠 Checking hallucinations and answer validity.")
        hallucination_score = await self.nlp_service.GradeHallucinations(
            retrieve_documents=state["documents"],
            generation=state["generation"]
        )
        if hallucination_score.binary_score != "yes":
            return "retry_generation"

        quality_score = self.nlp_service.gradeAnswer(
            query=self.state["question"],
            generation=self.state["generation"]
        )
        logger.info(f"🧪 Answer Quality Score: {quality_score.binary_score}")
        return "useful" if quality_score.binary_score == "yes" else "reformulate_query"

    # Decision Nodes
    async def route_question_to_source(self, state):
        logger.info("🧭 Routing question to data source...")
        route = await self.nlp_service.llm_router(state["question"])
        logger.info(f"➡️ Routed to: {route[0].datasource}")
        return route[0].datasource # one of: "web_search", "vectorstore", "internal"

    async def reformulate_question(self,state):
        logger.info("🛠️ Reformulating the question for better results.")
        better_question = await self.nlp_service.question_re_writer(query=state["question"])
        return {"question": better_question}
