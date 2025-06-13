import ollama
import requests
import yaml
import os

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
SERPAPI_KEY = config["SERPAPI_KEY"]

def web_search(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
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

def summarize_search_results(results_text):
    response = ollama.chat(
        model='qwen3:0.6b',
        messages=[
            {
                'role': 'system',
                'content': (
                    "Summarize the following web search results in 2-3 sentences. "
                    "Do not mention that these are search results, just provide a concise summary."
                )
            },
            {
                'role': 'user',
                'content': results_text
            }
        ]
    )
    return clean_response(response["message"]["content"])

def clean_response(text):
    while "<think>" in text and "</think>" in text:
        start = text.find("<think>")
        end = text.find("</think>") + len("</think>")
        text = text[:start] + text[end:]
    return text.strip()

def main():
    print("What do you want to know? Ask me anything or Type 'exit' to quit.")
    while True:
        prompt = input("\nMe: ")
        if prompt.lower() == 'exit':
            print("\nGoodbye talk to you later!")
            break

        if "search" in prompt.lower() or "look up" in prompt.lower():
            print("Searching the web...")
            search_results = web_search(prompt)
            if search_results[0] != "No results found.":
                summary = summarize_search_results("\n".join(search_results))
                print("Summary:", summary)
            else:
                print("No results found.")
            continue

        response = ollama.chat(
            model='qwen3:0.6b',
            messages=[
                {
                    'role': 'system',
                    'content': (
                        "You are an assistant named Zema from Darjeeling, India. "
                        "Do NOT mention your name or origin unless the user specifically asks 'Who are you?' or 'Where are you from?'. "
                        "For all other questions, answer directly and do not introduce yourself."
                    )
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        cleaned = clean_response(response["message"]["content"])
        print("Assistent:", cleaned)

if __name__ == "__main__":
    main()