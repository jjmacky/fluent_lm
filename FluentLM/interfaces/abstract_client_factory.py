from abc import ABC, abstractmethod

class AbstractClientFactory(ABC):

    @classmethod
    @abstractmethod
    def _create_client(cls, api_key):
        pass