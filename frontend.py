import os
import io
import uuid
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app
from db import create_trip, update_trip_result, get_trip_history

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


def build_pdf(user_query: str, final_response: str, thread_id: str) -> bytes:
    """Render the final travel plan as a nicely formatted PDF and return its bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TripTitle", parent=styles["Title"], textColor=colors.HexColor("#0a3d75"), spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"], textColor=colors.HexColor("#555555"), fontSize=9, spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], textColor=colors.HexColor("#0d4a8a"),
        spaceBefore=14, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontSize=10.5, leading=16, spaceAfter=8,
    )

    story = [
        Paragraph("Your Travel Plan", title_style),
        Paragraph(f"<b>Request:</b> {user_query}", meta_style),
        Paragraph(
            f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · Session {thread_id}",
            meta_style,
        ),
        HRFlowable(width="100%", color=colors.HexColor("#dddddd")),
        Spacer(1, 10),
    ]

    for raw_line in (final_response or "No travel plan was generated.").split("\n"):
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        while "**" in line:
            line = line.replace("**", "<b>", 1)
            line = line.replace("**", "</b>", 1) if "**" in line else line

        if line.startswith("### "):
            story.append(Paragraph(line[4:], heading_style))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], heading_style))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], heading_style))
        elif line.startswith(("- ", "* ")):
            story.append(Paragraph(f"• {line[2:]}", body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --c-black: #05070a;
    --c-panel: #0e1623;
    --c-panel-2: #0a1520;
    --c-border: #1e2e44;
    --c-blue: #3a7bd5;
    --c-blue-dark: #0d4a8a;
    --c-red: #ef4444;
    --c-red-dark: #b91c1c;
    --c-white: #ffffff;
    --c-text: #cce0f5;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: var(--c-black);
}

/* Trim Streamlit's default top gap so nothing needs scrolling to appear */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    height: 280px;
    border: 1px solid var(--c-border);
}
.hero-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.32) saturate(1.1);
    position: absolute;
    top: 0; left: 0;
}
.hero-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 2rem;
}
.hero-badge {
    background: rgba(58,123,213,0.22);
    border: 1px solid rgba(58,123,213,0.5);
    color: #7ab8f5 !important;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 0.9rem;
    display: inline-block;
}
.hero-badge-live {
    background: rgba(239,68,68,0.18);
    border: 1px solid rgba(239,68,68,0.55);
    color: #ff9c9c !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    margin: 0 0 0.9rem 0.5rem;
    display: inline-block;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    margin: 0 0 0.6rem;
    line-height: 1.2;
    background: linear-gradient(90deg, #ffffff 0%, #7ab8f5 55%, #ff8a8a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: #94adc8;
    font-size: 1rem;
    max-width: 560px;
}

/* ── Input card ── */
.input-card {
    background: var(--c-panel);
    border: 1px solid var(--c-border);
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.5rem;
}
.input-label {
    color: #7ab8f5;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

/* ── Buttons: default (primary CTA) — blue-to-red gradient ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #ef4444 0%, #3a7bd5 55%, #0d4a8a 100%) !important;
    color: var(--c-white) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.5rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    box-shadow: 0 0 24px rgba(58,123,213,0.3), 0 4px 15px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 40px rgba(239,68,68,0.45), 0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
}

/* Quick-prompt chips + sidebar buttons: lighter, outlined, secondary style */
div[data-testid="column"] div[data-testid="stButton"] > button,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background: var(--c-panel-2) !important;
    border: 1px solid var(--c-border) !important;
    color: var(--c-text) !important;
    box-shadow: none !important;
    font-weight: 600 !important;
}
div[data-testid="column"] div[data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    border-color: var(--c-red) !important;
    color: #ffffff !important;
    box-shadow: 0 0 16px rgba(239,68,68,0.25) !important;
    transform: none !important;
}

/* Sidebar "New Trip" button — make it stand out red */
section[data-testid="stSidebar"] button[kind="secondary"]:first-of-type {
    border-color: var(--c-red) !important;
}

/* ── Section headers ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--c-border);
}
.sec-head span { font-size: 1.15rem; font-weight: 600; color: #e0edf8; }

/* ── Final plan ── */
.final-card {
    background: linear-gradient(160deg, #0c1a2e 0%, #0a1520 100%);
    border: 1px solid var(--c-border);
    border-left: 4px solid var(--c-red);
    border-radius: 14px;
    padding: 1.8rem;
    line-height: 1.8;
    color: var(--c-text);
    font-size: 0.95rem;
}

/* ── Save bar ── */
.save-bar {
    background: var(--c-panel);
    border: 1px solid var(--c-border);
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #5a8ab0;
    font-size: 0.88rem;
    margin-top: 0.5rem;
}

/* Textarea */
.stTextArea textarea {
    background: var(--c-panel-2) !important;
    border: 1px solid var(--c-border) !important;
    border-radius: 10px !important;
    color: #e8f4ff !important;
    font-size: 0.95rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--c-red) !important;
    box-shadow: 0 0 0 2px rgba(239,68,68,0.2) !important;
}
.stTextArea textarea::placeholder { color: #4a6a85 !important; }

/* Text input */
input[type="text"], .stTextInput input {
    background: #0e1a2b !important;
    border: 1px solid #1a2e44 !important;
    border-radius: 8px !important;
    color: #e0edf8 !important;
}
input[type="text"]:focus, .stTextInput input:focus {
    border-color: var(--c-blue) !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important;
}

/* Labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
    color: #7ab8f5 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
}

/* Markdown */
.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th {
    color: var(--c-text) !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e8f4ff !important; }
.stMarkdown code {
    background: #0e1a2b !important;
    color: #ff9c9c !important;
    padding: 0.15em 0.4em;
    border-radius: 4px;
}

.stAlert { background: #0e1a2b !important; border-radius: 10px !important; }
.stAlert p, .stAlert div { color: #e0edf8 !important; }

div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1a3a5c 0%, #7a1f1f 140%) !important;
    color: var(--c-white) !important;
    border: 1px solid var(--c-red) !important;
    border-radius: 10px !important;
}

/* ── Auth / login page (fixed: single self-contained block, no scroll) ── */
.auth-card {
    background: var(--c-panel);
    border: 1px solid var(--c-border);
    border-top: 3px solid var(--c-red);
    border-radius: 20px;
    padding: 2.2rem 2.5rem 1.6rem;
    max-width: 420px;
    width: 100%;
    margin: 3rem auto 0.5rem;
    text-align: center;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.auth-icon { font-size: 2.6rem; margin-bottom: 0.6rem; }
.auth-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--c-white);
    margin: 0 0 0.5rem;
}
.auth-sub {
    color: #94adc8;
    font-size: 0.92rem;
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

/* ── Header user bar ── */
.user-bar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.7rem;
    margin-bottom: 0.8rem;
}
.user-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--c-panel);
    border: 1px solid var(--c-blue);
    border-radius: 30px;
    padding: 0.35rem 0.9rem 0.35rem 0.4rem;
    color: var(--c-text);
    font-size: 0.85rem;
}
.user-chip img {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 2px solid var(--c-red);
}

/* Keep the sidebar collapse control visible even with header hidden */
#MainMenu, footer { visibility: hidden; }
header { visibility: hidden; }
header [data-testid="stSidebarCollapsedControl"],
header [data-testid="stHeader"] button,
button[kind="header"] {
    visibility: visible !important;
}
</style>
""", unsafe_allow_html=True)


# ── Auth gate (Google OAuth via Streamlit native auth) ─────────────────────
# NOTE: everything for the login card is rendered as ONE self-contained block
# (icon/title/sub + button) with no split/unclosed wrapper divs — that split
# was what left an empty ~80vh box above the button, forcing a scroll to see
# "Continue with Google". This version needs no scrolling on normal screens.
if not st.user.is_logged_in:
    st.markdown("""
        <div class="auth-card">
            <div class="auth-icon">✈️</div>
            <div class="auth-title">AI Travel Booking System</div>
            <div class="auth-sub">Sign in to plan flights, hotels, weather and a full
            day-by-day itinerary — powered by a multi-agent AI pipeline.</div>
        </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        if st.button("🔐  Continue with Google", use_container_width=True):
            st.login("google")

    st.stop()

# ── Logged in: user bar with name/avatar + logout ──────────────────────────
user_name = st.user.get("name") or st.user.get("email") or "there"
user_email = st.user.get("email", "")
user_picture = st.user.get("picture")

bar_l, bar_r = st.columns([5, 1])
with bar_l:
    st.markdown(
        f"<div style='color:#5a8ab0;font-size:0.85rem;padding-top:0.4rem;'>"
        f"Welcome back, <b style='color:#cce0f5;'>{user_name}</b></div>",
        unsafe_allow_html=True,
    )
with bar_r:
    if st.button("Log out", use_container_width=True):
        st.logout()

# ── Sidebar: saved trip history ──────────────────────────────────────────────
if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None

with st.sidebar:
    st.markdown("### 🧳 Past Trips")

    if st.button("➕ New Trip", use_container_width=True, key="new_trip_btn"):
        st.session_state.selected_trip = None
        st.rerun()

    st.divider()
    history = get_trip_history(user_email)

    if not history:
        st.caption("No saved trips yet — generate one and it will appear here.")
    else:
        for trip in history:
            query = trip.get("user_query", "Untitled trip")
            preview = query[:42] + ("…" if len(query) > 42 else "")
            status = trip.get("status", "done")
            is_pending = status == "pending"

            created_at = trip.get("created_at")
            date_str = created_at.strftime("%b %d, %I:%M %p") if created_at else ""
            icon = "⏳" if is_pending else "✈️"
            label = f"{icon} {preview}" + (f"\n{date_str}" if date_str else "")

            if st.button(
                label,
                key=f"hist_{trip['thread_id']}",
                use_container_width=True,
                disabled=is_pending,
            ):
                st.session_state.selected_trip = trip
                st.rerun()


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="airplane above clouds"/>
    <div class="hero-content">
        <span class="hero-badge">✦ Multi-Agent AI System</span><span class="hero-badge-live">● Live</span>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">Specialized agents work together — extracting your trip details, then searching flights, hotels, weather, and building your itinerary, with an automatic QA pass before delivery.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Destination strip ─────────────────────────────────────────────────────────
DESTINATIONS = [
    ("🇯🇵 Tokyo",   "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("🇫🇷 Paris",   "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("🇹🇭 Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("🇮🇹 Rome",    "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("🇦🇪 Dubai",   "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;cursor:pointer;
                     border:1px solid var(--c-border);">
            <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.55);" />
            <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center;
                        color:#fff;font-size:0.8rem;font-weight:600;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

QUICK_PROMPTS = {
    "🇯🇵 Japan, 7 days": "Plan a complete 7-day trip to Japan for 2 people, including flights, hotels, and a day-by-day sightseeing itinerary, with a total budget of ₹2,00,000.",
    "🇫🇷 Paris, 5 days": "Plan a 5-day trip to Paris for 2 people, including round-trip flights, a centrally located hotel, and a day-by-day itinerary covering the main attractions.",
    "🇦🇪 Dubai, weekend": "Plan a 3-day weekend trip to Dubai for 2 people, including flights, a hotel near the city center, and a relaxed sightseeing itinerary.",
    "🇮🇩 Bali, 10 days": "Plan a 10-day backpacking trip to Bali for 1 person on a moderate budget, including flights, budget-friendly stays, and an itinerary covering beaches, temples, and local food spots.",
}

if "trip_query" not in st.session_state:
    st.session_state.trip_query = ""

qcols = st.columns(len(QUICK_PROMPTS))
for qc, (label, full_prompt) in zip(qcols, QUICK_PROMPTS.items()):
    with qc:
        if st.button(label, key=f"q_{label}", use_container_width=True):
            st.session_state.trip_query = full_prompt

user_query = st.text_area(
    "",
    key="trip_query",
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing for 2 people, with a total budget of ₹2,00,000.",
    height=100,
    label_visibility="collapsed",
)

# Fixed internally — matches the backend's evaluation_agent -> final_agent
# revision loop (max_iteration in TravelState). No UI control exposed.
MAX_ITERATION = 3

generate = st.button("🚀  Generate My Travel Plan", use_container_width=True)


# ── Selected/current trip result ─────────────────────────────────────────────
selected_trip = st.session_state.get("selected_trip")
if selected_trip:
    st.markdown(
        "<div class='sec-head'><span>🧠 Travel Plan</span></div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Query: {selected_trip['user_query']}")
    st.markdown(selected_trip.get("final_result", ""))

    saved_pdf = build_pdf(
        selected_trip["user_query"],
        selected_trip.get("final_result", ""),
        selected_trip["thread_id"],
    )
    st.download_button(
        "⬇️ Download Plan (PDF)",
        data=saved_pdf,
        file_name=f"travel_plan_{selected_trip['thread_id']}.pdf",
        mime="application/pdf",
        key=f"pdf_{selected_trip['thread_id']}",
    )


# ── Phase 1: user clicks Generate ────────────────────────────────────────────
if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        thread_id = str(uuid.uuid4())
        try:
            create_trip(user_email, thread_id, user_query)
        except Exception as e:
            st.warning(f"Couldn't save this thread yet: {e}")

        st.session_state.pending_generation = {
            "thread_id": thread_id,
            "user_query": user_query,
        }
        st.rerun()


# ── Phase 2: the pipeline actually runs, on the rerun triggered above ────────
pending = st.session_state.get("pending_generation")
if pending:
    thread_id = pending["thread_id"]
    pending_query = pending["user_query"]
    config = {"configurable": {"thread_id": thread_id}}

    collected = {
    "final_response": "",
    "llm_calls": 0,
    "rejected": False,
    "rejection_reason": "",
}
    initial_state = {
        "messages": [HumanMessage(content=pending_query)],
        "user_query": pending_query,

        "departure_city_name": None,
        "departure_city_iata": None,
        "arrival_city_name": None,
        "arrival_city_iata": None,
        "country_name": None,
        "departure_date": None,
        "arrival_date": None,
        "return_date": None,
        "passenger": None,
        "passengers": None,
        "budget": None,
        "currency": None,

        "flight_result": "",
        "hotel_results": "",
        "weather_result": "",
        "itinerary": "",
        "final_result": "",
        "evaluation": {},
        "max_iteration": MAX_ITERATION,
        "revision_count": 0,
        "llm_calls": 0,
    }

    with st.spinner("🤖 Planning your trip..."):
        try:
            for chunk in app.stream(
                initial_state,
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    if state_update is None:
                        continue

                    if node_name == "input_guardrail" and state_update.get("input_rejected"):
                        collected["rejected"] = True
                        collected["rejection_reason"] = state_update.get(
                        "rejection_reason", "This request was rejected by the input guardrail."
                    )
                    
                    if node_name == "final_agent":
                        collected["final_response"] = state_update.get("final_result", "")

                    if "llm_calls" in state_update:
                        collected["llm_calls"] += state_update["llm_calls"]
        except Exception as e:
            st.error("The travel planning pipeline failed.")
            st.exception(e)          # renders full traceback in the app
    # or, if you want it as copyable text:
    # st.code(traceback.format_exc())
            del st.session_state.pending_generation
            st.stop()

    if collected["rejected"]:
        st.warning(f"🚫 {collected['rejection_reason']}")
        del st.session_state.pending_generation
        st.stop()
    
    final_response = collected["final_response"] or "No travel plan was generated. Please try again."

    try:
        update_trip_result(thread_id, final_response)
    except Exception as e:
        st.warning(f"Trip generated, but saving to history failed: {e}")

    del st.session_state.pending_generation

    st.session_state.selected_trip = {
        "thread_id": thread_id,
        "user_query": pending_query,
        "final_result": final_response,
        "created_at": datetime.now(),
        "status": "done",
    }
    st.rerun()
