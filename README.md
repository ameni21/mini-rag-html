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
