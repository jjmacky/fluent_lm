from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional, Iterable
from .services.caller_facade import CallerFacade
from .services import helpers
import networkx as nx
import re

class Context:
    def __init__(self, initial_context: str | None = None):
        self.context = initial_context or {}

    def print(self):
        print(self.context)

    def add(self, key: str, value: Any):
        self.context[key] = value
    
    def get(self, key: str):
        return self.context.get(key)

    def remove(self, key: str):
        del self.context[key]

    def clear(self):
        self.context.clear()

    def update(self, key: str, new_value: Any):
        if key in self.context:
            self.context[key] = new_value
        else:
            raise KeyError(f"Key {key} not in context.")

class Step(ABC):
    def __init__(self, input_key: str | None = None, output_key: str | None = None):
        self.input_key = input_key
        self.output_key = output_key

    def get_input_key(self):
        self.input_key = self.input_key or helpers.generate_random_string()
        return self.input_key
    
    def get_output_key(self):
        self.output_key = self.output_key or helpers.generate_random_string()
        return self.output_key

    @abstractmethod
    def execute(self, current_data: Dict[str, Any]) -> Any:
        pass

class PromptStep(Step):
    def __init__(self, template: str, variables: Dict[str, Any] | None = None, input_key: str | None = None, output_key: str | None = None):
        super().__init__(input_key, output_key)
        self.template = template

        if variables is None:
            variables = {var: None for var in self._extract_variables(template)}
        
        self.variables = variables

    def _extract_variables(self, prompt: str) -> list:
        return re.findall(r'\{(\w+)\}', prompt)    

    def execute(self, context: Context) -> str:
        combined_vars = {**self.variables, **context.context} # Combine variables and context, with context taking precedence by unpacking it second.
        formatted_prompt = self.template.format(**combined_vars)
        context.add(self.get_output_key(), formatted_prompt)
        return formatted_prompt

class ModelStep(Step):
    def __init__(self, provider: str | None = None, model_name: str | None = None, prompt: str | None = None, client: str | None = None, input_key: str | None = None, output_key: str | None = None):
        super().__init__(input_key, output_key)
        self.provider = provider
        self.model_name = model_name
        self.client = client
        self.prompt_step = PromptStep(template = prompt) if prompt else None

    def execute(self, context: Context) -> str:
        if self.prompt_step:
            input_text = self.prompt_step.execute(context)
        else:
            input_text = context.get(self.get_input_key())

        result = CallerFacade.call_model(self.provider, self.model_name, self.client, input_text)
        context.add(self.get_output_key(), result)
        return result

class ApplyStep(Step):
    def __init__(self, func: Callable[[Any], Any], input_key: str | None = None, output_key: str | None = None):
        super().__init__(input_key, output_key)
        self.func = func

    def execute(self, context: Context) -> Any:
        input_value = context.get(self.get_input_key())
        result = self.func(input_value)
        context.add(self.get_output_key(), result)
        return result

class DatasetStep(Step):
    def __init__(self, dataset: Iterable[Any], input_key: str | None = None, output_key: str | None = None, target: str | None = None, target_type: str | None = None):
        super().__init__(input_key=input_key, output_key=output_key)
        self.dataset = dataset
        self.input_key = input_key
        self.output_key = output_key
        self.target = target
        self.target_type = target_type
        self._iterator = None

    def _ensure_iterator(self):
        if self._iterator is None:
            self._iterator = iter(self.dataset)

    def execute(self, context: Context):
        self._ensure_iterator()

        try:
            item = next(self._iterator)
            if self.target:
                if self.target_type == "indirect":
                    target_selection = item[self.target]
                    context.add(self.target, item[target_selection])
                elif self.target_type == "direct":
                    context.add(self.target, item[self.target])
                else:
                    raise ValueError(f"Invalid target_type of {self.target_type}. Must be one of 'indirect' or 'direct'.")
            if self.input_key:
                context.add(self.input_key, item[self.input_key])
            if self.output_key:
                context.add(self.output_key, item[self.input_key])
            return item
        except StopIteration:
            self._iterator = None
            return None

class Pipeline:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.context = None
        self.previous_step = None

    def get_previous_step(self):
        return self.previous_step
    
    def add_step(self, step: Step):
        self.graph.add_node(step)
        if self.previous_step:
            self.graph.add_edge(self.previous_step, step)
        self.previous_step = step

    def execute(self, initial_context: Optional[Dict[str, Any]] = None):
        self.context = Context(initial_context)
        results = []

        steps = list(nx.topological_sort(self.graph))
        first_step = steps[0] if steps else None

        if isinstance(first_step, DatasetStep):
            from tqdm import tqdm
            with tqdm(total = len(first_step.dataset)) as pbar:
                current_value = 0
                while True:
                    item = first_step.execute(self.context)
                    if item is None:
                        break
                    sub_result = self._execute_from(first_step)
                    if sub_result is not None:
                        results.append(sub_result)
                    self.context.clear()
                    current_value += 1
                    pbar.update(1)
                return results
        else:
            for step in steps:
                self._execute_step(step)
            if self.previous_step:
                results = self.context.get(self.previous_step.get_output_key())
            return results

    def _execute_from(self, start_step: Step):
        for step in nx.dfs_preorder_nodes(self.graph, start_step):
            if step != start_step:
                self._execute_step(step)

        if self.previous_step:
            return self.context.get(self.previous_step.get_output_key())
        
    def _execute_step(self, step: Step):
        predecessors = list(self.graph.predecessors(step))
        for pred in predecessors:
            input_data = self.context.get(pred.get_output_key())
            self.context.add(step.get_input_key(), input_data)
        step.execute(self.context)

    def print_result(self):
        previous_step = self.get_previous_step()
        print(self.context.get(previous_step.get_output_key()))
        

class PipelineBuilder:
    def __init__(self, keep_all_intermediate_steps: bool = False, progress_bar = False):
        self.pipeline = Pipeline()
        self.keep_all_intermediate_steps = keep_all_intermediate_steps
        self.progress_bar = progress_bar
    
    def _add_step(self, step: Step):
        self.pipeline.add_step(step)
        return self
    
    def using_dataset(self, dataset: List[Any], input_key: str | None = None, output_key: str | None = None, target: str | None = None, target_type: str | None = None) -> 'PipelineBuilder':
        return self._add_step(DatasetStep(dataset, input_key, output_key, target, target_type))

    def with_prompt(self, template: str, variables: Dict[str, str] | None = None, input_key: str | None = None, output_key: str | None = None) -> 'PipelineBuilder':
        return self._add_step(PromptStep(template, variables, input_key, output_key))

    def call_model(self, provider: str | None = None, model_name: str | None = None, prompt: str | None = None, client: str | None = None, input_key: str | None = None, output_key: str | None = None) -> 'PipelineBuilder':
        return self._add_step(ModelStep(provider, model_name, prompt, client, input_key, output_key))

    def apply(self, func: Callable[[Any], Any], input_key: str | None = None, output_key: str | None = None) -> 'PipelineBuilder':
        return self._add_step(ApplyStep(func, input_key, output_key))

    def build(self) -> Pipeline:
        return self.pipeline
    