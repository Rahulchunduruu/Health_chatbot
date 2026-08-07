import os
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    IS_STREAMLIT = hasattr(st, "secrets")
except ImportError:
    IS_STREAMLIT = False

class Config:
    Groq_api_key = os.getenv("Groq_api_key") or (st.secrets.get("Groq_api_key") if IS_STREAMLIT else None)
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or (st.secrets.get("TAVILY_API_KEY") if IS_STREAMLIT else None)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY") or (st.secrets.get("OPENWEATHER_API_KEY") if IS_STREAMLIT else None)

    if not Groq_api_key:
        raise ValueError("Groq_api_key missing. Add to .env (local) or secrets.toml (Streamlit).")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY missing. Add to .env (local) or secrets.toml (Streamlit).")
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY missing. Add to .env (local) or secrets.toml (Streamlit).")

