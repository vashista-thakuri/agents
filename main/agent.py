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
    write_note_in_notepadpp,
    run_command
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
    """
    A robust ToolCallingAgent that ensures only one tool is called per run and handles errors gracefully.
    Good to haves:
    - Logging for tool calls and errors
    - Defensive programming for tool_map
    - Consistent return types
    - Docstrings for methods
    - Fallback for unexpected tool call formats
    - Reset state on new run
    - Typing for methods
    - Callable agent interface
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_called_once: bool = False
        self.result_returned: bool = False
        # Defensive: ensure tool_map exists
        if not hasattr(self, 'tool_map'):
            self.tool_map = {}

    def reset(self) -> None:
        """Reset internal state for a new run."""
        self.tool_called_once = False
        self.result_returned = False

    def call_tool(self, name: str, input: dict[str, Any]) -> dict:
        """Call a tool by name with input, enforcing single call and error handling."""
        import logging
        logger = logging.getLogger(__name__)
        if self.result_returned:
            logger.warning(f"Tool call attempted after result returned: {name}")
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        if self.tool_called_once:
            self.result_returned = True
            logger.warning(f"Multiple tool calls attempted: {name}")
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        if name not in self.tool_map:
            logger.error(f"Attempted to call unknown tool '{name}'. Skipping.")
            return {
                "name": "final_answer",
                "arguments": {
                    "response": f"Tool '{name}' does not exist."
                }
            }
        tool_fn = self.tool_map[name]
        import inspect
        sig = inspect.signature(tool_fn)
        # Enforce empty input for no-argument tools
        if len(sig.parameters) == 0:
            input = {}  # Force empty dict for no-arg tools
        self.tool_called_once = True
        logger.info(f"Calling tool: {name} with input: {input}")
        try:
            result = super().call_tool(name, input)
        except Exception as e:
            logger.exception(f"Error calling tool '{name}': {e}")
            self.result_returned = True
            return {
                "name": "final_answer",
                "arguments": {
                    "response": f"Error calling tool '{name}': {e}"
                }
            }
        return result

    def parse_tool_call(self, tool_call: dict) -> dict:
        """Parse a tool call dict into a standard format."""
        import logging
        logger = logging.getLogger(__name__)
        if isinstance(tool_call, dict):
            # Simple string final response
            if set(tool_call.keys()) >= {"answer"} and "name" not in tool_call:
                return {
                    "name": "final_answer",
                    "arguments": {"answer": tool_call["answer"]}
                }
            # Single-key shorthand form: {"tool_name": ...}
            if "name" not in tool_call and len(tool_call) == 1:
                only_key = next(iter(tool_call))
                if only_key in self.tool_map:
                    val = tool_call[only_key]
                    tool_fn = self.tool_map[only_key]
                    import inspect
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
        # Defensive fallback for unexpected formats
        name = tool_call.get("name") if isinstance(tool_call, dict) else None
        arguments = tool_call.get("arguments", {}) if isinstance(tool_call, dict) else {}
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
                arguments = {}  # Force empty dict for no-arg tools
            else:
                allowed_keys = list(sig.parameters.keys())
                arguments = {k: v for k, v in arguments.items() if k in allowed_keys}
        else:
            logger.warning(f"parse_tool_call: Unknown tool name '{name}' in tool_call: {tool_call}")
            return {"name": "final_answer", "arguments": {"response": "Unknown tool call format."}}
        return {"name": name, "arguments": arguments}

    def handle_tool_call(self, tool_call: dict, *args, **kwargs) -> dict:
        """Handle a tool call, ensuring only one result is returned."""
        import logging
        logger = logging.getLogger(__name__)
        if self.result_returned:
            logger.warning("handle_tool_call called after result returned.")
            return {
                "name": "final_answer",
                "arguments": {
                    "response": "I don't know the answer."
                }
            }
        self.tool_called_once = True
        try:
            result = super().handle_tool_call(tool_call, *args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in handle_tool_call: {e}")
            self.result_returned = True
            return {
                "name": "final_answer",
                "arguments": {
                    "response": f"Error in handle_tool_call: {e}"
                }
            }
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

    def __call__(self, task: str, **kwargs) -> dict:
        """Allow the agent to be called directly with a task."""
        self.reset()
        # You may want to implement a run method or similar here
        # For now, just return a not implemented message
        return {"name": "final_answer", "arguments": {"response": "Direct call not implemented. Use .run() method."}}

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
    write_note_in_notepadpp,
    run_command
]

# Agent
agent = SafeRobustToolCallingAgent(
    model=model,
    tools=tools,
    prompt_templates=prompt_templates,
)