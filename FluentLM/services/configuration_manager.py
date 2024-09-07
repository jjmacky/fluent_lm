from . import helpers
from typing import Dict, List, Any, Type, Optional
from ..logging import PipelineLogger
from pathlib import Path
from dataclasses import dataclass, field
import json
from functools import wraps

@dataclass
class MainConfig:
    providers: List[str] = None
    provider_config_file_names: Dict[str, str] = field(default_factory=dict)
    default_provider: str = None
    config_dir: str = None
    main_config_file_name: str = "main_config.json"
    main_config_path: str = None

    def __post_init__(self):
        if self.config_dir is None:
            self.config_dir: Path = Path(__file__).parent.parent.parent.resolve() / "config"
        else:
            self.config_dir = Path(self.config_dir)
        
        self.main_config_path = self.config_dir / self.main_config_file_name    

class ConfigurationManager:
    _is_initialized= False
    _logger = PipelineLogger().get_logger()
    _main_config: MainConfig = None
    provider_configs = {}

    @classmethod
    def initialize(cls):
        cls._initialize_main_config()
        cls._setup_main_config()
        cls._setup_provider_configs()
        cls._is_initialized = True
        return cls

    @classmethod
    def is_initialized(cls):
        return cls._is_initialized

    @classmethod
    def _initialize_main_config(cls):
        cls._main_config = MainConfig()

    @classmethod
    def _setup_main_config(cls):
        main_config_path = cls._main_config.main_config_path

        cls._logger.info(f"Looking for file at {main_config_path}")

        if not main_config_path.exists():
            cls._logger.error(f"Main config file not found at {main_config_path}")
            raise FileNotFoundError(f"Main config file not found at {main_config_path}")

        config_variables = helpers.load_json(main_config_path)
        cls._main_config.providers = config_variables["providers"]
        cls._main_config.provider_config_file_names = config_variables["provider_config_file_names"]
        cls._main_config.default_provider = config_variables["default_provider"]
    
    @classmethod
    def _setup_provider_configs(cls):
        for provider, file_name in cls._main_config.provider_config_file_names.items():
            provider_path = cls._main_config.config_dir / file_name

            if not provider_path.exists():
                cls._logger.error(f"Configuration file for {provider} could not be found at {provider_path}")
                raise FileNotFoundError(f"Configuration file for {provider} could not be found at {provider_path}")

            cls._logger.info(f"Loading configuration file for {provider} from {provider_path}")
            provider_config = helpers.load_json(provider_path)
            cls.provider_configs[provider] = provider_config
    
    def validate_provider(func):
        @wraps(func)
        def wrapper(cls, provider, *args, **kwargs):
            if provider not in cls._main_config.providers:
                raise KeyError(f"Invalid provider {provider}. Provider must be one of: \n {cls.print_providers}")
            return func(cls, provider, *args, **kwargs)
        return wrapper
    
    @classmethod
    def get_default_provider(cls):
        return cls._main_config.default_provider
    
    @classmethod
    def print_default_provider(cls):
        print(cls._main_config.default_provider)
    
    @classmethod
    @validate_provider
    def update_default_provider(cls, provider):
        cls._main_config.default_provider = provider

    @classmethod
    def save_main_config(cls):
        file_path = cls._main_config.main_config_path
        main_config = helpers.load_json(file_path)
        main_config["default_provider"] = cls._main_config.default_provider
        helpers.save_json(main_config, file_path)

    @classmethod
    def get_provider_configs(cls):
        return cls.provider_configs
        
    @classmethod
    def print_providers(cls):
        print('\n'.join(cls._main_config.providers))

    @classmethod
    @validate_provider
    def print_provider_config(cls, provider):
        print(json.dumps(cls.provider_configs[provider], indent=4))

    @classmethod
    @validate_provider
    def set_api_key_env_var(cls, provider, env_var):
        cls.provider_configs[provider]["api_key_env_var"] = env_var

    @classmethod
    @validate_provider
    def set_api_key(cls, provider, api_key):
        cls.provider_configs[provider]["api_key"] = api_key

    @classmethod
    @validate_provider
    def set_default_model(cls, provider, default_model):
        cls.provider_configs[provider]["default_model"] = default_model

    @classmethod
    @validate_provider
    def change_mapping(cls, provider, operation, mappings_dict, **kwargs):
        if mappings_dict is None:
            mappings_dict = kwargs

        if not mappings_dict:
            raise ValueError(f"No mappings provided to update.")
        
        valid_operations = ["edit", "add", "delete"]
        if operation.lower() not in valid_operations:
            raise ValueError(f"Operation {operation} is not recognized. Must be one of {', '.join(valid_operations)}.")
        
        match operation:
            case "edit" | "add":
                cls.provider_configs[provider]["mappings"].update(mappings_dict)
            case "delete":
                for key in mappings_dict:
                    try:
                        del cls.provider_configs[provider]["mappings"][key]
                    except KeyError:
                        raise KeyError(f"Friendly name {key} not found.")

    @classmethod
    @validate_provider
    def save_config_to_disk(cls, provider):
        file_name = cls._main_config["provider_config_file_names"][provider]
        provider_path = cls._main_config.config_dir / file_name
        config_to_write = cls.provider_configs[provider]
        helpers.save_json(config_to_write, provider_path)
