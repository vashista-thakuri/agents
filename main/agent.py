from smolagents import LiteLLMModel, ToolCallingAgent, CodeAgent
from tools import multiplyer, search_web, final_answer
from typing import Any, List, Dict
import yaml

with open("main/prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

class CustomLiteLLMModel(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        return super().chat(messages, **kwargs)

model = CustomLiteLLMModel(model_id="ollama/qwen3:0.6b")

class SafeToolCallingAgent(ToolCallingAgent):
    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        return super().call_tool(name, input)
    
agent = SafeToolCallingAgent(
    model=model,
    tools=[multiplyer, search_web, final_answer],
    prompt_templates=prompt_templates
)