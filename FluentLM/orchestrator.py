from .services.configuration_manager import ConfigurationManager
from .services.provider_manager import ProviderManager
from .services.lm_caller import LMCaller
import time

class Orchestrator:
    def __init__(self):
        self.configuration_manager = None
        self.provider_manager = None
        self.initialize()
    
    def initialize(self):
        self.init_configuration_manager()
        self.init_provider_manager()
        self.init_lm_caller()

    def init_configuration_manager(self):
        self.configuration_manager = ConfigurationManager.initialize()
        self._wait_for_completion(self.configuration_manager.is_initialized, "ConfigurationManager")

    def init_provider_manager(self):
        if not self.configuration_manager:
            raise RuntimeError("ConfigurationManager must be initialized before ProviderManager")
        self.provider_manager = ProviderManager.initialize(self.configuration_manager)
        self._wait_for_completion(self.provider_manager.is_initialized, "ProviderManager")

    def init_lm_caller(self):
        if not self.provider_manager:
            raise RuntimeError("ProviderManager must be initialized before LMCaller.")
        self.lm_caller = LMCaller.initialize(self.provider_manager)
        self._wait_for_completion(self.lm_caller.is_initialized, "LMCaller")

    def _wait_for_completion(self, check_func, component_name, timeout=10, interval=0.1):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_func():
                return
            time.sleep(interval)
        raise TimeoutError(f"{component_name} initialization timed out.")
    
    def get_config_manager(self):
        return self.configuration_manager