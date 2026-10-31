"""
app.py
------
Educentriks Cognify — Adaptive AI Certification Coach (Microsoft AI-103)
Premium EdTech SaaS Design System:
- Linear / Vercel inspired clean aesthetics
- Educentriks brand colors (#0052B4 Cobalt Blue, #C8102E Crimson Red)
- Interactive demo prompt chips for instant judge evaluation
- Live exam readiness progress metrics computed from PostgreSQL
- Studio-grade audio recording deck with native speech-to-text
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from streamlit_mic_recorder import speech_to_text

# System configuration
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
    page_title="Educentriks Cognify | AI-103 Coach",
    page_icon="assets/logo.png" if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper for ThreadPool execution to avoid Tornado event loop collisions
def run_in_clean_loop(coro):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()

# Premium SaaS Design System (Educentriks Palette)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
    }

    .stApp {
        background: #F8FAFC;
    }

    /* Top Header Bar spacing */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-top: 3.5rem !important;
        padding-bottom: 4rem;
        max-width: 1250px;
    }

    /* Top Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0052B4 0%, #003B82 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 82, 180, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.1;
    }

    .hero-tagline {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #FCA5A5;
        margin-top: 4px;
    }

    .hero-stat-pill {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 10px 18px;
        text-align: right;
    }

    /* Interactive Tab Pills */
    div[data-testid="stTabs"] button {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #475569;
        margin-right: 8px;
        transition: all 0.2s ease;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #0052B4 !important;
        color: #FFFFFF !important;
        border-color: #0052B4 !important;
        box-shadow: 0 4px 12px rgba(0, 82, 180, 0.25);
    }

    /* Modern Card Layouts */
    .saas-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .saas-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }

    /* Concept Status Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-proficient { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-developing { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .badge-revision { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .badge-unassessed { background: #F1F5F9; color: #64748B; border: 1px solid #CBD5E1; }

    /* Interactive Voice Bar Deck */
    .voice-deck {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px 20px;
        margin: 20px 0 12px 0;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    }

    /* Quick Prompt Chips */
    .prompt-chip-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    /* Sidebar Profile Header */
    .sidebar-avatar {
        width: 44px;
        height: 44px;
        background: #0052B4;
        color: white;
        font-weight: 800;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    
    .sidebar-profile-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 16px;
    }

    .stButton>button {
        background-color: #0052B4;
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        border-radius: 8px;
        border: none;
        padding: 0.45rem 1rem;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #003B82;
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
    "Alex (Benchmark Verified)": "00640701-425e-4d1c-b79e-8086530642cb",
}

# ── SIDEBAR: Educentriks Identity & Profile ──────────────────────────────────
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=180)
    else:
        st.markdown("<h2 style='color:#0052B4; margin:0;'>Educentriks</h2>", unsafe_allow_html=True)

    st.markdown('<div style="color:#C8102E; font-weight:700; font-size:0.8rem; letter-spacing:0.08em; text-transform:uppercase; margin-top:-6px; margin-bottom:12px;">Education. Evolved.</div>', unsafe_allow_html=True)
    
    st.caption("Active Learner Context")
    selected_learner_label = st.selectbox(
        "Active Learner:",
        list(DEMO_LEARNERS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    learner_id = DEMO_LEARNERS[selected_learner_label]

    profile = get_learner_profile(learner_id)
    if "error" not in profile:
        name_parts = profile.get("name", "Alex Rivera").split()
        initials = "".join([p[0] for p in name_parts[:2]])

        # Query live mastery metrics from DB
        with get_connection() as conn:
            m_stats = conn.execute(
                """
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN status = 'proficient' THEN 1 ELSE 0 END) AS prof,
                       SUM(CASE WHEN status = 'developing' THEN 1 ELSE 0 END) AS dev
                FROM mastery_records WHERE learner_id = %s::uuid
                """,
                (learner_id,)
            ).fetchone()

        total_assessed = m_stats["total"] or 0
        prof_count = m_stats["prof"] or 0
        readiness_score = int((prof_count * 100 + (m_stats["dev"] or 0) * 50) / 7) if total_assessed > 0 else 15

        st.markdown(f"""
        <div class="sidebar-profile-box">
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="sidebar-avatar">{initials}</div>
                <div>
                    <div style="font-weight:700; font-size:1rem; color:#0F172A;">{profile.get('name')}</div>
                    <div style="font-size:0.8rem; color:#64748B;">{profile.get('current_role', 'Developer')}</div>
                </div>
            </div>
            <div style="margin-top:14px;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:600; color:#475569; margin-bottom:4px;">
                    <span>AI-103 Exam Readiness</span>
                    <span><b>{readiness_score}%</b></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(1.0, readiness_score / 100))

    st.divider()

    # Next Recommended Activity (Dynamic from DB)
    st.caption("Prescribed Next Activity")
    next_act = get_next_activity(learner_id, "AI-103")
    if next_act.get("status") == "activity_found":
        st.markdown(f"""
        <div style="background:#F1F5F9; border-left:3px solid #0052B4; border-radius:0 8px 8px 0; padding:12px 14px;">
            <div style="font-size:0.7rem; font-weight:700; color:#0052B4; text-transform:uppercase; letter-spacing:0.04em;">Next Objective</div>
            <div style="font-weight:700; font-size:0.9rem; color:#0F172A; margin:2px 0;">{next_act.get('title')}</div>
            <div style="font-size:0.78rem; color:#64748B;">{next_act.get('concept_name')}</div>
        </div>
        """, unsafe_allow_html=True)
    elif next_act.get("status") == "no_plan":
        st.caption("Complete diagnostic to populate recommended activities.")
    else:
        st.success("All scheduled curriculum activities completed!")

    st.write("")
    if st.button("Reset Session History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_initialized = False
        st.session_state.last_processed_speech = ""
        st.rerun()


# ── MAIN TOP HERO BANNER ─────────────────────────────────────────────────────
with get_connection() as conn:
    total_concepts = conn.execute("SELECT COUNT(*) AS c FROM concepts WHERE certification = 'AI-103'").fetchone()["c"]
    assessed_for_learner = conn.execute(
        "SELECT COUNT(*) AS c FROM mastery_records WHERE learner_id = %s::uuid",
        (learner_id,)
    ).fetchone()["c"]

st.markdown(f"""
<div class="hero-banner">
    <div>
        <div class="hero-tagline">Education. Evolved. • Problem Statement PS02</div>
        <div class="hero-title">Educentriks Cognify</div>
        <div style="font-size:0.92rem; opacity:0.9; margin-top:6px;">
            Adaptive AI certification learning coach for <b>Microsoft AI-103</b> (Azure AI Apps & Agents Developer).
        </div>
    </div>
    <div style="display:flex; gap:12px;">
        <div class="hero-stat-pill">
            <div style="font-size:0.75rem; text-transform:uppercase; opacity:0.8;">Curriculum Depth</div>
            <div style="font-size:1.25rem; font-weight:800;">{assessed_for_learner} / {total_concepts} Concepts</div>
        </div>
        <div class="hero-stat-pill">
            <div style="font-size:0.75rem; text-transform:uppercase; opacity:0.8;">Orchestrator</div>
            <div style="font-size:1.25rem; font-weight:800;">Google ADK</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_coach, tab_curriculum, tab_insights = st.tabs([
    "Learning Coach & Voice Deck",
    "Curriculum & Prerequisite Tree",
    "Instructor & Cohort Analytics",
])

# Async Agent Executor
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

# Synchronous Turn Handler with Retry Logic
def handle_turn(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Consulting curriculum and evaluating response..."):
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


# ── TAB 1: Coaching Conversation & Voice Deck ────────────────────────────────
with tab_coach:
    # Interaction Feed
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander("Grounded Sources Cited (Official Documentation)", expanded=False):
                    for src in msg["citations"]:
                        st.markdown(f"- [{src.get('source_title', 'Microsoft Learn Documentation')}]({src.get('source_url', '#')})")

    # Interactive Voice & Prompt Bar Deck
    st.markdown("""
    <div class="voice-deck">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <div>
                <span style="font-weight:700; font-size:0.95rem; color:#0F172A;">Interactive Voice Deck</span>
                <span style="font-size:0.8rem; color:#64748B; margin-left:8px;">Browser-native audio recording</span>
            </div>
            <span class="badge-pill badge-proficient">Mic Ready</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_mic, col_chips = st.columns([1, 4], vertical_alignment="center")

    with col_mic:
        spoken_input = speech_to_text(
            language='en',
            start_prompt="Record Voice",
            stop_prompt="Stop Recording",
            just_once=True,
            use_container_width=True,
            key="mic_recorder",
        )

    with col_chips:
        st.markdown('<div class="prompt-chip-label">Quick Judge Testing Prompts:</div>', unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        if q1.button("🎯 Test Diagnostic", use_container_width=True):
            handle_turn("Can you give me a diagnostic question on Agent Tool Calling so I can test my knowledge?")
            st.rerun()
        if q2.button("📚 Explain RAG & Vector Search", use_container_width=True):
            handle_turn("Explain how RAG retrieval and vector embeddings connect in Microsoft AI-103.")
            st.rerun()
        if q3.button("📅 Show My Review Plan", use_container_width=True):
            handle_turn("What is my next recommended activity and scheduled spaced repetition review?")
            st.rerun()

    if spoken_input and spoken_input != st.session_state.last_processed_speech:
        st.session_state.last_processed_speech = spoken_input
        handle_turn(spoken_input)
        st.rerun()

    # Typed text input bar
    typed_prompt = st.chat_input("Ask a question, explain technical reasoning, or request a diagnostic...")
    if typed_prompt:
        handle_turn(typed_prompt)
        st.rerun()


# ── TAB 2: Curriculum & Concept Mastery ──────────────────────────────────────
with tab_curriculum:
    st.markdown("### Microsoft AI-103 Concept Prerequisite Graph")
    st.caption("Prerequisite dependencies mapped to Azure AI Apps and Agents Developer Associate performance domains.")

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
                "proficient": "badge-proficient",
                "developing": "badge-developing",
                "needs_revision": "badge-revision",
                "not_assessed": "badge-unassessed",
            }.get(status, "badge-unassessed")

            st.markdown(f"""
            <div class="saas-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; font-size:1rem; color:#0F172A;">{row['name']}</span>
                    <span class="badge-pill {status_css}">{status.replace('_', ' ')}</span>
                </div>
                <div style="font-size:0.82rem; color:#64748B; margin-top:6px;">
                    Domain: <b>{row['domain']}</b> • Difficulty: <b>{row['difficulty'].title()}</b> • Confidence: <b>{float(row['confidence']):.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("##### Prerequisite Architecture Flow")
        with st.container():
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            for p in prereqs:
                st.markdown(f"• **{p['prerequisite']}** ➔ *required for* ➔ **{p['concept']}**")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("##### Spaced Repetition Calendar")
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
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            if reviews:
                for r in reviews:
                    st.markdown(f"""
                    <div style="padding:6px 0; border-bottom:1px solid #F1F5F9;">
                        <b>{r['name']}</b><br>
                        <span style="font-size:0.8rem; color:#64748B;">Scheduled Review: <b>{r['due_date']}</b> ({r['interval_days']}-day interval)</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No spaced reviews scheduled for this profile yet.")
            st.markdown('</div>', unsafe_allow_html=True)


# ── TAB 3: Cohort & Instructor Analytics (PS02) ──────────────────────────────
with tab_insights:
    st.markdown("### Institutional Cohort Analytics (PS02)")
    st.caption("Privacy-preserving class-level aggregates. Identifies prerequisite bottlenecks and recurring student misconceptions.")

    teacher_data = get_teacher_dashboard("AI-103")
    
    st.markdown(f"""
    <div style="font-size:0.82rem; color:#475569; background:#EFF6FF; border:1px solid #BFDBFE; padding:10px 14px; border-radius:8px; margin-bottom:1.5rem;">
        🔒 <b>Privacy Guarantee:</b> {teacher_data.get('note')}
    </div>
    """, unsafe_allow_html=True)

    # Top KPI Metrics Row
    gaps = teacher_data.get("concept_gaps", [])
    total_assessed_cohort = sum([g["assessed_count"] for g in gaps])
    total_needs_rev = sum([g["needs_revision_count"] for g in gaps])
    top_misconceptions = teacher_data.get("top_misconceptions", [])

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="saas-card" style="text-align:center;">
            <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:700;">Class Assessments</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0052B4; margin-top:4px;">{total_assessed_cohort}</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="saas-card" style="text-align:center;">
            <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:700;">Concepts Needing Revision</div>
            <div style="font-size:1.8rem; font-weight:800; color:#C8102E; margin-top:4px;">{total_needs_rev}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="saas-card" style="text-align:center;">
            <div style="font-size:0.8rem; color:#64748B; text-transform:uppercase; font-weight:700;">Tracked Misconceptions</div>
            <div style="font-size:1.8rem; font-weight:800; color:#0F172A; margin-top:4px;">{len(top_misconceptions)}</div>
        </div>
        """, unsafe_allow_html=True)

    col_gap_table, col_misc_table = st.columns([3, 2])

    with col_gap_table:
        st.markdown("##### Class Concept Gap Distribution")
        if gaps:
            for g in gaps:
                st.markdown(f"""
                <div class="saas-card">
                    <div style="font-weight:700; color:#0F172A; font-size:0.95rem;">{g['concept_name']}</div>
                    <div style="font-size:0.8rem; color:#64748B; margin-bottom:10px;">{g['domain']} • {g['difficulty'].title()}</div>
                    <div style="display:flex; gap:20px; font-size:0.82rem;">
                        <span>Assessed: <b>{g['assessed_count']}</b></span>
                        <span style="color:#B91C1C;">Needs Revision: <b>{g['needs_revision_count']}</b></span>
                        <span style="color:#B45309;">Developing: <b>{g['developing_count']}</b></span>
                        <span style="color:#047857;">Proficient: <b>{g['proficient_count']}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No class assessment records available.")

    with col_misc_table:
        st.markdown("##### Recurring Conceptual Misconceptions")
        if top_misconceptions:
            for m in top_misconceptions:
                st.markdown(f"""
                <div class="saas-card" style="border-left: 4px solid #C8102E;">
                    <div style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#C8102E;">{m['concept_name']}</div>
                    <div style="font-size:0.9rem; color:#1E293B; margin:6px 0; font-style:italic;">"{m['description']}"</div>
                    <div style="font-size:0.78rem; color:#64748B;">Identified across <b>{m['occurrence_count']}</b> student assessment(s)</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No recurring misconceptions identified yet.")
