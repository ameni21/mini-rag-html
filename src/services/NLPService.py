
from pydantic import ValidationError
from models.db_schemes import Project, DataChunk
from langchain_community.tools.tavily_search import TavilySearchResults
from models.db_schemes.minirag.schemes.datachunk import RetrievedDocument
from services.BaseService import BaseService
from stores.langgraph.scheme.garderDocuments import GradeDocuments
from stores.langgraph.scheme.gradeAnswer import GradeAnswer
from stores.langgraph.scheme.gradeHallucinations import GradeHallucinations
from stores.langgraph.scheme.routerQuery import RouteQuery
from stores.llm.LLMEnums import DocumentTypeEnum
from helpers.config import get_settings
from langsmith import traceable
from typing import List
import logging
import json
import os

logger = logging.getLogger('uvicorn.error')

class NLPService(BaseService):

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    
    def normalize_routing_output(self, raw: str):
        self.raw = raw.strip().lower()
        if "vector" in raw:
            return "vectorstore"
        elif "web" in raw :
            return "web_search"
        elif "internal" in raw:
            return "internal"
        
    def binary_score(self, raw: str):
        self.raw = raw.strip().lower()
        if "yes" in raw:
            return "yes"
        else:
            return "no"
        
    def _get_doc_content(self, doc):
        """Safely extract content from a document regardless of its type"""
        if hasattr(doc, 'text'):
            return doc.text
        elif isinstance(doc, dict) and 'content' in doc:
            return doc['content']
        elif isinstance(doc, (str, int, float, bool)):
            return str(doc)
        else:
            # Handle other types, including slice
            logger.warning(f"Unexpected document type: {type(doc)}, converting to string")
            return str(doc)
        

    def create_collection_name(self, project_id: str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )
    
    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = self.embedding_client.embed_text(text=texts, 
                                                  document_type=DocumentTypeEnum.DOCUMENT.value)

        # step3: create collection if not exists
        _ = await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True
    
    @traceable(run_type="retriever")
    async def search_vector_db_collection(self, project_id: int, text: str, limit: int = 5):
        # Step 1: Get collection name
        collection_name = self.create_collection_name(project_id=project_id)

        # Step 2: Get text embedding vector
        vectors = await self.embedding_client.embed_text(
            text=text, 
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vectors:
            return []

        query_vector = vectors[0] if isinstance(vectors, list) and vectors else None
        if not query_vector:
            return []

        # Step 3: Perform semantic search
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        if not results:
            return []

        # Step 4: Serialize results (convert to dict)
        serialized = []
        for doc in results:
            serialized.append({
                'content': getattr(doc, 'text', None),
                'score': getattr(doc, 'score', None)
            })

        return serialized

    @traceable(run_type="llm")
    async def answer_rag_question(self,  query: str, retrieve_documents:List ):
        
        answer, full_prompt, chat_history = None, None, None


        if not retrieve_documents or len(retrieve_documents)==0:
            return answer, full_prompt, chat_history 
        
        # step 2: construct LLM prompt
        system_prompt = self.template_parser.get("rag","system_prompt")
   
        documents_prompts = "\n".join([
            self.template_parser.get("rag","documents_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(
                        self._get_doc_content(doc)
                ),
            })
            for idx, doc in enumerate(retrieve_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt",{"query": query})

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
    
            )
        ]

        full_prompt =  "\n\n".join([documents_prompts,footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history
    
    @traceable(run_type="llm")
    async def answer_llm_question(self,  query: str):
        
        answer, full_prompt, chat_history = None, None, None

                
        # step1: Construct LLM prompt
        system_prompt = self.template_parser.get("llm", "system_prompt")

        footer_prompt = self.template_parser.get("llm", "footer_prompt", {
            "query": query
        })

        # step2: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ footer_prompt])

        # step3: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history
        
    @traceable(run_type="tool")
    async def web_search_question(self, query: str):
        settings = get_settings()
        os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY
        
        
        # step 1: retrieve related documents
        web_search_tool = TavilySearchResults(k=3, tavily_api_key=os.environ["TAVILY_API_KEY"])

        # step 2 : Make sure the query is a string
        if isinstance(query, dict) and "text" in query:
            query = query["text"]
        elif not isinstance(query, str):
            query = str(query)

        # step 3: Call the tool with the properly formatted query
        results_list = web_search_tool.invoke({"query": query})

        if not results_list or len(results_list) == 0:
            return False
        
        return results_list
    
    

    
    @traceable(run_type="chain")
    async def llm_router(self, query: str):
        
        answer, full_prompt, chat_history = None, None, None

                
        # step 1: Load prompt components
        system_prompt = self.template_parser.get("routing","system_prompt")
        footer_prompt = self.template_parser.get("routing", "footer_prompt",{"query": query})

         # Step 2: Build chat history 
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                
            )
        ]

        full_prompt =  "\n\n".join([footer_prompt])

        # Step 2: Call generation provider generate_text function
        raw_answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        # Step 4: Parse the result into the RouteQuery model
        try:
            cleaned_answer = self.normalize_routing_output(raw_answer)
            answer = RouteQuery(datasource=cleaned_answer)
        except ValidationError as ve:
            logger.error(f"Failed to parse LLM response into RouteQuery: {ve}")
            answer = None

        return answer, full_prompt, chat_history
    
    @traceable(run_type="parser")
    async def GradeHallucinations(self, retrieve_documents:List,  generation : str):
        
        answer, full_prompt, chat_history = None, None, None
        

        if not retrieve_documents or len(retrieve_documents)==0:
            return answer, full_prompt, chat_history 

        
        # step 2: Load prompt components
        system_prompt = self.template_parser.get("grounding","system_prompt")

        document_prompts = "\n".join([
            self.template_parser.get("grounding", "documents_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text if hasattr(doc, 'text') else doc,
                }) 
            for idx, doc in enumerate(retrieve_documents)

        ])

        generation_prompt = self.template_parser.get("grounding", "generation_prompt", {"generation": generation} )

        footer_prompt = self.template_parser.get("grounding", "footer_prompt")

         # Step 3: Build chat history 
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                #self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt =  "\n\n".join([document_prompts, generation_prompt, footer_prompt])

        # Step 4: Call generation provider generate_text function

        raw_answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        # Step 5: Parse the result into the GradeHallucinations model
        try:
            cleaned_answer = self.binary_score(raw_answer)
            answer = GradeHallucinations(binary_score=cleaned_answer)
        except ValidationError as ve:
            logger.error(f"Failed to parse LLM response into GradeHallucinations: {ve}")
            answer = None

        return answer, full_prompt, chat_history
    
    @traceable(run_type="retriever")
    async def gard_documents_retrieval(self, query:str, retrieve_documents:List):
        
        answer, full_prompt, chat_history = None, None, None

    

        if not retrieve_documents or len(retrieve_documents)==0:
            return answer, full_prompt, chat_history 

        
        # step 2: Load prompt components
        system_prompt = self.template_parser.get("garding","system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("garding", "documents_prompt", {
                "doc_num": idx + 1,
                "chunk_text": self.generation_client.process_text(
                    str(doc.get('content', '')) if isinstance(doc, dict)
                    else str(getattr(doc, 'text', doc))
                )
            })
            for idx, doc in enumerate(retrieve_documents)
        ])

        footer_prompt = self.template_parser.get("garding", "footer_prompt", {"query":query})

         # Step 3: Build chat history 
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                
            )
        ]

        full_prompt =  "\n\n".join([documents_prompts, footer_prompt])

        # Step 4: Call generation provider generate_text function

        raw_answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        # Step 5: Parse the result into the GradeDocuments model
        try:
            cleaned_answer = self.binary_score(raw_answer)
            answer = GradeDocuments(binary_score=cleaned_answer)
        except ValidationError as ve:
            logger.error(f"Failed to parse LLM response into GradeDocuments: {ve}")
            answer = None

        return answer, full_prompt, chat_history
    
    @traceable(run_type="parser")
    async def gradeAnswer(self, query:str,  generation : str):
        
        answer, full_prompt, chat_history = None, None, None
        
        # step 1: Load prompt components
        system_prompt = self.template_parser.get("resolution","system_prompt")

        generation_prompt = self.template_parser.get("resolution", "generation_prompt", {"generation": generation} )

        footer_prompt = self.template_parser.get("resolution", "footer_prompt", {"query":query})

         # Step 2: Build chat history 
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                #self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt =  "\n\n".join([ generation_prompt, footer_prompt])

        # Step 3: Call generation provider generate_text function

        raw_answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        # Step 4: Parse the result into the GradeAnswer model
        try:
            cleaned_answer = self.binary_score(raw_answer)
            answer = GradeAnswer(binary_score=cleaned_answer)
        except ValidationError as ve:
            logger.error(f"Failed to parse LLM response into GradeAnswer: {ve}")
            answer = None

        return answer, full_prompt, chat_history
    
    @traceable(run_type="prompt")
    async def question_re_writer(self,  query: str ):
        
        answer, full_prompt, chat_history = None, None, None
        
        #  construct LLM prompt
        system_prompt = self.template_parser.get("rewriter","system_prompt")
   
        
        footer_prompt = self.template_parser.get("rewriter", "footer_prompt",{"query": query})

        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role="system"
                #self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt =  "\n\n".join([footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history