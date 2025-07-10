from smolagents.tools import Tool
import yaml
import requests

class SerpAPISearchTool(Tool):
    name = "web_search"
    description = "Performs a web search using SerpAPI (Google Search API) and returns the top search results."
    inputs = {'query': {'type': 'string', 'description': 'The search query to perform.'}}
    output_type = "string"

    def __init__(self, max_results=2, **kwargs):
        super().__init__()
        self.max_results = max_results

        with open("main/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        self.api_key = config["SERPAPI_KEY"]

    def forward(self, query: str) -> str:
        
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": self.max_results
        }

        response = requests.get("https://serpapi.com/search", params=params, verify=False)  # Disable SSL verification here
        response.raise_for_status()
        results = response.json()
        organic_results = results.get("organic_results", [])
        if not organic_results:
            raise Exception("No results found!")

        postprocessed_results = [
            f"[{item.get('title', 'No Title')}]({item.get('link', '')})\n{item.get('snippet', '')}"
            for item in organic_results[:self.max_results]
        ]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)