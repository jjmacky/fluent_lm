import os

class APIKeyManager:
    @classmethod
    def get_api_key_from_env(cls, env_api_var):
        return os.environ.get(env_api_var)