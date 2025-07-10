from typing import Any
from smolagents.tools import Tool

class PrintReasoningTool(Tool):
    name = "print_reasoning"
    description = "Prints the thought process before every every step."
    inputs = {'Thought': {'type': 'any', 'description': 'The throught process of the LLM before the step'}}
    output_type = "any"

    def forward(self, Thought: Any) -> Any:
        return Thought

    def __init__(self, *args, **kwargs):
        self.is_initialized = False
