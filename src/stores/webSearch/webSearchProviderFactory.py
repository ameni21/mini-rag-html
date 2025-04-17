# webSearchProviderFactory.py
from stores.webSearch.provider import TavilyProvider
from .webSearchEnum import WebSearchProviderEnum

# from .SerpAPIProvider import SerpAPIProvider

class WebSearchProviderFactory:

    def __init__(self, config):
        self.config =  config


    def create(self, provider:str ):

        if provider == WebSearchProviderEnum.TAVILY.value:
            return TavilyProvider(
                api_key = self.config.TAVILY_API_KEY,
                base_url = self.config.TAVILY_API_URL
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
