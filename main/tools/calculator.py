from typing import Any
from smolagents.tools import Tool
import re
import math

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates a mathematical expression given in natural language and returns the computed result. Supports basic arithmetic operations and common synonyms."
    inputs = {'expression': {'type': 'string', 'description': 'The mathematical expression to evaluate, can be in natural language.'}}
    output_type = "any"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_initialized = False

    def forward(self, expression: str) -> Any:
        replacements = {
            'into': '*',
            'times': '*',
            'plus': '+',
            'minus': '-',
            'divided by': '/',
            'divide by': '/',
            'divide': '/',
            'multiplied by': '*',
            'multiplied': '*',
            'x': '*',
        }
        expr = expression.lower()
        # Replace multi-word keys first
        for word in sorted(replacements, key=lambda x: -len(x)):
            op = replacements[word]
            expr = re.sub(rf'\b{re.escape(word)}\b', op, expr)
        # Remove any characters except numbers, operators, parentheses, and spaces
        cleaned = re.findall(r'[\d\.\+\-\*/\(\) ]+', expr)
        safe_expr = ''.join(cleaned)
        try:
            return eval(safe_expr, {"__builtins__": None}, math.__dict__)
        except Exception as e:
            return f"Error: {e}"