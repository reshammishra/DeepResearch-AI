import os
import re
import time
from datetime import datetime
import streamlit as st

# Configure page
st.set_page_config(
    page_title="ResearchAI - Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for SaaS Dashboard Light Aesthetic
st.markdown(
    """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0f172a;
    }

    /* Background overrides */
    .stApp {
        background-color: #f8fafc;
    }

    /* Hide default streamlit decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    /* Card Containers */
    .saas-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }

    .saas-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 12px;
    }

    .saas-card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0;
    }

    /* Status Pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #ecfdf5;
        color: #059669;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #a7f3d0;
    }

    .status-badge.working {
        background-color: #eff6ff;
        color: #2563eb;
        border-color: #bfdbfe;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
    }

    .status-dot.pulsing {
        background-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
    }

    /* Workflow Pipeline Steps */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 16px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        margin-bottom: 24px;
        overflow-x: auto;
    }

    .pipeline-step {
        flex: 1;
        min-width: 170px;
        padding: 12px 14px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.2s ease;
    }

    .pipeline-step.active {
        border-color: #3b82f6;
        background: #eff6ff;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
    }

    .pipeline-step.completed {
        border-color: #10b981;
        background: #f0fdf4;
    }

    .step-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        background: #e2e8f0;
        color: #64748b;
    }

    .pipeline-step.active .step-number {
        background: #2563eb;
        color: #ffffff;
    }

    .pipeline-step.completed .step-number {
        background: #10b981;
        color: #ffffff;
    }

    .step-info {
        display: flex;
        flex-direction: column;
    }

    .step-name {
        font-size: 0.88rem;
        font-weight: 600;
        color: #1e293b;
    }

    .step-desc {
        font-size: 0.72rem;
        color: #64748b;
    }

    .pipeline-arrow {
        color: #cbd5e1;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* Critique Score Callout */
    .score-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        margin-bottom: 16px;
    }

    .score-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2563eb;
        line-height: 1;
    }

    .score-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Review sections */
    .critic-section {
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    .critic-strengths {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
    }

    .critic-improvements {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
    }

    .critic-verdict {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        font-style: italic;
    }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 9px;
        font-weight: 600;
        transition: all 0.15s ease-in-out;
    }

    .stButton>button:hover {
        border-color: #2563eb;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15);
    }

    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 9px;
        border-color: #cbd5e1;
        font-size: 0.95rem;
    }

    .stTextInput>div>div>input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748b;
        background-color: transparent;
        border: none;
    }

    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 2px solid #2563eb !important;
        background-color: #eff6ff !important;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        background: #ffffff;
    }

    .empty-icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }

    .empty-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
    }

    .empty-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        max-width: 500px;
        margin: 0 auto 20px auto;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper function to sanitize text content
def clean_content(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        res = []
        for c in content:
            if isinstance(c, dict) and "text" in c:
                res.append(c["text"])
            elif isinstance(c, str):
                res.append(c)
            else:
                res.append(str(c))
        return "\n".join(res)
    return str(content)


def extract_http_urls(text):
    urls = re.findall(r'https?://[^\s\)\]\"\'<>]+', text)
    unique_urls = []
    seen = set()
    for url in urls:
        url = url.rstrip(".,;:!?")
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    return unique_urls


def select_topic(topic):
    st.session_state.topic_input = topic


# Parse critic feedback strictly based on returned text
def parse_critic_feedback(feedback_text):
    feedback_text = clean_content(feedback_text)
    data = {
        "score": None,
        "strengths": [],
        "improvements": [],
        "verdict": None,
        "raw": feedback_text,
    }

    # Extract score like Score: 8/10 or Score: 8
    score_match = re.search(r"Score:\s*(\d+(?:\.\d+)?(?:\s*/\s*10)?)", feedback_text, re.IGNORECASE)
    if score_match:
        data["score"] = score_match.group(1).replace(" ", "")

    # Extract Strengths section
    strengths_match = re.search(r"Strengths:\s*\n(.*?)(?=\n\s*(?:Areas to Improve|Improvements|Weaknesses|Missing Information|Unsupported Claims|Recommendations|One line verdict|Verdict):|\Z)", feedback_text, re.DOTALL | re.IGNORECASE)
    if strengths_match:
        lines = [line.strip().lstrip("-*• ") for line in strengths_match.group(1).strip().splitlines() if line.strip()]
        data["strengths"] = [l for l in lines if l]

    # Extract Areas to Improve / Weaknesses section
    improve_match = re.search(r"(?:Areas to Improve|Improvements|Weaknesses):\s*\n(.*?)(?=\n\s*(?:Missing Information|Unsupported Claims|Recommendations|One line verdict|Verdict):|\Z)", feedback_text, re.DOTALL | re.IGNORECASE)
    if improve_match:
        lines = [line.strip().lstrip("-*• ") for line in improve_match.group(1).strip().splitlines() if line.strip()]
        data["improvements"] = [l for l in lines if l]

    # Also pick up Missing Information, Unsupported Claims, Recommendations and merge into improvements
    for section_name in ["Missing Information", "Unsupported Claims", "Recommendations"]:
        section_match = re.search(
            rf"{section_name}:\s*\n(.*?)(?=\n\s*(?:Missing Information|Unsupported Claims|Recommendations|One line verdict|Verdict):|\Z)",
            feedback_text, re.DOTALL | re.IGNORECASE
        )
        if section_match:
            lines = [line.strip().lstrip("-*• ") for line in section_match.group(1).strip().splitlines() if line.strip()]
            meaningful = [l for l in lines if l and l.lower() not in ("none", "none identified", "n/a")]
            if meaningful:
                data["improvements"].append(f"**{section_name}:**")
                data["improvements"].extend(meaningful)

    # Extract Verdict
    verdict_match = re.search(r"(?:One line verdict|Verdict):\s*\n?(.*)", feedback_text, re.DOTALL | re.IGNORECASE)
    if verdict_match:
        data["verdict"] = verdict_match.group(1).strip()

    return data

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""

if "current_stage" not in st.session_state:
    st.session_state.current_stage = "idle"  # idle, search, reader, writer, critic, complete

if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
            <div style="background: #2563eb; color: white; width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold;">
                🔬
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #0f172a; line-height: 1.1;">ResearchAI</h2>
                <span style="font-size: 0.76rem; color: #64748b; font-weight: 600;">Multi-Agent Research Assistant</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # System Status Card
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Pipeline Status</span>
                <span class="status-badge"><span class="status-dot"></span> Ready</span>
            </div>
            <div style="font-size: 0.8rem; color: #334155;">
                4 Specialized Autonomous Agents
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # About the Application
    with st.expander("ℹ️ About the System", expanded=False):
        st.markdown(
            """
            **ResearchAI** coordinates a team of autonomous LangChain agents to conduct deep, structured academic & market research.
            
            Instead of a single LLM prompt, the system breaks research into four specialized agent stages: web discovery, targeted scraping, structured synthesis, and critical peer review.
            """
        )

    # Pipeline Workflow Guide
    with st.expander("🔄 Agent Pipeline Overview", expanded=True):
        st.markdown(
            """
            - **1. 🔍 Search Agent**  
              Retrieves recent, reliable web findings and citations via Tavily Search.
              
            - **2. 📖 Reader Agent**  
              Identifies top authoritative URLs and deeply scrapes technical content.
              
            - **3. ✍️ Writer Agent**  
              Synthesizes findings into a structured, publication-ready research report.
              
            - **4. 🧐 Critic Agent**  
              Rigorous evaluation reviewing clarity, evidence, and missing perspectives.
            """
        )

    st.markdown("---")

    # Session Research History
    st.markdown("<h4 style='font-size: 0.95rem; font-weight: 700; margin-bottom: 10px;'>📚 Research History</h4>", unsafe_allow_html=True)
    if st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history)):
            history_idx = len(st.session_state.history) - 1 - idx
            col1, col2 = st.columns([4, 1])
            with col1:
                topic_title = item["topic"]
                if len(topic_title) > 28:
                    topic_title = topic_title[:28] + "..."
                if st.button(f"📄 {topic_title}", key=f"hist_btn_{history_idx}", use_container_width=True):
                    st.session_state.current_result = item["result"]
                    st.session_state.current_topic = item["topic"]
                    st.session_state.current_stage = "complete"
                    st.rerun()
            with col2:
                st.caption(item["timestamp"])
        
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.session_state.current_result = None
            st.session_state.current_topic = ""
            st.session_state.current_stage = "idle"
            st.rerun()
    else:
        st.caption("No research sessions recorded yet.")

# Main Application Layout
st.markdown(
    """
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 style="font-size: 2.1rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.02em;">
                    AI Research Assistant
                </h1>
                <p style="font-size: 1rem; color: #64748b; margin: 4px 0 0 0; font-weight: 500;">
                    Research smarter with autonomous AI agents.
                </p>
            </div>
            <div>
                <div class="status-badge">
                    <span class="status-dot"></span> System Ready • Autonomous Pipeline Active
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Workflow Visualizer Function
def render_pipeline_tracker(active_stage="idle"):
    stages = [
        {"id": "search", "num": "1", "name": "Search Agent", "desc": "Information Discovery"},
        {"id": "reader", "num": "2", "name": "Reader Agent", "desc": "URL Extraction & Scraping"},
        {"id": "writer", "num": "3", "name": "Writer Agent", "desc": "Synthesis & Drafting"},
        {"id": "critic", "num": "4", "name": "Critic Agent", "desc": "Review & Fact Check"},
    ]

    stage_order = ["search", "reader", "writer", "critic", "complete"]
    current_idx = stage_order.index(active_stage) if active_stage in stage_order else -1

    html_parts = ['<div class="pipeline-container">']
    for idx, stage in enumerate(stages):
        if active_stage == "complete" or current_idx > idx:
            step_class = "pipeline-step completed"
            icon = "✓"
        elif active_stage == stage["id"]:
            step_class = "pipeline-step active"
            icon = stage["num"]
        else:
            step_class = "pipeline-step"
            icon = stage["num"]

        html_parts.append(f"""
            <div class="{step_class}">
                <div class="step-number">{icon}</div>
                <div class="step-info">
                    <span class="step-name">{stage["name"]}</span>
                    <span class="step-desc">{stage["desc"]}</span>
                </div>
            </div>
        """)
        if idx < len(stages) - 1:
            html_parts.append('<div class="pipeline-arrow">→</div>')

    html_parts.append("</div>")
    return "".join(html_parts)

# Pipeline Visualizer Placeholder
pipeline_placeholder = st.empty()
pipeline_placeholder.markdown(render_pipeline_tracker(st.session_state.current_stage), unsafe_allow_html=True)

# Research Input Section Card
with st.container():
    st.markdown(
        """
        <div class="saas-card" style="margin-bottom: 24px;">
            <div class="saas-card-header">
                <h3 class="saas-card-title">🔍 New Research Topic</h3>
                <span style="font-size: 0.8rem; color: #64748b;">Autonomous Multi-Agent Deep Search</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Input form
    topic_input = st.text_input(
        label="Topic",
        placeholder="Enter a research topic, e.g. Impact of Generative AI on Healthcare...",
        label_visibility="collapsed",
        key="topic_input",
    )

    language = st.selectbox(
        "Output language",
        options=["Auto", "Hindi", "English", "Hinglish"],
        index=0,
        help="The report and critic feedback will use this language.",
    )

    # Suggested topic chips
    col_chips, col_btn = st.columns([3, 1])
    with col_chips:
        st.markdown("<div style='font-size: 0.8rem; color: #64748b; margin-top: 4px; margin-bottom: 8px;'>Try an example topic:</div>", unsafe_allow_html=True)
        chip_cols = st.columns(4)
        sample_topics = [
            "Impact of Generative AI on Healthcare",
            "Quantum Computing in Cybersecurity",
            "Autonomous Vehicles & Smart Cities",
            "Nuclear Fusion Energy Breakthroughs",
        ]
        for c_idx, sample in enumerate(sample_topics):
            with chip_cols[c_idx]:
                short_sample = sample if len(sample) < 22 else sample[:20] + "…"
                st.button(
                    f"💡 {short_sample}",
                    key=f"chip_{c_idx}",
                    use_container_width=True,
                    on_click=select_topic,
                    args=(sample,),
                )

    with col_btn:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        start_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Handle Pipeline Execution
if start_button:
    clean_topic = st.session_state.topic_input.strip()
    if not clean_topic:
        st.error("⚠️ Please enter a research topic before starting.")
    else:
        st.session_state.current_topic = clean_topic
        st.session_state.current_stage = "search"
        pipeline_placeholder.markdown(render_pipeline_tracker("search"), unsafe_allow_html=True)

        # Progress & Status Container
        status_box = st.status(f"🔬 Autonomous Research in progress for: **{clean_topic}**", expanded=True)

        def step_callback(stage_id, message):
            st.session_state.current_stage = stage_id
            pipeline_placeholder.markdown(render_pipeline_tracker(stage_id), unsafe_allow_html=True)
            status_box.write(f"• **{message}**")

        try:
            from pipeline import run_research_pipeline

            # Execute pipeline with live status callback
            step_callback("search", "Search Agent: Querying web for recent and authoritative sources...")
            start_time = time.time()
            
            result = run_research_pipeline(
                clean_topic,
                on_step=step_callback,
                language=language,
            )
            elapsed_time = round(time.time() - start_time, 1)

            st.session_state.current_result = result
            st.session_state.current_stage = "complete"
            pipeline_placeholder.markdown(render_pipeline_tracker("complete"), unsafe_allow_html=True)

            # Record in session history
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.history.append({
                "topic": clean_topic,
                "timestamp": timestamp,
                "elapsed": f"{elapsed_time}s",
                "result": result,
            })

            status_box.update(
                label=f"✅ Research completed in {elapsed_time}s!",
                state="complete",
                expanded=False,
            )
            st.toast("Research pipeline finished successfully!", icon="🎉")
            st.rerun()

        except Exception as e:
            st.session_state.current_stage = "idle"
            pipeline_placeholder.markdown(render_pipeline_tracker("idle"), unsafe_allow_html=True)
            status_box.update(label="❌ Pipeline execution failed", state="error", expanded=True)
            st.error(f"**Error executing research pipeline:** {str(e)}")

# Display Research Results Section
if st.session_state.current_result is not None:
    res = st.session_state.current_result
    active_topic = st.session_state.current_topic

    # Header bar with Actions
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        st.markdown(
            f"""
            <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;">
                <h2 style="font-size: 1.4rem; font-weight: 700; color: #0f172a; margin: 0;">
                    Research Results: <span style="color: #2563eb;">{active_topic}</span>
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        col_clear, col_dl = st.columns([1, 1])
        with col_clear:
            if st.button("🧹 Clear", use_container_width=True, help="Clear active results"):
                st.session_state.current_result = None
                st.session_state.current_topic = ""
                st.session_state.current_stage = "idle"
                st.rerun()
        with col_dl:
            report_text = clean_content(res.get("report", ""))
            safe_slug = re.sub(r"[^\w\s-]", "", active_topic).strip().replace(" ", "_")[:30]
            st.download_button(
                label="📥 Export",
                data=report_text,
                file_name=f"Research_Report_{safe_slug}.md",
                mime="text/markdown",
                use_container_width=True,
                help="Download full research report as Markdown",
            )

    # Tabs for the four stages
    tab_report, tab_critic, tab_search, tab_scraped = st.tabs([
        "📄 Final Research Report",
        "🧐 Critic Review",
        "🔍 Search Results",
        "🌐 Scraped Content",
    ])

    # 1. FINAL RESEARCH REPORT TAB
    with tab_report:
        report_text = clean_content(res.get("report", ""))
        word_count = len(report_text.split())
        est_read_time = max(1, round(word_count / 200))

        st.markdown(
            f"""
            <div style="display: flex; gap: 16px; margin-bottom: 16px; font-size: 0.82rem; color: #64748b; background: #ffffff; padding: 10px 16px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <span>📊 <b>Words:</b> {word_count}</span>
                <span>⏱️ <b>Estimated Read:</b> ~{est_read_time} min</span>
                <span>🏷️ <b>Topic:</b> {active_topic}</span>
                <span>🤖 <b>Synthesized by:</b> Writer Agent</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="saas-card" style="padding: 32px; background: #ffffff;">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(report_text)
        st.markdown("</div>", unsafe_allow_html=True)

        # Quick download below report as well
        st.download_button(
            label="📥 Download Report (.md)",
            data=report_text,
            file_name=f"Research_Report_{safe_slug}.md",
            mime="text/markdown",
            key="btn_dl_bottom",
        )

    # 2. CRITIC REVIEW TAB
    with tab_critic:
        feedback_raw = clean_content(res.get("feedback", ""))
        critic_data = parse_critic_feedback(feedback_raw)

        # Score display if present
        if critic_data["score"]:
            st.markdown(
                f"""
                <div class="score-card">
                    <div class="score-value">{critic_data["score"]}</div>
                    <div class="score-label">Evaluation Score Assigned by Critic Chain</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Verdict callout if present
        if critic_data["verdict"]:
            st.markdown(
                f"""
                <div class="critic-section critic-verdict">
                    <strong style="color: #1e40af; display: block; margin-bottom: 4px;">⚖️ One Line Verdict</strong>
                    <span style="color: #1e293b; font-size: 0.95rem;">{critic_data["verdict"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Two-column layout for Strengths & Areas to Improve
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #065f46; margin-bottom: 10px;'>✅ Strengths</h4>", unsafe_allow_html=True)
            if critic_data["strengths"]:
                for item in critic_data["strengths"]:
                    st.markdown(
                        f"""
                        <div class="critic-section critic-strengths" style="margin-bottom: 8px; font-size: 0.88rem; color: #064e3b;">
                            • {item}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No specific strength bullet points identified.")

        with col_w:
            st.markdown("<h4 style='font-size: 1rem; font-weight: 700; color: #92400e; margin-bottom: 10px;'>⚠️ Areas to Improve</h4>", unsafe_allow_html=True)
            if critic_data["improvements"]:
                for item in critic_data["improvements"]:
                    st.markdown(
                        f"""
                        <div class="critic-section critic-improvements" style="margin-bottom: 8px; font-size: 0.88rem; color: #78350f;">
                            • {item}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No specific improvement points identified.")

        # Complete Unfiltered Feedback expander
        with st.expander("📝 View Full Uncut Critic Output", expanded=False):
            st.text(feedback_raw)

    # 3. SEARCH RESULTS TAB
    with tab_search:
        search_text = clean_content(res.get("search_results", ""))
        source_urls = extract_http_urls(search_text)
        st.markdown(
            """
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 16px;">
                Information discovered by the Search Agent using Tavily Web Search.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if source_urls:
            st.markdown("#### Open source pages")
            source_columns = st.columns(min(3, len(source_urls)))
            for index, source_url in enumerate(source_urls):
                with source_columns[index % len(source_columns)]:
                    st.link_button(
                        f"Open source {index + 1}",
                        source_url,
                        use_container_width=True,
                    )

        st.markdown(
            """
            <div class="saas-card">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(search_text)
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. SCRAPED CONTENT TAB
    with tab_scraped:
        scraped_text = clean_content(res.get("scraped_content", ""))
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 0.85rem; color: #64748b;">
                <span>Detailed technical content extracted by Reader Agent from selected high-priority URLs.</span>
                <span>Length: {len(scraped_text):,} chars</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="saas-card">
            """,
            unsafe_allow_html=True,
        )
        if scraped_text.strip():
            st.text_area(
                label="Scraped Content Details",
                value=scraped_text,
                height=420,
                label_visibility="collapsed",
            )
        else:
            st.info("No deeper scraped content was captured for this query.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Empty State when no research is loaded
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">🔬</div>
            <div class="empty-title">Ready for Your Next Investigation</div>
            <div class="empty-subtitle">
                Enter any scientific, business, or technology topic above. Four collaborative agents will autonomously gather web sources, scrape in-depth documents, write a structured report, and critique its rigor.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Feature Highlights Grid
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        st.markdown(
            """
            <div class="saas-card" style="padding: 16px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🔍</div>
                <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Broad Search</div>
                <div style="font-size: 0.78rem; color: #64748b;">Tavily-powered live web queries across authoritative publications.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col2:
        st.markdown(
            """
            <div class="saas-card" style="padding: 16px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">📖</div>
                <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Deep Scraping</div>
                <div style="font-size: 0.78rem; color: #64748b;">Automated extraction of dense article bodies bypassing navigation fluff.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col3:
        st.markdown(
            """
            <div class="saas-card" style="padding: 16px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">✍️</div>
                <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Structured Synthesis</div>
                <div style="font-size: 0.78rem; color: #64748b;">Professional reporting with introductions, findings, conclusions & sources.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col4:
        st.markdown(
            """
            <div class="saas-card" style="padding: 16px; text-align: center;">
                <div style="font-size: 1.5rem; margin-bottom: 8px;">🧐</div>
                <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;">Rigorous Critique</div>
                <div style="font-size: 0.78rem; color: #64748b;">Objective evaluation checking evidence, weaknesses, and citations.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
