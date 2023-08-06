from typing import Dict
from .runtime import PixRuntime
from .steps import PixStep


class PixPlugin:
    def init(runtime: PixRuntime):
        pass


class PixPluginContext(dict):
    steps: Dict[str, PixStep] = {}
    
    def add_step(self, step_name: str, step: PixStep):
        self.steps[step_name] = step
