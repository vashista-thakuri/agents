# AI AGENTS


This is a command-line AI assistant that can answer your questions, perform web searches, and summarize results using large language models. When you ask a question, the assistant responds directly. If your question includes phrases like "search" or "look up," it fetches the latest information from the web using the SerpAPI and summarizes the findings for you. The assistant is designed to be concise and helpful, only revealing its name or origin if specifically asked.

To use the application, simply run it in your terminal, type your question, and receive an answer or a summarized web search result.

## Sample Output

Below is an example of the application's output, so you know what kind of answers to expect:

```
What do you want to know? Ask me anything or Type 'exit' to quit.

Me: look up the weather in hyderabad india tomorrow           
Searching the web...
Summary: The Hyderabad weather forecast shows a steady 81° to 86°F with rain early, followed by a mix of cloudy conditions with thunderstorms developing for the afternoon. High temperatures range between 86°F and 78°F, while there's 90% chance of rain and 88% precipitation. Wind conditions remain moderate with winds from the northwest and gusts of 23 mph.

Me: exit

Goodbye talk to you later!
```

## How to run the code

- **Note:** For security reasons, the `SERPAPI_KEY` is not included in the repository. You must create a file named `config.yaml` inside the `src` folder and add your API key in the following format:


Open your terminal and run the following commands:

```
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python src/app.py
```

To remove the virtual environment after use:

```
Remove-Item -Recurse -Force .\venv
```