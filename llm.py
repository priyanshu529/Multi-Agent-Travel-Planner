
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
GOOGLE_API_KEY=st.secrets["GOOGLE_API_KEY"]


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    
)
