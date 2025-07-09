from smolagents import LiteLLMModel, ToolCallingAgent
from tools import (
    think,
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
import inspect

# Load prompt templates
with open("main/prompts.yaml", encoding="utf-8") as f:
    prompt_templates = yaml.safe_load(f)

class JamesBond(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        return super().chat(messages, **kwargs)

class SafeRobustToolCallingAgent(ToolCallingAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_called_once = False
        self.result_returned = False

    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        # Prevent any tool call if result already returned
        if self.result_returned:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        if self.tool_called_once:
            self.result_returned = True
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        self.tool_called_once = True
        return super().call_tool(name, input)

    def parse_tool_call(self, tool_call):
        if isinstance(tool_call, dict):
            # Simple string final response
            if set(tool_call.keys()) >= {"response"} and "name" not in tool_call:
                return {
                    "name": "final_answer",
                    "arguments": {"response": tool_call["response"]}
                }

            # Single-key shorthand form: {"tool_name": ...}
            if "name" not in tool_call and len(tool_call) == 1:
                only_key = next(iter(tool_call))
                if only_key in self.tool_map:
                    val = tool_call[only_key]
                    tool_fn = self.tool_map[only_key]
                    sig = inspect.signature(tool_fn)
                    if len(sig.parameters) == 0:
                        return {"name": only_key, "arguments": {}}
                    else:
                        return {
                            "name": only_key,
                            "arguments": {"response": str(val)} if isinstance(val, str) else (val or {})
                        }

            # Handle OpenAI-style: {"function_name": "foo"} → {"name": "foo"}
            if "function_name" in tool_call and "name" not in tool_call:
                tool_call["name"] = tool_call.pop("function_name")

        name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})

        if name in self.tool_map:
            tool_fn = self.tool_map[name]
            sig = inspect.signature(tool_fn)

            if hasattr(tool_fn, "args_schema"):
                allowed_keys = list(tool_fn.args_schema.__fields__.keys())
                arguments = {k: v for k, v in arguments.items() if k in allowed_keys}
                if not allowed_keys:
                    arguments = {}
            elif len(sig.parameters) == 0:
                arguments = {}
            else:
                allowed_keys = list(sig.parameters.keys())
                arguments = {k: v for k, v in arguments.items() if k in allowed_keys}

        return {"name": name, "arguments": arguments}

    def handle_tool_call(self, tool_call, *args, **kwargs):
        # Prevent any further tool handling if result already returned
        if self.result_returned:
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        self.tool_called_once = True
        result = super().handle_tool_call(tool_call, *args, **kwargs)

        # If final_answer is returned, set result_returned and block further steps
        if isinstance(result, dict) and result.get("name") == "final_answer":
            self.result_returned = True
            response = result.get("arguments", {}).get("response", "")
            if any(e in response.lower() for e in ["error", "aborting", "does not exist"]):
                return {
                    "name": "final_answer",
                    "arguments": {
                        "response": "I don't know the answer."
                    }
                }
            if not isinstance(result.get("arguments"), dict) or "response" not in result["arguments"]:
                return {
                    "name": "final_answer",
                    "arguments": {
                        "response": str(result)
                    }
                }
            return result

        # Otherwise, wrap any result as final and block further steps
        self.result_returned = True
        return {
            "name": "final_answer",
            "arguments": {
                "response": str(result) if result is not None else ""
            }
        }
    
# Model
model = JamesBond(
    model_id="ollama/gemma3:1b",
    temperature=0.7,
    max_tokens=1024,
)

# Tools
tools = [
    think,
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
agent = SafeRobustToolCallingAgent(
    model=model,
    tools=tools,
    prompt_templates=prompt_templates,
)