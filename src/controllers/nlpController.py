from fastapi import FastAPI, APIRouter, status, Request
from fastapi.responses import JSONResponse
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.enums import ResponseSignal
import logging
from controllers.scheme.nlp import PushRequest, SearchRequest
from services.NLPService import NLPService
from tqdm.auto import tqdm





logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags={"api_v1", "nlp"},
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id:int, project_name:str, push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
    )

    chunk_model = await ChunkModel.create_instance(
        db_client = request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        project_name= project_name

    )



    if not project:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }

        )
    
    nlp_service = NLPService(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    # create collection if not exists
    collection_name = nlp_service.create_collection_name(project_id=project.project_id)

    _ = await request.app.vectordb_client.create_collection(
        collection_name=collection_name,
        embedding_size=request.app.embedding_client.embedding_size,
        do_reset=push_request.do_rest,
    )

    # setup batching
    total_chunks_count = await chunk_model.get_total_chunks_count(project_id=project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Vector Indexing", position=0)

    while has_records:
        page_chunks = await chunk_model.get_poject_chunks(project_id=project.project_id, page_no=page_no)
        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)

        is_inserted = await nlp_service.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunks_ids=chunks_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTOR_ERROR.value
                }
            )
        
        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={
            "signal" : ResponseSignal.INSERT_INTO_VECTOR_SUCCESS.value,
            "inserted_item_count" : inserted_items_count
        }  
    )



@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int, project_name:str):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
    )


    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        project_name=project_name
    )

    nlp_service = NLPService(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_info = await nlp_service.get_vector_db_collection_info(project=project)

    print(collection_info)

    return JSONResponse(
        content={
            "signal" : ResponseSignal.VECTORDB_COLLECTION_RETRIVED.value,
            "inserted_item_count" : collection_info
        }  
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, project_name:str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
    )


    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        project_name=project_name
    )

    nlp_service = NLPService(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )


    results = await nlp_service.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        content={
            "signal" : ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results" : [result.dict() for result in results ]
        }  
    )


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, project_name:str, search_request: SearchRequest):

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
    )


    project = await project_model.get_project_or_create_one(
        project_id=project_id,
        project_name= project_name
    )

    nlp_service = NLPService(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    answer, full_prompt, chat_history = await  nlp_service.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )
    
    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value
            }
        )
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
                "answer": answer,
                "full_prompt": full_prompt,
                "chat_history": chat_history
            }
        )
        

@nlp_router.post("/index/answer_llm")
async def answer_llm(request: Request,  search_request: SearchRequest):

    
    nlp_service = NLPService(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    answer, full_prompt, chat_history = await  nlp_service.answer_llm_question(
        query=search_request.text,
        limit=search_request.limit,
    )
    
    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value
            }
        )
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
                "answer": answer,
                "full_prompt": full_prompt,
                "chat_history": chat_history
            }
        )

