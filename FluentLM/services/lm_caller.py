from .configuration_manager import ConfigurationManager
from .provider_manager import Provider, ProviderManager

class LMCaller:
    _provider_manager = None
    _providers = None
    _is_initialized = False

    @classmethod
    def initialize(cls, provider_manager: ProviderManager):
        cls._provider_manager = provider_manager
        cls._providers = cls._provider_manager.get_providers()
        cls._is_initialized = True
        return cls

    @classmethod
    def get_caller(cls, *args, **kwargs):
        return cls.intelligent_parser(args, kwargs)
    
    @classmethod
    def is_initialized(cls):
        return cls._is_initialized

    @classmethod
    def intelligent_parser(cls, args, kwargs):
        current_provider = cls._provider_manager.get_default_provider()

        provider_name = None
        client_name = None
        model_name = None
        prompt = "Hello, my friend"

        for arg in args:
            if any(arg == provider.name for provider in cls._providers):
                provider_name = arg
            elif any(arg in provider.mappings for provider in cls._providers):
                model_name = arg
            elif any(arg in provider.clients for provider in cls._providers):
                client_name = arg
            else:
                prompt = arg

        for provider in cls._providers:
            if (provider_name == provider.name) or (model_name in provider.mappings) or (client_name in provider.clients):
                current_provider = provider

        if not current_provider:
            raise ValueError("Could not determine provider.")

        parsed_args = {
            "provider_name": current_provider.name,
            "model_name": current_provider.mappings[model_name] if model_name else current_provider.default_model,
            "client": current_provider.clients[client_name] if client_name else current_provider.default_client,
            "prompt": prompt
        }

        return current_provider.model_caller, {**parsed_args, **parsed_args}


