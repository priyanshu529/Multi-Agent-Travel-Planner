import streamlit as st
from langchain_litellm import ChatLiteLLM

gemini_key = st.secrets["GEMINI_API_KEY"].strip()

primary = ChatLiteLLM(
    model="gemini/gemini-2.5-flash-lite",
    api_key=gemini_key,
)

fallback = ChatLiteLLM(
    model="groq/openai/gpt-oss-120b",
    api_key=st.secrets["GROQ_API_KEY"].strip(),
)

llm = primary.with_fallbacks([fallback])
