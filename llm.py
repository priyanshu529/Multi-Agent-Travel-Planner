import streamlit as st
from langchain_litellm import ChatLiteLLM

primary = ChatLiteLLM(
    model="gemini/gemini-3.1-flash-lite",
    api_key=st.secrets["GEMINI_API_KEY"],
)

fallback_1 = ChatLiteLLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=st.secrets["GEMINI_API_KEY"],
)

fallback_2 = ChatLiteLLM(
    model="groq/openai/gpt-oss-120b",
    api_key=st.secrets["GROQ_API_KEY"],
)

llm = primary.with_fallbacks([fallback_1, fallback_2])
