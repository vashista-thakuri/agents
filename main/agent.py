from smolagents import LiteLLMModel, ToolCallingAgent
from tools.final_answer import FinalAnswerTool
from tools.search_web import SerpAPISearchTool
from tools.calculator import CalculatorTool
from tools.wikipedia_search import WikipediaSearchTool
from tools.outlook_email import OutlookEmailTool
import yaml
from typing import Any, List, Dict

# Load prompt templates
with open("main/prompts.yaml", "r", encoding="utf-8") as f:
    prompt_templates = yaml.safe_load(f)

# Custom Agent that safely calls tools
class SafeToolCallingAgent(ToolCallingAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._called_tools = set()

    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        # Prevent duplicate tool calls with identical parameters
        tool_call_signature = (name, tuple(sorted(input.items())))
        if tool_call_signature in self._called_tools:
            print(f"Duplicate tool call to '{name}' with same arguments detected. Skipping.")
            return f"Duplicate tool call to '{name}' with same arguments detected. Skipping."
        self._called_tools.add(tool_call_signature)

        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        tool = self.tool_map[name]
        required_args = set(tool.inputs.keys())
        filtered_input = {k: v for k, v in input.items() if k in required_args}
        return super().call_tool(name, filtered_input)

# Base LLM Model
class JamesBond(LiteLLMModel):
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        return super().chat(messages, **kwargs)
model = JamesBond(
    model_id="ollama/gemma3:1b",
    temperature=0.7,
    max_tokens=1024,
)


# Initialising tools
final_answer = FinalAnswerTool()
search_web = SerpAPISearchTool()
calculator = CalculatorTool()
wikipedia_search = WikipediaSearchTool()
outlook_email = OutlookEmailTool()

# Agent initialization
agent = SafeToolCallingAgent(
    model=model,
    tools=[
        wikipedia_search,
        #search_web,
        final_answer,
        #calculator,
        outlook_email
    ],
    prompt_templates=prompt_templates,
)