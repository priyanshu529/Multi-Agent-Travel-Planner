
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
GEMINI_API_KEY=st.secrets["GEMINI_API_KEY"]


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    
)
