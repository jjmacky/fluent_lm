from ...interfaces.abstract_client_factory import AbstractClientFactory

class OpenAIClientFactory(AbstractClientFactory):
    @classmethod
    def _create_client(cls, api_key):
        from openai import OpenAI
        return OpenAI(api_key=api_key)