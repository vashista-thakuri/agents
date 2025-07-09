from smolagents import tool
import requests
from bs4 import BeautifulSoup
import subprocess
import math
from datetime import date
from typing import Any

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
    Evaluates a basic arithmetic expression.

    Args:
        expression (str): A valid arithmetic expression, e.g., '2 + 3 * 4'.

    Returns:
        float: The result of the evaluated expression.
    """
    try:
        return eval(expression, {"__builtins__": None}, math.__dict__)
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
def search_web(query: str) -> str:
    """
    Searches the web using SerpAPI and returns the main story snippet.

    Args:
        query (str): The search query string.

    Returns:
        str: The content snippet from the top result page.
    """
    import yaml
    try:
        with open("main/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        api_key = config["SERPAPI_KEY"]
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
        }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        url = data["organic_results"][0]["link"]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup.find("p").text if soup.find("p") else "No summary found."
    except Exception as e:
        return f"Search error: {e}"

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

    Returns:
        str: Today's date in ISO format (YYYY-MM-DD).
    """
    return date.today().isoformat()