from ..providers.anthropic.anthropic_factory import AnthropicClientFactory
from ..providers.anthropic.anthropic_caller import AnthropicCaller
from ..providers.openai.openai_factory import OpenAIClientFactory
from ..providers.openai.openai_caller import OpenAICaller
from ..interfaces.abstract_client_factory import AbstractClientFactory
from ..interfaces.abstract_model_caller import AbstractModelCaller
from .configuration_manager import ConfigurationManager
from anthropic import Anthropic
from openai import OpenAI
from typing import Dict, List, Any, Type, Optional, Union
from dataclasses import dataclass, field
import os

@dataclass
class Provider:
    name: str = None
    api_key_env_var: str = None
    mappings: Dict[str, str] = field(default_factory=dict)
    default_model: str = None
    clients: Dict[str, Union[OpenAI, Anthropic, Any]] = field(default_factory=dict)
    client_factory: Type[AbstractClientFactory] = None
    default_client: Union[OpenAI, Anthropic, Any] = None
    model_caller: Type[AbstractModelCaller] = None

class ProviderManager:
    _provider_client_factories = {
        "anthropic": AnthropicClientFactory,
        "openai": OpenAIClientFactory
    }
    _provider_model_callers = {
        "anthropic": AnthropicCaller,
        "openai": OpenAICaller
    }
    _is_initialized = False

    @classmethod
    def initialize(cls, config_manager: ConfigurationManager):
        cls._configuration_manager = config_manager
        cls.providers = []
        cls.provider_configs = config_manager.get_provider_configs()
        cls.generate_providers()
        cls._is_initialized = True
        return cls

    @classmethod
    def is_initialized(cls):
        return cls._is_initialized  

    @classmethod
    def generate_providers(cls):
        for provider_config in cls.provider_configs.values():
            provider = Provider()

            provider.name = provider_config["name"]
            provider.api_key_env_var = provider_config["api_key_env_var"]
            provider.default_model = provider_config["default_model"]
            provider.mappings = provider_config["mappings"]

            provider.client_factory = cls._provider_client_factories[provider.name]
            provider.model_caller = cls._provider_model_callers[provider.name]

            api_key = os.environ.get(provider.api_key_env_var)
            default_client = provider.client_factory._create_client(api_key)
            default_client_name = f"{provider.name}_client"
            provider.clients[default_client_name] = default_client
            provider.default_client = default_client

            cls.providers.append(provider)
    
    @classmethod
    def get_default_provider(cls):
        default_provider_name = cls._configuration_manager.get_default_provider()
        return cls.get_provider_by_name(default_provider_name)
    
    @classmethod
    def get_providers(cls):
        return cls.providers

    @classmethod
    def get_provider_by_name(cls, provider_name: str):
        for provider in cls.providers:
            if provider.name == provider_name:
                return provider