import os
import io
import uuid
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

st.set_page_config(
    page_title="Multi Agent Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background-color: #080d14;
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    height: 280px;
}
.hero-bg {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    filter: brightness(0.35);
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
    background: rgba(58,123,213,0.25);
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
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.6rem;
    line-height: 1.2;
}
.hero-sub {
    color: #94adc8;
    font-size: 1rem;
    max-width: 560px;
}

/* ── Input card ── */
.input-card {
    background: #0e1623;
    border: 1px solid #1e2e44;
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

/* ── Generate button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1a6bbf 0%, #0d4a8a 50%, #0a3d75 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2.5rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    width: 100% !important;
    box-shadow: 0 0 24px rgba(26,107,191,0.35), 0 4px 15px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 40px rgba(26,107,191,0.6), 0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, #2278d4 0%, #1057a0 50%, #0d4a8a 100%) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
}

/* ── Section headers ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e2e44;
}
.sec-head span { font-size: 1.15rem; font-weight: 600; color: #e0edf8; }

/* ── Final plan ── */
.final-card {
    background: linear-gradient(160deg, #0c1a2e 0%, #0a1520 100%);
    border: 1px solid #1e3a5c;
    border-left: 4px solid #3a7bd5;
    border-radius: 14px;
    padding: 1.8rem;
    line-height: 1.8;
    color: #cce0f5;
    font-size: 0.95rem;
}

/* ── Save bar ── */
.save-bar {
    background: #0e1623;
    border: 1px solid #1e2e44;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #5a8ab0;
    font-size: 0.88rem;
    margin-top: 0.5rem;
}

/* Hide branding */
#MainMenu, footer, header { visibility: hidden; }

/* Textarea */
.stTextArea textarea {
    background: #0a1520 !important;
    border: 1px solid #1e2e44 !important;
    border-radius: 10px !important;
    color: #e8f4ff !important;
    font-size: 0.95rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #3a7bd5 !important;
    box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important;
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
    border-color: #3a7bd5 !important;
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
    color: #cce0f5 !important;
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e8f4ff !important; }
.stMarkdown code {
    background: #0e1a2b !important;
    color: #7ab8f5 !important;
    padding: 0.15em 0.4em;
    border-radius: 4px;
}

.stAlert { background: #0e1a2b !important; border-radius: 10px !important; }
.stAlert p, .stAlert div { color: #e0edf8 !important; }

div[data-testid="stDownloadButton"] > button {
    background: #1a3a5c !important;
    color: #e8f4ff !important;
    border: 1px solid #2a5080 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session ID (unique per browser session — no shared memory across users) ──
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
thread_id = st.session_state.thread_id

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="airplane above clouds"/>
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title">✈️ Multi Agent Travel Planner</div>
        <div class="hero-sub">A crew of specialized AI agents plans your trip end to end — one extracts your trip details, others independently search flights, hotels and weather, an itinerary agent stitches it together, and a QA agent reviews the plan before it reaches you.</div>
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
        <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;cursor:pointer;">
            <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.55);" />
            <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center;
                        color:#fff;font-size:0.8rem;font-weight:600;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

# Full, well-formed example prompts instead of short keyword-style chips —
# these are what actually get filled into the textbox when clicked.
QUICK_PROMPTS = {
    "🇯🇵 Japan, 7 days": "Plan a complete 7-day trip to Japan for 2 people, including flights, hotels, and a day-by-day sightseeing itinerary, with a total budget of ₹2,00,000.",
    "🇫🇷 Paris, 5 days": "Plan a 5-day trip to Paris for 2 people, including round-trip flights, a centrally located hotel, and a day-by-day itinerary covering the main attractions.",
    "🇦🇪 Dubai, weekend": "Plan a 3-day weekend trip to Dubai for 2 people, including flights, a hotel near the city center, and a relaxed sightseeing itinerary.",
    "🇮🇩 Bali, 10 days": "Plan a 10-day backpacking trip to Bali for 1 person on a moderate budget, including flights, budget-friendly stays, and an itinerary covering beaches, temples, and local food spots.",
}

# The text area's content lives in session_state under "trip_query".
# We only ever WRITE to it (from a suggestion button) before the widget is
# created; the widget itself is bound via key=, not value=, so Streamlit
# doesn't blow away the box's contents on the next rerun (e.g. when you
# click "Generate" instead of a suggestion).
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


# ── Friendly names for each graph node, shown live as the pipeline runs ───────
# Add/rename keys here to match whatever your LangGraph node names actually are
# (check the node names you passed to `graph.add_node(...)` in main.py).
AGENT_LABELS = {
    "extraction_agent": "🔎 Calling extraction agent — reading your trip details",
    "extract_agent": "🔎 Calling extraction agent — reading your trip details",
    "parser_agent": "🔎 Calling extraction agent — reading your trip details",
    "flight_agent": "🛫 Calling flight agent — searching flights",
    "hotel_agent": "🏨 Calling hotel agent — searching hotels",
    "weather_agent": "⛅ Calling weather agent — checking the forecast",
    "itinerary_agent": "🗺️ Calling itinerary agent — building your day-by-day plan",
    "evaluation_agent": "🧐 Calling evaluation agent — reviewing the draft plan",
    "final_agent": "✅ Calling final agent — finalizing your travel plan",
}


def agent_label(node_name: str) -> str:
    """Friendly 'Calling X agent' label for a graph node, with a sane fallback
    for any node not explicitly listed in AGENT_LABELS."""
    if node_name in AGENT_LABELS:
        return AGENT_LABELS[node_name]
    pretty = node_name.replace("_", " ").replace("-", " ").strip()
    if not pretty.lower().endswith("agent"):
        pretty = f"{pretty} agent"
    return f"🤖 Calling {pretty}"


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

    # The final_response is markdown-ish text produced by the LLM.
    # Convert a light subset of markdown (headings, bold) into PDF paragraphs.
    for raw_line in (final_response or "No travel plan was generated.").split("\n"):
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        # Basic **bold** -> <b>bold</b> conversion
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


# ── Pipeline ──────────────────────────────────────────────────────────────────
if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        # Fresh, isolated run config for this session's UUID.
        config = {"configurable": {"thread_id": thread_id}}

        collected = {
            "final_response": "",
            "llm_calls": 0,
        }

        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "user_query": user_query,

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

        # Live status widget — updates its label per-node as the graph streams,
        # and keeps a running, expandable log of every agent that's been called.
        status = st.status("🤖 Starting the multi-agent pipeline...", expanded=True)

        try:
            for chunk in app.stream(
                initial_state,
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    if state_update is None:
                        continue

                    label = agent_label(node_name)
                    status.update(label=label)
                    status.write(label)

                    if node_name == "final_agent":
                        collected["final_response"] = state_update.get("final_result", "")

                    if "llm_calls" in state_update:
                        collected["llm_calls"] += state_update["llm_calls"]

            status.update(label="✅ Travel plan ready!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="❌ Pipeline failed", state="error", expanded=True)
            st.error(f"The travel planning pipeline failed: {e}")
            st.stop()

        # ── Final plan ────────────────────────────────────────────────────────
        st.markdown("---")
        if collected["final_response"]:
            st.markdown(
                "<div class='sec-head'><span>🧠 Your Travel Plan</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='final-card'>{collected['final_response']}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("No travel plan was generated. Please try again.")

        # ── Save & download (PDF) ────────────────────────────────────────────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.pdf"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        pdf_bytes = build_pdf(user_query, collected["final_response"], thread_id)

        with open(os.path.join(save_dir, filename), "wb") as f:
            f.write(pdf_bytes)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button(
                "⬇️ Download Plan (PDF)",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        with info_col:
            st.markdown(
                f"<div class='save-bar'>📁 Auto-saved → <code>travel_plans/{filename}</code></div>",
                unsafe_allow_html=True,
            )
