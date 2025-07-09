from smolagents import LiteLLMModel, ToolCallingAgent
from tools import (
    multiply,
    search_web,
    get_news,
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

class JamesBond(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        return super().chat(messages, **kwargs)

class SafeToolCallingAgent(ToolCallingAgent):
    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        return super().call_tool(name, input)

# Function to handle tool calls with a specific format
class PatchedSafeToolCallingAgent(SafeToolCallingAgent):
    def parse_tool_call(self, tool_call):
        if (
            isinstance(tool_call, dict)
            and set(tool_call.keys()) >= {"response"}
            and "name" not in tool_call
        ):
            return {
                "name": "final_answer",
                "arguments": {"response": tool_call["response"]}
            }

        if "name" not in tool_call:
            if len(tool_call) == 1:
                only_key = next(iter(tool_call))
                if only_key in self.tool_map:
                    val = tool_call[only_key]
                    tool_fn = self.tool_map[only_key]
                    import inspect
                    sig = inspect.signature(tool_fn)
                    if len(sig.parameters) == 0:
                        return {
                            "name": only_key,
                            "arguments": {}
                        }
                    else:
                        return {
                            "name": only_key,
                            "arguments": {"response": str(val)} if isinstance(val, str) else (val or {})
                        }

        if "function_name" in tool_call and "name" not in tool_call:
            tool_call["name"] = tool_call.pop("function_name")

        name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        if name in self.tool_map:
            tool_fn = self.tool_map[name]
            import inspect
            sig = inspect.signature(tool_fn)
            if hasattr(tool_fn, "args_schema"):
                allowed_keys = list(tool_fn.args_schema.__fields__.keys())
                arguments = {k: v for k, v in arguments.items() if k in allowed_keys}
                if not allowed_keys:
                    arguments = {}
            elif len(sig.parameters) == 0:
                # Force arguments to be empty for tools with no parameters
                arguments = {}
            else:
                # Remove any arguments not in the function signature
                allowed_keys = list(sig.parameters.keys())
                arguments = {k: v for k, v in arguments.items() if k in allowed_keys}

        return {
            "name": name,
            "arguments": arguments
        }

# Avoiding Infinite Loop on Tool Calls
class LoopGuardSafeToolCallingAgent(PatchedSafeToolCallingAgent):
    MAX_TOOL_CALLS = 2
    MAX_STEPS = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_call_counts = {}
        self.step_counter = 0
        self.tool_called_and_answered = set()
        self.first_tool_call_successful = False
        self.first_tool_call_result = None
        self.error_count = 0  # Track consecutive errors
        self.last_error_tool = None

    def handle_tool_call(self, tool_call, *args, **kwargs):
        name = tool_call.get("name")
        # If already called and answered, do not repeat
        if name in self.tool_called_and_answered:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": f"Tool `{name}` was already called and returned an answer. Finalizing to prevent duplicate calls."
                }
            }
        self.tool_call_counts[name] = self.tool_call_counts.get(name, 0) + 1
        if self.tool_call_counts[name] > self.MAX_TOOL_CALLS:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        result = super().handle_tool_call(tool_call, *args, **kwargs)
        # Error handling: if result is an error, increment error_count
        if isinstance(result, dict) and result.get("name") == "final_answer":
            resp = result.get("arguments", {}).get("response", "")
            if "error" in resp.lower() or "does not exist" in resp.lower() or "aborting" in resp.lower():
                if self.last_error_tool == name:
                    self.error_count += 1
                else:
                    self.error_count = 1
                    self.last_error_tool = name
                if self.error_count > 2:
                    return {
                        "name": "final_answer",
                        "arguments": {
                            "response": "I don't know the answer."
                        }
                    }
            else:
                self.error_count = 0
                self.last_error_tool = None
        else:
            self.error_count = 0
            self.last_error_tool = None
        if name != "final_answer":
            self.tool_called_and_answered.add(name)
        # If first tool call succeeded, store result
        if self.step_counter == 1 and name != "final_answer":
            if not (isinstance(result, dict) and result.get("name") == "final_answer" and "error" in result.get("arguments", {}).get("response", "").lower()):
                self.first_tool_call_successful = True
                self.first_tool_call_result = result
        return result

    def step(self, *args, **kwargs):
        self.step_counter += 1
        if self.step_counter > self.MAX_STEPS:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        # If the first tool call was successful, just return its result
        if self.step_counter == 2 and self.first_tool_call_successful:
            return self.first_tool_call_result
        if self.error_count > 2:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        return super().step(*args, **kwargs)

# Model
model = JamesBond(
    model_id="ollama/gemma3:1b",
    temperature=0.7,
    max_tokens=1024,
)

# Tools
tools = [
    multiply,
    search_web,
    get_news,
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