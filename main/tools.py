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
import pyautogui
import pygetwindow as gw
import pyperclip
import time
import os

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
    Evaluates arithmetic expressions (numbers and operators only).

    Args:
        expression (str): A valid arithmetic expression, e.g., '2 + 3 * 4'.

    Returns:
        float: The result of the evaluated expression.
    """
    # Only allow digits, decimal points, arithmetic operators, parentheses, and spaces
    cleaned = re.findall(r'[\d\.\+\-\*/\(\) ]+', expression)
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
def get_news() -> str:
    """
    Fetches the top news headlines from India Today using SerpAPI.
    This function uses SerpAPI to search Google News limited to India Today articles.
    It returns the titles and links of the top 5 headlines.
    
    Returns:
        str: A formatted string with top 5 headlines from India Today or an error message.
    """
    with open("main/config.yaml", "r") as f:
            config = yaml.safe_load(f)
    serp_api_key = config["SERPAPI_KEY"]
    params = {
        "q": "site:indiatoday.in",
        "engine": "google_news",
        "hl": "en",
        "gl": "in",
        "api_key": serp_api_key
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        data = response.json()

        news_results = data.get("news_results", [])
        if not news_results:
            return "No India Today headlines found at the moment."

        headlines = [f"{news['title']} - {news['link']}" for news in news_results[:5]]
        return "\n".join(headlines)

    except requests.exceptions.RequestException as e:
        return f"Error fetching India Today headlines: {str(e)}"
    
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
        None

    Returns:
        str: Today's date in ISO format (YYYY-MM-DD).
    """
    return date.today().isoformat()

@tool
def write_note_in_notepadpp(note: str) -> str:
    """
    Opens Notepad++, writes the given note, and saves it to the user's Desktop as note.txt.

    Args:
        note (str): The note content to write.

    Returns:
        str: Success message or error.
    """
    try:
        # Path to Notepad++ (update if installed elsewhere)
        npp_path = r"C:\Windows\notepad.exe"
        if not os.path.exists(npp_path):
            return "Notepad not found at the default location. Please update the path."
        subprocess.Popen([npp_path])
        time.sleep(2)  # Wait for Notepad++ to open
        # Focus Notepad++ window
        windows = gw.getWindowsWithTitle('Notepad')
        if not windows:
            return "Could not find Notepad window."
        windows[0].activate()
        time.sleep(0.5)
        # Use clipboard for reliability
        pyperclip.copy(note)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'v')
        # Save As (Ctrl+Shift+S)
        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(1)
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        filename = os.path.join(desktop, 'note.txt')
        pyperclip.copy(filename)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(1)
        return f"Note written and saved to {filename}"
    except Exception as e:
        return f"Error: {e}"

@tool
def run_command(command: str) -> str:
    """
    Runs a simple command line instruction and returns its output or error.

    Args:
        command (str): The command line instruction to execute.

    Returns:
        str: The output from the command or an error message.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return f"Command error: {e.stderr.strip()}"