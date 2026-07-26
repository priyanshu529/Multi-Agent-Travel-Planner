"""Single place to configure/instantiate the LLM used across all agents."""

from langchain_google_genai import ChatGoogleGenerativeAI
GEMINI_API_KEY=ST.SECRETS["GEMINI_API_KEY"]


llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    
)
