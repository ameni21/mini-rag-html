from ..LLMinterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
from typing import List, Union

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        return response.text
    
    async def embed_text(
        self,
        text: Union[str, List[str]],
        document_type: str = None
    ) -> Union[List[List[float]], None]:
        """
        Embed one or more texts using the Cohere API.
        Returns a list of embedding vectors (each a list of floats), or None on failure.
        """

        # 1) Sanity checks
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None

        # 2) Normalize input into a list of strings
        #    If someone passes a Pydantic model (or other), try to extract `.text`
        if isinstance(text, str):
            iterable_texts = [text]
        elif isinstance(text, list) and all(isinstance(t, str) for t in text):
            iterable_texts = text
        else:
            # fallback for GraphRequest or similar
            try:
                iterable_texts = [text.text]
            except Exception:
                self.logger.error(
                    f"embed_text expected str or List[str], got {type(text)}"
                )
                return None

        # 3) Choose the input type enum
        input_type = CoHereEnums.DOCUMENT
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnums.QUERY

        # 4) Pre-process each text chunk
        processed_texts = [self.process_text(t) for t in iterable_texts]

        # 5) Call Cohere embed endpoint
        try: 
            response = self.client.embed(
                model=self.embedding_model_id,
                texts=processed_texts,
                input_type=input_type,
                embedding_types=["float"],
            )
        except Exception as e:
            self.logger.error(f"CoHere embed API call failed: {e}")
            return None

        # 6) Validate the response structure
        if (
            not response
            or not getattr(response, "embeddings", None)
            or not getattr(response.embeddings, "float", None)
        ):
            self.logger.error("Invalid embedding response from CoHere")
            return None

        # 7) Return the raw float vectors
        return response.embeddings.float
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": prompt,
        }