from smolagents import tool
import requests
from bs4 import BeautifulSoup
import subprocess
import math
from datetime import date
from typing import Any
import yaml
from urllib.parse import urljoin, urlparse
import re

@tool
def think(thought: str) -> str:
    """
    Logs internal reasoning or plan before using any other tool.

    Args:
        thought (str): The internal reasoning or plan to be logged.

    Returns:
        str: A formatted string representing the internal thought.
    """
    return f"💭 Thought: {thought}"

@tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The product of a and b.
    """
    return a * b

@tool
def calculator(expression: str) -> float:
    """
    Evaluates arithmetic expressions with natural language support.

    Args:
        expression (str): A valid arithmetic expression, e.g., '2 + 3 * 4'.

    Returns:
        float: The result of the evaluated expression.
    """
    replacements = {
        'into': '*',
        'times': '*',
        'plus': '+',
        'minus': '-',
        'divided by': '/',
        'divide by': '/',
        'divide': '/',
        'multiplied by': '*',
        'multiplied': '*',
        'x': '*',
    }
    expr = expression.lower()
    for word, op in replacements.items():
        expr = re.sub(rf'\\b{word}\\b', op, expr)
    cleaned = re.findall(r'[\d\.\+\-\*/\(\) ]+', expr)
    safe_expr = ''.join(cleaned)
    try:
        return eval(safe_expr, {"__builtins__": None}, math.__dict__)
    except Exception as e:
        return f"Error: {e}"

@tool
def final_answer(response: Any) -> str:
    """
    Returns the final response to the user.

    Args:
        response (Any): The response content of any type.

    Returns:
        str: The same response, converted to a string.
    """
    return str(response)

@tool
def get_news(query: str) -> str:
    """
    Searches the web using SerpAPI, visits the top result page, extracts up to 5
    article links from that page, fetches their contents, and returns a summary
    of each.

    Args:
        query (str): The search query.

    Returns:
        str: Summaries of top 5 articles found within the top result page.
    """
    def extract_article_text(url: str) -> str:
        try:
            page = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(page.content, "html.parser")
            candidates = soup.find_all("article")
            if not candidates:
                candidates = soup.find_all("main")
            if not candidates:
                candidates = sorted(soup.find_all("div"), key=lambda d: len(d.find_all("p")), reverse=True)

            for block in candidates:
                paragraphs = block.find_all("p")
                if len(paragraphs) >= 3:
                    text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
                    return text[:800]
            return "No substantial content found."
        except Exception as e:
            return f"Error fetching article: {e}"

    try:
        with open("main/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        api_key = config["SERPAPI_KEY"]

        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
        }
        response = requests.get("https://serpapi.com/search", timeout=10, params=params, verify=False)
        data = response.json()
        top_url = data["organic_results"][0]["link"]

        page = requests.get(top_url, timeout=10, verify=False)
        soup = BeautifulSoup(page.content, "html.parser")

        base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(top_url))
        links = soup.find_all("a", href=True)
        article_urls = []

        for a in links:
            href = a["href"]
            if any(keyword in href.lower() for keyword in ["article", "news", "story", "202", "2024", "2025"]):
                full_url = urljoin(base_url, href)
                if full_url not in article_urls and base_url in full_url:
                    article_urls.append(full_url)
            if len(article_urls) >= 5:
                break

        summaries = []
        for idx, url in enumerate(article_urls):
            text = extract_article_text(url)
            summaries.append(f"🔹 Article {idx+1} - {url}\n{text.strip()}\n")

        return "\n".join(summaries) if summaries else "No internal articles found."

    except Exception as e:
        return f"Search error: {e}"
    
@tool
def search_web(query: str) -> str:
    """
    Performs a Google search using SerpAPI and returns a summary of the top results.

    Args:
        query (str): The search query string.

    Returns:
        list: A list containing a single string with the title and a concatenated summary of snippets from the top organic results.
    """
    with open("main/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    api_key = config["SERPAPI_KEY"]

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 3
    }
    response = requests.get(url, params=params, verify=False)
    data = response.json()
    organic_results = data.get("organic_results", [])
    if not organic_results:
        return ["No results found."]

    first = organic_results[0]
    title = first.get('title', '')
    snippet_parts = []

    if first.get('snippet'):
        snippet_parts.append(first['snippet'])

    rich_snippet = first.get('rich_snippet', {}).get('top', {}).get('snippet', '')
    if rich_snippet and rich_snippet not in snippet_parts:
        snippet_parts.append(rich_snippet)

    about = first.get('about_this_result', {}).get('sections', [])
    for section in about:
        if 'description' in section:
            snippet_parts.append(section['description'])

    i = 1
    while len(" ".join(snippet_parts)) < 500 and i < len(organic_results):
        next_snip = organic_results[i].get('snippet', '')
        if next_snip and next_snip not in snippet_parts:
            snippet_parts.append(next_snip)
        i += 1

    long_snippet = " ".join(snippet_parts).strip()
    return [f"{title}\n{long_snippet}"]

@tool
def run_python(code: str) -> str:
    """
    Executes Python code and returns the output or error.

    Args:
        code (str): A string containing Python code.

    Returns:
        str: Output or error message from code execution.
    """
    try:
        local_vars = {}
        exec(code, {"__builtins__": {}}, local_vars)
        return str(local_vars)
    except Exception as e:
        return f"Execution error: {e}"

@tool
def shell_command(command: str) -> str:
    """
    Executes a shell command and returns its output.

    Args:
        command (str): A valid shell command.

    Returns:
        str: The output from running the shell command.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Shell error: {e.stderr.strip()}"

@tool
def get_date() -> str:
    """
    Retrieves the current system date.

    Args: 
        This tool does not require any arguments.

    Returns:
        str: Today's date in ISO format (YYYY-MM-DD).
    """
    return date.today().isoformat()