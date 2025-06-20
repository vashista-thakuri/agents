from smolagents import LiteLLMModel, ToolCallingAgent, CodeAgent
from tools import calculator
from typing import Any, List, Dict
import yaml

with open("main/prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

class CustomLiteLLMModel(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        system_prompt = {
            "role": "system",
            "content": (
                "You are an assistant named Zema from Darjeeling. "
                "Never respond with a plain answer. "
                "Only use tools you are allowed to call — do not invent tool names. "
                "Only mention your name or origin if the user asks 'Who are you?' or 'Where are you from?'."
            )
        }
        all_messages = [system_prompt] + messages
        return super().chat(all_messages, **kwargs)

model = CustomLiteLLMModel(model_id="ollama/qwen3:0.6b")

# Create the agent
agent = ToolCallingAgent(
    model=model,
    tools=[calculator],
    prompt_templates=prompt_templates
)