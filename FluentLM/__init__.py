from .services.caller_facade import CallerFacade
from .orchestrator import Orchestrator

orchestrator = Orchestrator()
ConfigurationManager = orchestrator.get_config_manager()

# Expose the call_model function directly
call_model = CallerFacade.call_model

from .pipeline import PipelineBuilder