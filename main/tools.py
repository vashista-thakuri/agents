from smolagents import tool
import os
import requests
import yaml
from bs4 import BeautifulSoup
import re

@tool
def final_answer(answer: str) -> str:
    """
    Finalizes the agent's response.

    Args:
        answer (str): A string containing the final answer.

    Returns:
        str: The finalized answer string.

    """
    return answer

@tool
def multiplyer(a: int, b: int) -> int:
    """
    Multiply two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The product of a and b.
    """
    return a * b

@tool
def search_web(query: str) -> str:
    """
    Performs a Google search using SerpAPI and returns 
    the main headline story from the top link.

    Args:
        query (str): The search query string.

    Returns:
        str: The article’s main headline story, including
             the title and key points from the first few sentences of the article body.
    """
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    SERPAPI_KEY = config["SERPAPI_KEY"]

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google"
    }

    try:
        res = requests.get(url, params=params, timeout=10, verify=False)
        results = res.json()

        first_result = results.get("organic_results", [])[0]
        link_url = first_result.get("link")

        if not link_url:
            return "No valid link found in search results."

        page = requests.get(link_url, timeout=5, verify=False)
        soup = BeautifulSoup(page.text, 'html.parser')

        headline_tag = soup.find('h1')
        headline = headline_tag.get_text(strip=True) if headline_tag else "No headline found"

        paragraphs = soup.find_all('p')
        article_text = " ".join(p.get_text() for p in paragraphs if p.get_text())
        article_text = re.sub(r'\s+', ' ', article_text).strip()

        sentences = re.split(r'(?<=[.!?]) +', article_text)
        summary = " ".join(sentences[:5])

        return summary

    except Exception as e:
        return f"Search or scraping failed: {str(e)}"