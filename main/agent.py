from smolagents import LiteLLMModel, ToolCallingAgent
from tools import (
    multiply,
    search_web,
    final_answer,
    run_python,
    shell_command,
    calculator,
    get_date,
)
import yaml
from typing import Any, List, Dict

# Load prompt templates
with open("main/prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

class CustomLiteLLMModel(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        return super().chat(messages, **kwargs)

class SafeToolCallingAgent(ToolCallingAgent):
    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        return super().call_tool(name, input)

class PatchedSafeToolCallingAgent(SafeToolCallingAgent):
    def parse_tool_call(self, tool_call):
        if "name" not in tool_call:
            if len(tool_call) == 1:
                only_key = next(iter(tool_call))
                if only_key in self.tool_map:
                    val = tool_call[only_key]
                    return {
                        "name": only_key,
                        "arguments": {"response": str(val)} if isinstance(val, str) else (val or {})
                    }
                
        if "function_name" in tool_call and "name" not in tool_call:
            tool_call["name"] = tool_call.pop("function_name")

        name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        if name in self.tool_map and hasattr(self.tool_map[name], "args_schema"):
            allowed_keys = list(self.tool_map[name].args_schema.__fields__.keys())
            arguments = {k: v for k, v in arguments.items() if k in allowed_keys}

        return {
            "name": name,
            "arguments": arguments
        }

# Avoiding Infinite Loop on Tool Calls
class LoopGuardSafeToolCallingAgent(PatchedSafeToolCallingAgent):
    MAX_TOOL_CALLS = 10
    MAX_STEPS = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_call_counts = {}
        self.step_counter = 0

    def handle_tool_call(self, tool_call, *args, **kwargs):
        name = tool_call.get("name")
        self.tool_call_counts[name] = self.tool_call_counts.get(name, 0) + 1
        if self.tool_call_counts[name] > self.MAX_TOOL_CALLS:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": f"Tool `{name}` was called too many times. Aborting to prevent infinite loop."
                }
            }
        return super().handle_tool_call(tool_call, *args, **kwargs)

    def step(self, *args, **kwargs):
        self.step_counter += 1
        if self.step_counter > self.MAX_STEPS:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "Too many tool calls. Ending conversation to prevent infinite loop."
                }
            }
        return super().step(*args, **kwargs)

# Model
model = CustomLiteLLMModel(
    model_id="ollama/qwen3:0.6b",
    temperature=0.7,
    max_tokens=1024,
)

# Tools
tools = [
    multiply,
    search_web,
    final_answer,
    run_python,
    shell_command,
    calculator,
    get_date,
]

# Agent
agent = LoopGuardSafeToolCallingAgent(
    model=model,
    tools=tools,
    prompt_templates=prompt_templates,
)