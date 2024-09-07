from .lm_caller import LMCaller

class CallerFacade:
    @staticmethod
    def call_model(*args, **kwargs):
       caller, kwargs = LMCaller.get_caller(*args, **kwargs)
    #    print(kwargs)
       return caller.call_model(**kwargs)