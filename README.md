# AI AGENTS


This is a tool-driven command‑line AI assistant that can answer your questions, perform real‑time web searches when needed, and deliver concise summaries—all powered by large language models. The assistant automatically decides when fresh information is required and fetches it via SerpAPI before replying.

To use the application, simply run it in your terminal, type your question, and receive an answer or a summarized web search result.

## Sample Output

Below is an example of the application's output, so you know what kind of answers to expect:

**👋 Agent:**  
**"What do you want to know? Ask me anything or type 'exit' to quit."**


**👤 Me:**  
**"What big announcements in tech were made yesterday in India?"**

> ```
> Internal Working:
>
> Step 1: Tool Invocation
> Called tool: `search_web`  
> Query: "big announcements in tech from India yesterday"
> 
> Step 2: Planning & Observations
> The assistant processes the results, interprets key updates, and prepares the final answer.
> 
> Step 3: Final Answer
> ```

**👋 Agent:**  
**Big announcements in tech from India yesterday include:  
MakeMyTrip raised $3.1 billion in the largest fundraise by a listed Indian internet company.  
The funds were raised through 14 transactions during the week, compared to 36 in the same period last year.  
As a result, Trip.com’s stake in MakeMyTrip dropped to 19.99% from 45.34%, reducing its board presence from five directors to two.  
This follows allegations that MakeMyTrip compromised Indian army travel data due to its Chinese ownership.**

**👤 Me:**  
**exit**

**👋 Agent:**  
**Goodbye! Talk to you later!**

## How to run the code

- **Note:** For security reasons, the `SERPAPI_KEY` is not included in the repository. You must create a file named `config.yaml` inside the `main` folder and add your API key in the following format:


**Note:** Make sure Ollama is installed in you system and pull the "**qwen3:0.6b**" model.

Open your terminal and run the following commands:

Powershell:
```
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main/app.py
```

Terminal:
```
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main/app.py
```

To remove the virtual environment after use:

```
Remove-Item -Recurse -Force .\venv
```