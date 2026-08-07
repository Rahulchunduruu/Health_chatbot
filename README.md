# Healthcare AI Chatbot

A Streamlit-based healthcare assistant that uses Groq, LangChain tools, and external search integrations to answer general health questions.

## Key Features

- Chat interface built with `Streamlit`
- Agent workflow using `langchain-groq`, `langchain-core`, and `langgraph`
- Tool integrations for:
  - DuckDuckGo web search
  - Tavily research search
  - Google Scholar lookup
  - Current date/time
  - Location-aware weather information
- Conversation persistence via SQLite (`chatbot.db`)

## Project Structure

- `app.py` — Streamlit chat UI and session state
- `main.py` — agent graph, tool routing, and Groq LLM integration
- `config.py` — environment variable loading and validation
- `prompt.py` — HealthBot rules, scope, and response prompts
- `tools.py` — tool wrappers for search, weather, and location
- `requirements.txt` — dependency list
- `.env` — local API keys and config
- `chatbot.db` — SQLite checkpoint store created at runtime

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Create a `.env` file in the repository root with the required keys:

```env
Groq_api_key=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- `Groq_api_key` is required.
- `OPENWEATHER_API_KEY` is required for weather tools.
- `TAVILY_API_KEY` is required for Tavily searches.

## Running the App

Run the app with Streamlit directly:

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## How It Works

- `app.py` accepts user questions and tracks chat history in `st.session_state`.
- `main.py` builds a `StateGraph` with an `agent` node, optional tool loop, and a final `summarizer` node.
- `tools.py` exposes functions as LangChain tools for search, weather, and location.
- `prompt.py` defines HealthBot behavior, safety rules, and tool usage instructions.
- `chatbot.db` stores conversation checkpoints for persistence.

## Usage

- Ask health-related questions in the Streamlit chat box.
- HealthBot will use available tools when appropriate and return a concise response.
- The assistant is designed for general health guidance only, not medical diagnosis.

## Notes

- The repository does not include a FastAPI backend.
- The dependency file is named `requirements.txt`.
- Keep `.env` private to avoid exposing API keys.

## Troubleshooting

- If the app fails to start, confirm the virtual environment is active and dependencies are installed.
- Ensure `.env` contains a valid `Groq_api_key`.
- For weather or Tavily results, confirm `OPENWEATHER_API_KEY` and `TAVILY_API_KEY` are set.
- If Streamlit is missing, install it with `python -m pip install streamlit`.
