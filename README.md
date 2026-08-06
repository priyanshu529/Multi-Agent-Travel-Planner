# ✈️ Multi-Agent Travel Planner

A multi-agent AI travel planning system built with **LangGraph**, **MCP (Model Context Protocol)**, and **Streamlit**. A single user query is parsed, fanned out to specialized flight, hotel, and weather agents, synthesized into a complete itinerary, and refined through a self-evaluation loop before being returned as a polished, downloadable travel plan.

Repo: [priyanshu529/Multi-Agent-Travel-Planner](https://github.com/priyanshu529/Multi-Agent-Travel-Planner)

---

## 🧭 Overview

This is a **single-purpose planning pipeline**, not a chat app — every query runs through the full LangGraph agent graph described below and comes out as one structured trip report. Users sign in with **Google (via Streamlit's native `st.login`)**, and each trip run is persisted to Postgres so past trips show up in a history sidebar and can be revisited later.

---

## 🏗️ Agent Workflow

```mermaid
flowchart LR
    A([User query]) --> B[Input Guardrail Agent]
    B --> C[Query Extraction Agent]
    C --> D[Flight Agent]
    C --> E[Hotel Agent]
    C --> F[Weather Agent]
    D --> G[Itinerary Agent]
    E --> G
    F --> G
    G --> H[Final Agent]
    H --> I[Evaluation Agent]
    I -- revise --> H
    I -- approved --> J([Travel output])
```

*(GitHub renders this Mermaid block automatically. If viewing elsewhere, here's the same flow as plain text:)*

```
User query
   → Query Extraction Agent
       → Flight Agent   ─┐
       → Hotel Agent     ─┼─→ Itinerary Agent → Final Agent ⇄ Evaluation Agent
       → Weather Agent  ─┘        (revise loop until approved)
                                              → Travel output
```

**Nodes (LangGraph `StateGraph`, see `graph.py`):**

1. **`query_agent`** (`agents/query_extract.py`) — extracts structured trip fields (origin/destination IATA codes, dates, passengers, budget, currency) from the free-text query using a Gemini-backed structured-output LLM call, with sensible defaults (e.g. defaults departure to Delhi, infers missing dates/budget).
2. **`flight_agent`**, **`hotel_agent`**, **`weather_agent`** — run in parallel off `query_agent`:
   - `flight_agent` calls a **remote MCP server** (`travel_mcp/mcp_client.py` → `travel_mcp/mcp_server.py`, a FastMCP tool wrapping SerpApi's Google Flights engine, currently deployed on Render) via `langchain-mcp-adapters`.
   - `hotel_agent` calls SerpApi's Google Hotels engine directly (`tools/hotel_search_tool.py`), sizing rooms/budget from passenger count and trip budget.
   - `weather_agent` calls the free Open-Meteo API (`tools/weather_tool.py`) — geocodes the destination, then pulls a forecast (extending the request window if the trip is more than 15 days out).
3. **`itinerary_agent`** — merges flight, hotel, and weather results into a day-by-day plan via the LLM.
4. **`final_agent`** — compiles everything into one Markdown-formatted report (trip summary, flights table, hotels table, weather table, day-by-day itinerary, budget breakdown, travel tips). On revision, it's re-prompted with the specific issues the Evaluation Agent flagged.
5. **`evaluation_agent`** — a structured-output LLM call that QA-checks the final plan (realistic pricing, valid dates, budget respected, internal consistency) and returns `passed`/`confidence`/`issues`.
6. **`evaluation_router`** — approves the plan if it passed with ≥0.85 confidence, or if `max_iteration` (default 3) revision attempts have been used; otherwise loops back to `final_agent` for another pass.

State is defined in `model.py` (`TravelState`) and persisted via a **Postgres-backed LangGraph checkpointer** (`db.py`, `PostgresSaver`), keyed by `thread_id` — this is what allows a trip to be resumed and shown in the history sidebar.

---

## ✨ Features

- 🧠 **Parallel multi-agent orchestration** — flight, hotel, and weather agents run concurrently off a single query-extraction step
- 🔁 **Self-evaluation loop** — a dedicated Evaluation Agent QA-checks the final plan and triggers automatic revisions (up to `max_iteration` times) before returning output
- 🛫 **Flight search** via a FastMCP tool server wrapping SerpApi's Google Flights engine
- 🏨 **Hotel search** via SerpApi's Google Hotels engine, budget-aware (rooms and per-night cap derived from party size and trip budget)
- 🌤️ **Weather forecasting** via Open-Meteo (free, no key required)
- 💾 **Persistent trip history** — every run is saved to a `trip_history` Postgres table (`user_email`, `thread_id`, query, result, status) and LangGraph state is checkpointed by `thread_id`
- 🔐 **Google OAuth login** using Streamlit's native `st.login("google")`
- 📄 **PDF export** — the final plan can be downloaded as a formatted PDF (`reportlab`, built in `frontend.py`)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Agent orchestration | LangGraph |
| LLM | Google Gemini (`langchain-google-genai`, `gemini-3.5-flash-lite`) |
| Tool integration | MCP (FastMCP server + `langchain-mcp-adapters`) |
| Flight & hotel data | SerpApi (Google Flights / Google Hotels engines) |
| Weather data | Open-Meteo |
| State persistence | PostgreSQL (`langgraph-checkpoint-postgres`, `psycopg`) |
| Auth | Streamlit native Google OAuth (`st.login`) |
| PDF export | ReportLab |
| Language | Python |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A PostgreSQL instance (local or hosted, e.g. Supabase/Neon/RDS)
- A Google AI (Gemini) API key
- A SerpApi API key (used for both flights and hotels — see note below)
- Google OAuth credentials for Streamlit login

### Installation

```bash
git clone https://github.com/priyanshu529/Multi-Agent-Travel-Planner.git
cd Multi-Agent-Travel-Planner
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration — `.streamlit/secrets.toml`

The app reads all credentials via `st.secrets`. Create `.streamlit/secrets.toml` in the project root:

```toml
# .streamlit/secrets.toml

# --- LLM (Gemini, used by query/itinerary/final/evaluation agents) ---
GOOGLE_API_KEY = "your_google_ai_api_key"

# --- Flight Agent (calls the remote MCP flight-search tool) ---
SERPAPI_API_KEY = "your_serpapi_key"

# --- Hotel Agent (SerpApi Google Hotels engine) ---
HOTEL_API_KEY = "your_serpapi_key"

# --- Postgres (LangGraph checkpointer + trip history) ---
DATABASE_URL = "postgresql://username:password@host:port/dbname"

# --- Google OAuth login (Streamlit native auth) ---
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "a-long-random-string-you-generate"
client_id = "your_google_oauth_client_id"
client_secret = "your_google_oauth_client_secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

**Notes:**
- `SERPAPI_API_KEY` and `HOTEL_API_KEY` currently point to the same SerpApi account/key — they're read separately (`mcp_client.py` vs `hotel_search_tool.py`), so both entries are required even though the value is identical today.
- The flight tool itself calls SerpApi through a **remote MCP server** already deployed at `https://serpapi-mcp-server-8u7m.onrender.com/mcp` (see `travel_mcp/mcp_client.py`). To run your own MCP server instead, deploy `travel_mcp/mcp_server.py` (it needs its own `SERPAPI_API_KEY` in its environment) and update the `url` in `mcp_client.py`.
- For Google OAuth setup (creating `client_id`/`client_secret` and configuring the redirect URI), follow [Streamlit's official `st.login` guide](https://docs.streamlit.io/develop/api-reference/user/st.login) — `Authlib` is required and should be added to `requirements.txt` if not already present.
- Never commit `secrets.toml` — it should be listed in `.gitignore`. On **Streamlit Community Cloud**, paste the same contents into **Settings → Secrets** instead.

### Running Locally

```bash
streamlit run frontend.py
```

(`main.py` is also available for a quick CLI test of the LangGraph pipeline without the UI: `python main.py`.)

---

## 🗂️ Project Structure

```
Multi-Agent-Travel-Planner/
├── frontend.py                  # Streamlit UI: login, trip form, history sidebar, PDF export
├── main.py                       # CLI entrypoint for testing the graph directly
├── graph.py                      # LangGraph StateGraph assembly (nodes + edges)
├── model.py                      # TravelState schema + Pydantic models (QueryExtract, EvaluationResult)
├── llm.py                        # Gemini LLM client setup
├── db.py                         # Postgres connection, LangGraph checkpointer, trip_history table
├── agents/
│   ├── query_extract.py           # Query Extraction Agent
│   ├── flight_agent.py            # Flight Agent (calls MCP tool)
│   ├── hotel_agent.py             # Hotel Agent (SerpApi Google Hotels)
│   ├── weather_agent.py           # Weather Agent (Open-Meteo)
│   ├── itinerary_agent.py         # Itinerary Agent
│   ├── final_agent.py             # Final Agent (compiles the Markdown report)
│   └── evaluation_agent.py        # Evaluation Agent + router
├── tools/
│   ├── hotel_search_tool.py       # SerpApi Google Hotels wrapper
│   └── weather_tool.py            # Open-Meteo geocoding + forecast wrapper
├── travel_mcp/
│   ├── mcp_client.py               # MultiServerMCPClient — connects to the flight MCP server
│   └── mcp_server.py               # FastMCP server exposing search_flights_prices (SerpApi Google Flights)
├── requirements.txt
└── .streamlit/
    └── secrets.toml                 # Not committed — see Configuration above
```

---



## 👤 Author

Created and designed by **Priyanshu**
🔗 [LinkedIn](https://www.linkedin.com/in/priyanshu-shishodiya-71a067333/)
