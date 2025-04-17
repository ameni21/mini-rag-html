from stores.webSearch.webSearchInterface import WebSearchInterface
from tavily import AsyncTavilyClient


class TavilyProvider(WebSearchInterface):
    def __init__(self, api_key: str, api_url:str=None):
        self.api_key = api_key
        self.base_url = api_url

    async def search(self, query: str):
        
        tavily_client = AsyncTavilyClient(api_key=self.api_key )
        response = await tavily_client.search(query)
        
        return response
