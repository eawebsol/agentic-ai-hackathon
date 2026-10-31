"""
app.py
------
Educentriks Cognify
Adaptive Certification Coach • Microsoft AI-103
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from streamlit_mic_recorder import speech_to_text

# System path & configuration
sys.path.append(str(Path(__file__).resolve().parent))

for env_path in [Path("hello_agent/.env"), Path(".env")]:
    if env_path.exists():
        load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

openrouter_key = os.getenv("OPENROUTER_API_KEY")
if openrouter_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_key

from agents.tutor.agent import cognify_agent
from agents.tutor.tools.profile import get_learner_profile
from agents.tutor.tools.activity import get_next_activity
from agents.tutor.tools.events import get_teacher_dashboard
from agents.tutor.tools.curriculum import get_exam_objectives
from api.database import get_connection

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

LOGO_PATH = Path("assets/logo.png")

# Page Configuration
st.set_page_config(
    page_title="Educentriks Cognify",
    page_icon="assets/logo.png" if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper to run async coroutines safely in Streamlit without loop collisions
def run_in_clean_loop(coro):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

# Custom Design System — Professional, Editorial, Clean
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Ensure Streamlit top header never overlaps tabs */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .stDeployButton {
        display: none !important;
    }
    
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .brand-header {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #0052B4;
        margin: 0;
        line-height: 1.2;
    }
    
    .brand-tagline {
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #C8102E;
        margin-top: 4px;
        margin-bottom: 6px;
    }

    .brand-description {
        font-size: 0.95rem;
        color: #475569;
        margin-bottom: 1.25rem;
        font-weight: 400;
        line-height: 1.5;
    }

    .badge-primary {
        display: inline-flex;
        align-items: center;
        background-color: #EFF6FF;
        color: #0052B4;
        border: 1px solid #BFDBFE;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
    }

    .badge-status {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: capitalize;
    }

    .status-proficient { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .status-developing { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .status-revision { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .status-unassessed { background: #F1F5F9; color: #64748B; border: 1px solid #CBD5E1; }

    .surface-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .profile-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .activity-panel {
        background: #F8FAFC;
        border-left: 3px solid #0052B4;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 12px 0;
    }

    .stButton button {
        background-color: #0052B4;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        border-radius: 6px;
        border: none;
    }
    
    .stButton button:hover {
        background-color: #003E8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_processed_speech" not in st.session_state:
    st.session_state.last_processed_speech = ""

if "adk_runner" not in st.session_state or st.session_state.get("model_name") != cognify_agent.model:
    session_service = InMemorySessionService()
    st.session_state.session_service = session_service
    st.session_state.adk_runner = Runner(
        agent=cognify_agent,
        session_service=session_service,
        app_name="educentriks_cognify",
    )
    st.session_state.model_name = cognify_agent.model
    st.session_state.session_initialized = False

DEMO_LEARNERS = {
    "Alex Rivera (Transitioning Developer)": "00000000-0000-0000-0000-000000000001",
    "Sarah Chen (Solutions Architect)": "00000000-0000-0000-0000-000000000002",
    "Alex (Verified Benchmark Profile)": "00640701-425e-4d1c-b79e-8086530642cb",
}

# ── SIDEBAR: Navigation & Learner Context ────────────────────────────────────
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=190)
    else:
        st.markdown("<h3 style='color:#0052B4; margin:0;'>Educentriks</h3>", unsafe_allow_html=True)

    st.markdown('<div class="brand-tagline">Education. Evolved.</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge-primary">Microsoft AI-103 Track</span>', unsafe_allow_html=True)
    st.write("")

    st.caption("Active Learner Profile")
    selected_learner_label = st.selectbox(
        "Select Profile:",
        list(DEMO_LEARNERS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    learner_id = DEMO_LEARNERS[selected_learner_label]

    profile = get_learner_profile(learner_id)
    if "error" not in profile:
        with st.container():
            st.markdown(f"""
            <div class="profile-card">
                <div style="font-weight:700; font-size:1.05rem; color:#0F172A;">{profile.get('name')}</div>
                <div style="font-size:0.82rem; color:#64748B; margin-top:2px;">{profile.get('current_role', 'Engineer')} • {profile.get('experience_level', 'Intermediate').title()}</div>
                <div style="margin-top: 8px; font-size: 0.78rem; color: #475569;">
                    Target: <b>{profile.get('target_certification', 'AI-103')}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            prefs = profile.get("learning_preferences", [])
            if prefs:
                st.caption(f"Preferences: {', '.join(prefs)}")
    else:
        st.caption("Profile unavailable in local store.")

    st.divider()

    st.caption("Adaptive Focus")
    next_act = get_next_activity(learner_id, "AI-103")
    if next_act.get("status") == "activity_found":
        st.markdown(f"""
        <div class="activity-panel">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.04em; font-weight:700; color:#0052B4;">Next Step</div>
            <div style="font-weight:700; font-size:0.92rem; color:#0F172A; margin: 2px 0;">{next_act.get('title')}</div>
            <div style="font-size:0.8rem; color:#64748B;">{next_act.get('concept_name')}</div>
        </div>
        """, unsafe_allow_html=True)
    elif next_act.get("status") == "no_plan":
        st.caption("Complete diagnostic to populate recommended activities.")
    else:
        st.caption("All scheduled activities completed.")

    st.write("")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_initialized = False
        st.session_state.last_processed_speech = ""
        st.rerun()


# ── MAIN CONTENT AREA ────────────────────────────────────────────────────────
st.markdown('<div class="brand-header">Educentriks Cognify</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-description">Adaptive learning coach for Microsoft Certified: Azure AI Apps and Agents Developer Associate (AI-103). Diagnoses conceptual gaps, verifies technical reasoning, and adapts based on objective evidence.</div>', unsafe_allow_html=True)

tab_coach, tab_curriculum, tab_insights = st.tabs([
    "Learning Coach",
    "Curriculum & Mastery Graph",
    "Cohort Analytics",
])

# Async Agent Executor (Pure async function, no thread-local session_state dependencies)
async def execute_agent_turn(user_text: str, runner: Runner, session_service, current_learner_id: str):
    sess_id = f"sess_{current_learner_id}"
    try:
        await session_service.create_session(
            app_name="educentriks_cognify",
            user_id="user",
            session_id=sess_id,
        )
    except Exception:
        pass

    content = Content(parts=[Part(text=f"[Learner ID: {current_learner_id}]\n{user_text}")])
    citations = []
    tutor_response_text = ""
    tool_calls_executed = []

    async for event in runner.run_async(
        user_id="user",
        session_id=sess_id,
        new_message=content,
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if getattr(part, "function_call", None):
                    tool_calls_executed.append(part.function_call.name)
                if getattr(part, "function_response", None):
                    fr = part.function_response
                    if fr.name == "search_learning_resources":
                        resp = fr.response or {}
                        for ch in resp.get("chunks", []):
                            if ch.get("source_url"):
                                citations.append(ch)
                if getattr(part, "text", None):
                    tutor_response_text += part.text

    if not tutor_response_text and tool_calls_executed:
        tutor_response_text = "I have updated your learner record and consulted the AI-103 curriculum. How would you like to proceed with your study plan?"

    return tutor_response_text, citations

# Synchronous Turn Handler with Automatic 503 Spike Resilience
def handle_turn(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Analyzing response and consulting curriculum..."):
        max_retries = 3
        last_error = None
        for attempt in range(max_retries):
            try:
                runner = st.session_state.adk_runner
                service = st.session_state.session_service
                active_id = learner_id
                
                response_text, citations = run_in_clean_loop(
                    execute_agent_turn(user_input, runner, service, active_id)
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "citations": citations,
                })
                return
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    import time
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Service connection note: {last_error}. Please try your request once more.",
            "citations": [],
        })

# ── TAB 1: Coaching Conversation ─────────────────────────────────────────────
with tab_coach:
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander("Grounded Sources Cited", expanded=False):
                    for src in msg["citations"]:
                        st.markdown(f"- [{src.get('source_title', 'Microsoft Documentation')}]({src.get('source_url', '#')})")

    # Voice Input Bar
    st.markdown("<div style='margin-top:1.5rem; margin-bottom:0.5rem; font-size:0.85rem; font-weight:600; color:#475569;'>Voice or Text Response</div>", unsafe_allow_html=True)
    
    col_speech, col_info = st.columns([1, 4])
    with col_speech:
        spoken_input = speech_to_text(
            language='en',
            start_prompt="Speak Answer",
            stop_prompt="Listening...",
            just_once=True,
            use_container_width=True,
            key="mic_recorder",
        )

    with col_info:
        st.caption("Click 'Speak Answer' to speak naturally, or use the text box below. Cognify evaluates conceptual reasoning against official rubrics.")

    # Check for speech transcription
    if spoken_input and spoken_input != st.session_state.last_processed_speech:
        st.session_state.last_processed_speech = spoken_input
        handle_turn(spoken_input)
        st.rerun()

    # Typed text input
    typed_prompt = st.chat_input("Ask a question, request a diagnostic, or explain a technical scenario...")
    if typed_prompt:
        handle_turn(typed_prompt)
        st.rerun()


# ── TAB 2: Curriculum & Concept Mastery ──────────────────────────────────────
with tab_curriculum:
    st.subheader("Curriculum Concept Graph")
    st.caption("Prerequisite dependencies mapped to Microsoft AI-103 performance domains.")

    with get_connection() as conn:
        concepts = conn.execute(
            """
            SELECT c.id, c.slug, c.name, c.domain, c.difficulty,
                   COALESCE(mr.status, 'not_assessed') AS mastery_status,
                   COALESCE(mr.confidence, 0.0) AS confidence
            FROM concepts c
            LEFT JOIN mastery_records mr
                ON mr.concept_id = c.id AND mr.learner_id = %s::uuid
            ORDER BY c.difficulty, c.name
            """,
            (learner_id,)
        ).fetchall()

        prereqs = conn.execute(
            """
            SELECT c.name AS concept, p.name AS prerequisite
            FROM concept_prerequisites cp
            JOIN concepts c ON cp.concept_id = c.id
            JOIN concepts p ON cp.prerequisite_id = p.id
            """
        ).fetchall()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("##### Topic Mastery Breakdown")
        for row in concepts:
            status = row["mastery_status"]
            status_css = {
                "proficient": "status-proficient",
                "developing": "status-developing",
                "needs_revision": "status-revision",
                "not_assessed": "status-unassessed",
            }.get(status, "status-unassessed")

            with st.container():
                st.markdown(f"""
                <div class="surface-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:700; font-size:0.95rem; color:#0F172A;">{row['name']}</span>
                        <span class="badge-status {status_css}">{status.replace('_', ' ')}</span>
                    </div>
                    <div style="font-size:0.8rem; color:#64748B; margin-top:4px;">
                        Domain: {row['domain']} • Difficulty: {row['difficulty'].title()} • Evidence: {float(row['confidence']):.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown("##### Prerequisite Sequence")
        with st.container():
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            for p in prereqs:
                st.markdown(f"• **{p['prerequisite']}** → {p['concept']}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("##### Spaced Repetition Schedule")
        with get_connection() as conn:
            reviews = conn.execute(
                """
                SELECT c.name, rs.due_date, rs.interval_days
                FROM review_schedules rs
                JOIN concepts c ON rs.concept_id = c.id
                WHERE rs.learner_id = %s::uuid
                ORDER BY rs.due_date ASC
                """,
                (learner_id,)
            ).fetchall()

        with st.container():
            st.markdown('<div class="surface-card">', unsafe_allow_html=True)
            if reviews:
                for r in reviews:
                    st.markdown(f"**{r['name']}** — Next review due on `{r['due_date']}` ({r['interval_days']}-day cadence)")
            else:
                st.caption("No spaced reviews scheduled for this profile yet.")
            st.markdown('</div>', unsafe_allow_html=True)


# ── TAB 3: Cohort & Instructor Analytics ─────────────────────────────────────
with tab_insights:
    st.subheader("Cohort Gap Assessment")
    st.caption("Aggregated institutional overview evaluating common curriculum friction points without exposing individual responses.")

    teacher_data = get_teacher_dashboard("AI-103")
    
    st.markdown(f"""
    <div style="font-size:0.82rem; color:#475569; background:#F1F5F9; padding:8px 12px; border-radius:6px; margin-bottom:1rem;">
        <b>Privacy Guarantee:</b> {teacher_data.get('note')}
    </div>
    """, unsafe_allow_html=True)

    col_gap_table, col_misconceptions = st.columns([3, 2])

    with col_gap_table:
        st.markdown("##### Concept Mastery Distribution")
        gaps = teacher_data.get("concept_gaps", [])
        if gaps:
            for g in gaps:
                with st.container():
                    st.markdown(f"""
                    <div class="surface-card">
                        <div style="font-weight:700; color:#0F172A; font-size:0.92rem;">{g['concept_name']}</div>
                        <div style="font-size:0.78rem; color:#64748B; margin-bottom:8px;">{g['domain']} • {g['difficulty'].title()}</div>
                        <div style="display:flex; gap:16px; font-size:0.82rem;">
                            <span>Assessed: <b>{g['assessed_count']}</b></span>
                            <span style="color:#B91C1C;">Needs Revision: <b>{g['needs_revision_count']}</b></span>
                            <span style="color:#B45309;">Developing: <b>{g['developing_count']}</b></span>
                            <span style="color:#047857;">Proficient: <b>{g['proficient_count']}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.caption("No student diagnostic data recorded yet.")

    with col_misconceptions:
        st.markdown("##### Recurring Conceptual Misconceptions")
        top_misc = teacher_data.get("top_misconceptions", [])
        if top_misc:
            for m in top_misc:
                st.markdown(f"""
                <div class="surface-card" style="border-left: 3px solid #C8102E;">
                    <div style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#C8102E;">{m['concept_name']}</div>
                    <div style="font-size:0.88rem; color:#1E293B; margin:6px 0; font-style:italic;">"{m['description']}"</div>
                    <div style="font-size:0.78rem; color:#64748B;">Identified across <b>{m['occurrence_count']}</b> student assessment(s)</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No recurring misconceptions identified yet.")
