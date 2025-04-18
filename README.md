# Multi-Source RAG Chatbot

The objective of this project is to design and implement a Retrieval-Augmented
Generation (RAG) chatbot capable of answering user queries using three retrieval
modes:
1.​ Native LLM responses (direct from model)
2.​ Vectorstore-based RAG using ChromaDB and LangGraph
3.​ Web search-based augmentation using a search API/tool (e.g., Tavily or
Serper)
The chatbot should dynamically choose the best retrieval mode based on the
nature of the user’s query, demonstrating context awareness and retrieval strategy
switching.

## 🚀 Key Highlights

✅ **Robust PostgreSQL Integration** with seamless data migration using **Alembic** and **SQLAlchemy**  
✅ **Clean model initialization** leveraging **Pydantic** schemas for validation and consistency  
✅ **Scalable semantic search** powered by **Qdrant**, serving as a high-performance vector database  
✅ **Modular LLM Provider Interface** implemented via a factory pattern, enabling easy extensibility and clean code  
✅ **Support for both local and remote LLMs**, including OpenAI and Ollama-based models  
✅ **Custom multilingual prompt templates**, optimized for **Arabic** and **English** use cases  
✅ **MVC-based architecture** ensuring separation of concerns and maintainability  
✅ **End-to-end NLP pipeline**: `Upload ➝ Chunk ➝ Index ➝ Query ➝ Generate Answer`  
✅ **Adaptive RAG Strategy**: intelligent query routing between multiple sources based on content type and relevance.

📘 [Read more: Adaptive RAG strategy using LangGraph (Official Tutorial)](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/rag/langgraph_adaptive_rag.ipynb)  
🖼️ Adaptive RAG Routing Overview:  
![Adaptive RAG Strategy](src/assets/images/adaptative_rag_starigie.png)

Supported routes:
- 🌐 **Web Search**: for questions involving recent or external information  
- 🔄 **Self-Corrective RAG**: for refining answers based on indexed documents  
- 🧠 **LLM with internal vector data**: for deep semantic search on local embeddings  
- 🚀 **LLM with external data route**: newly added support for dynamic data sources

---

## 📦 Tech Stack

- **FastAPI** for the backend API
- **PostgreSQL + pgvector** for structured data and vector storage
- **Qdrant** as the semantic search engine
- **LangGraph** for multi-tool RAG orchestration
- **Pydantic** for model validation
- **Alembic** for database migration
- **Docker** for containerization

---

## 🧪 Evaluation with LangSmith

We use to trace RAG workflows.

🔍 [View Example Trace](https://smith.langchain.com/public/2ae5ef28-7c59-47b7-b5cd-e9f70596544f/r)




## Table of Contents
- Requirements
- Installation
- Run the FastAPI server

## (Optional) Steup your command line intrface for better readability
```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Requirements

 Python 3.10 or later

#### Install Dependencies 

```bash 
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

#### Install Python using pip3

1) install pip 

```bash 
$ sudo apt-get install python3-pip
```

2)  create a new environnement 

```bash
$ python3 -m venv .venv
```

3) Activer l’environnement virtuel 
```bash 
source .venv/bin/activate
```

## Installation


### Install the required packages

```bash 
$ pip install -r requirements.txt
```

### Setup the environment variables
```bash 
$ cp .env.example .env
```
Set your environment variables in the .env file. Like OPENAI_API_KEY value.

### Run Alembic Migration 
```bash
$ alembic upgrade head
```

### Run Docker Compose Services
```bash 
$ cd docker
$ cp .env.example .env
```
*update .env with your credentials

```bash 
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 7000
```
