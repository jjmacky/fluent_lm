from abc import ABC, abstractmethod

class AbstractModelCaller(ABC):
    @abstractmethod
    def call_model(cls, model_name, prompt, client, **kwargs):
        pass