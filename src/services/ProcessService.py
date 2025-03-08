from .BaseService import BaseService
from .ProjectService import ProjectService
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.enums import ProcessingEnum
from bs4 import BeautifulSoup

class ProcessService(BaseService):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectService().get_project_path(project_id=project_id)

    
    
    def extract_text_from_html(self, file_id: str):

        file_path = os.path.join(
            self.project_path,
            file_id
        )
        """
        Extracts text from an HTML file using BeautifulSoup.
        Removes script and style elements.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")

                # Remove script and style tags
                for script_or_style in soup(["script", "style"]):
                    script_or_style.extract()

                text = soup.get_text(separator="\n")
                return [{"page_content": text, "metadata": {"file_name": os.path.basename(file_path)}}]

        except Exception as e:
            print(f"Error processing HTML file {file_path}: {e}")
            return None



    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        file_content_texts = [
            rec["page_content"]
            for rec in file_content
        ]

        file_content_metadata = [
            rec["metadata"]
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )

        return chunks


    