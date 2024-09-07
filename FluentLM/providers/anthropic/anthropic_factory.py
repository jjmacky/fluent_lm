from ...interfaces.abstract_client_factory import AbstractClientFactory

class AnthropicClientFactory(AbstractClientFactory):
    @classmethod
    def _create_client(cls, api_key):
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)