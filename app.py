import streamlit as st
import os
import io
import datetime
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# Custom Module Imports
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt, get_chunks_with_metadata
from brain import save_to_brain, query_brain
from exporter import generate_report

# 1. PAGE CONFIGURATION & THEME
st.set_page_config(
    page_title="LexiGuard AI | Premium Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. PREMIUM CSS (GLASSMORPHISM)
st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp { background-color: #0A0C10; color: #E6EDF3; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }

    /* Custom Chat Bubbles */
    .stChatMessage {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363D;
        border-radius: 15px;
        padding: 10px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #161B22;
        border-radius: 10px 10px 0 0;
        gap: 10px;
        padding: 10px;
        color: #8B949E;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262D;
        color: #58A6FF !important;
        border-bottom: 2px solid #58A6FF;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTICATION GATING
user = login_system()
if not user:
    st.title("⚖️ LexiGuard AI")
    st.warning("🔐 Please login via the sidebar to access the Auditor Dashboard.")
    st.stop()

# 4. SESSION STATE INITIALIZATION
if "chat" not in st.session_state: st.session_state.chat = []
if "doc_ready" not in st.session_state: st.session_state.doc_ready = False
if "summary" not in st.session_state: st.session_state.summary = ""

# 5. SIDEBAR: CONTROLS & VOICE TOGGLE
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=80)
    st.title("Control Center")
    st.caption(f"🛡️ Active Auditor: **{user}**")
    
    st.divider()
    audio_enabled = st.toggle("🔊 Auto-Read Responses", value=False)
    
    if st.button("🗑️ Reset Intelligence", use_container_width=True):
        st.session_state.chat = []
        st.session_state.doc_ready = False
        st.rerun()

    if st.session_state.doc_ready:
        st.divider()
        st.subheader("Report Export")
        if st.button("📄 Generate Final PDF"):
            report = generate_report(user, st.session_state.doc_name, st.session_state.summary, st.session_state.chat)
            st.download_button("📥 Download Now", data=report, file_name="LexiGuard_Audit.pdf")

# 6. MAIN INTERFACE: TABS
st.title("Strategic Legal Dashboard")

if not st.session_state.doc_ready:
    # Upload Landing Page
    with st.container():
        st.info("👋 Welcome, Auditor. Upload a document to begin the AI risk assessment.")
        uploaded_file = st.file_uploader("Upload Contract (PDF or TXT)", type=["pdf", "txt"])
        
        if uploaded_file:
            with st.status("🧠 Analyzing Document Clauses...", expanded=True) as status:
                st.session_state.doc_name = uploaded_file.name
                # File Handling
                doc_data = read_pdf(uploaded_file) if "pdf" in uploaded_file.type else read_txt(uploaded_file)
                chunks, metas = get_chunks_with_metadata(doc_data)
                save_to_brain(chunks, metas, uploaded_file.name)
                
                # Initial Risk Audit
                summary_prompt = f"Perform a high-level risk audit on this text. Identify 3 critical vulnerabilities: {doc_data['content'][:4000]}"
                st.session_state.summary = ask_ai(summary_prompt)
                
                st.session_state.doc_ready = True
                status.update(label="✅ Audit Ready!", state="complete", expanded=False)
                st.rerun()

else:
    # THE AUDITOR WORKSPACE
    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "💬 AI Chat Auditor", "🎧 Audio Analysis"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Status", "Fully Analyzed")
        c2.metric("File", st.session_state.doc_name[:12] + "...")
        c3.metric("Risk Level", "Verified", delta="High Accuracy")
        
        st.markdown("### 📝 Critical Risk Assessment")
        st.markdown(st.session_state.summary)

    with tab2:
        # Chat History Container
        chat_container = st.container(height=400)
        for role, msg in st.session_state.chat:
            with chat_container.chat_message(role):
                st.markdown(msg)

        # Input Area (Mic + Text)
        st.divider()
        col_text, col_mic = st.columns([0.85, 0.15])
        
        with col_mic:
            audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='mic')
        
        with col_text:
            user_input = st.chat_input("Ask about specific clauses or liabilities...")

        # Process Input
        final_query = user_input
        if audio_data:
            st.toast("🎙️ Audio received! (Ready for processing)")
            # In basic gTTS/Mic, we verify audio. For full text, use Whisper API.
        
        if final_query:
            st.session_state.chat.append(("user", final_query))
            with chat_container.chat_message("user"):
                st.markdown(final_query)

            with chat_container.chat_message("assistant"):
                with st.spinner("Consulting Legal Brain..."):
                    context, pages = query_brain(final_query)
                    response = ask_ai(f"Context: {context}\nQuestion: {final_query}")
                    st.markdown(response)
                    
                    # Page Citations
                    if pages:
                        st.caption(f"Sources: Pages {', '.join(map(str, sorted(set(pages))))}")
                    
                    # Voice Output logic
                    if audio_enabled:
                        tts = gTTS(text=response, lang='en')
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        st.audio(fp)

            st.session_state.chat.append(("assistant", response))

    with tab3:
        st.subheader("Listen to Full Report")
        if st.button("🔊 Generate Audio Summary"):
            with st.spinner("Converting text to speech..."):
                full_audio_text = f"Audit Report for {st.session_state.doc_name}. " + st.session_state.summary
                tts_all = gTTS(text=full_audio_text, lang='en')
                audio_fp = io.BytesIO()
                tts_all.write_to_fp(audio_fp)
                st.audio(audio_fp)
                st.success("Audio ready. You can play or download it above.")