# main/agent.py

from smolagents import LiteLLMModel, ToolCallingAgent
from tools import multiplyer, search_web, final_answer
from typing import Any, List, Dict
import yaml

# Load prompt templates
with open("main/prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

# Custom model wrapper (optional, useful for logging)
class CustomLiteLLMModel(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        response = super().chat(messages, **kwargs)
        print("[Model Output]", response)
        return response

# ToolCallingAgent with safe dispatch and validation
class SafeToolCallingAgent(ToolCallingAgent):
    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        if not isinstance(name, str) or not isinstance(input, dict):
            print(f"[Error] Invalid tool call format. Got name={name}, input={input}")
            return "Malformed tool call: missing 'name' or 'arguments'."

        if name not in self.tool_map:
            print(f"[Warning] Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."

        print(f"[Tool Call] Calling tool '{name}' with args: {input}")
        return super().call_tool(name, input)

# Initialize model and agent
model = CustomLiteLLMModel(model_id="ollama/qwen3:0.6b")

agent = SafeToolCallingAgent(
    model=model,
    tools=[multiplyer, search_web, final_answer],
    prompt_templates=prompt_templates
)
