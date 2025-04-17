from abc import ABC, abstractmethod

class WebSearchInterface(ABC):
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> list:
        """
        Execute a search using the provider.

        Args:
            query (str): The search query.

        Returns:
            list: A list of results (dicts or strings depending on provider).
        """
        pass
