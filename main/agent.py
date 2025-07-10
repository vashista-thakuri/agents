from smolagents import LiteLLMModel, ToolCallingAgent
from tools.final_answer import FinalAnswerTool
from tools.search_web import SerpAPISearchTool
from tools.calculator import CalculatorTool
from tools.wikipedia_search import WikipediaSearchTool
import yaml
from typing import Any, List, Dict

# Load prompt templates
with open("main/prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

# Custom Agent that safely calls tools
class SafeToolCallingAgent(ToolCallingAgent):
    def call_tool(self, name: str, input: Dict[str, Any]) -> Any:
        if name not in self.tool_map:
            print(f"Warning: Attempted to call unknown tool '{name}'. Skipping.")
            return f"Tool '{name}' does not exist."
        return super().call_tool(name, input)

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

# Agent initialization
agent = SafeToolCallingAgent(
    model=model,
    tools=[
        wikipedia_search, 
        #search_web, 
        final_answer, 
        #calculator
        ],
    prompt_templates=prompt_templates,
)