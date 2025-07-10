from smolagents.tools import Tool
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WikipediaSearchTool(Tool):
    name = "wikipedia_search"
    description = "Searches Wikipedia and returns all readable text content from the most relevant article."
    inputs = {'query': {'type': 'string', 'description': 'The topic to search for on Wikipedia.'}}
    output_type = "string"

    def forward(self, query: str) -> str:
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }

        try:
            response = requests.get(search_url, params=search_params, verify=False)
            response.raise_for_status()
            search_results = response.json().get("query", {}).get("search", [])
            if not search_results:
                return f"No Wikipedia page found for '{query}'."
        except Exception as e:
            return f"Search failed: {str(e)}"

        title = search_results[0]["title"]
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

        try:
            page_response = requests.get(page_url, verify=False)
            page_response.raise_for_status()
        except Exception as e:
            return f"Failed to fetch article: {page_url}\n{str(e)}"

        try:
            soup = BeautifulSoup(page_response.text, "html.parser")
            paragraphs = soup.find_all('p')
            text_content = ' '.join([p.get_text() for p in paragraphs])
            trimmed_text = text_content.strip().replace('\n', ' ')[:5000]

            if not trimmed_text:
                return f"Could not extract readable content from: {page_url}"

            return trimmed_text + "..."
        except Exception as e:
            return f"Could not process the Wikipedia page content: {str(e)}"
