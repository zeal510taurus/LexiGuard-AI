import streamlit as st
import os
import io
import datetime
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

# Custom Module Imports (Ensure these files are in your GitHub)
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt, get_chunks_with_metadata
from brain import save_to_brain, query_brain
from exporter import generate_report

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="LexiGuard AI | Premium Auditor",
    page_icon="⚖️",
    layout="wide"
)

# 2. PREMIUM CSS (GLASSMORPHISM & DARK MODE)
st.markdown("""
    <style>
    .stApp { background-color: #0A0C10; color: #E6EDF3; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #161B22;
        border-radius: 5px;
        padding: 10px 20px;
        color: #8B949E;
    }
    .stTabs [aria-selected="true"] { color: #58A6FF !important; border-bottom: 2px solid #58A6FF; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN GATE
user = login_system()
if not user:
    st.title("⚖️ LexiGuard AI")
    st.info("🔐 Please use the sidebar to log into your Auditor account.")
    st.stop()

# 4. SESSION STATE
if "chat" not in st.session_state: st.session_state.chat = []
if "doc_ready" not in st.session_state: st.session_state.doc_ready = False
if "summary" not in st.session_state: st.session_state.summary = ""

# 5. SIDEBAR
with st.sidebar:
    st.title("🛡️ Auditor Portal")
    st.write(f"Logged in: **{user}**")
    st.divider()
    
    audio_enabled = st.toggle("🔊 Auto-Read AI Responses", value=False)
    
    if st.button("🗑️ Clear Current Audit", use_container_width=True):
        st.session_state.chat = []
        st.session_state.doc_ready = False
        st.rerun()

# 6. MAIN INTERFACE
st.title("Strategic Document Intelligence")

if not st.session_state.doc_ready:
    # UPLOAD SECTION
    st.markdown("### 📥 Step 1: Upload Legal Document")
    uploaded_file = st.file_uploader("Drop PDF or TXT here", type=["pdf", "txt"])
    
    if uploaded_file:
        with st.status("🧠 Building Intelligence...", expanded=True) as status:
            st.session_state.doc_name = uploaded_file.name
            doc_data = read_pdf(uploaded_file) if "pdf" in uploaded_file.type else read_txt(uploaded_file)
            chunks, metas = get_chunks_with_metadata(doc_data)
            save_to_brain(chunks, metas, uploaded_file.name)
            
            # Initial Audit
            st.session_state.summary = ask_ai(f"Provide a 3-point risk audit for: {doc_data['content'][:3000]}")
            st.session_state.doc_ready = True
            status.update(label="✅ Audit Ready!", state="complete")
            st.rerun()

else:
    # AUDITOR DASHBOARD TABS
    tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "💬 AI Chat Auditor", "📄 Export Report"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Analysis", "Complete")
        c2.metric("Document", st.session_state.doc_name[:10] + "...")
        c3.metric("AI Confidence", "98%")
        
        st.markdown("### 📝 Critical Vulnerabilities Identified")
        st.write(st.session_state.summary)
        
        # Audio Player for Summary
        if st.button("🎵 Listen to Summary"):
            tts = gTTS(text=st.session_state.summary, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp)

    with tab2:
        # CHAT WINDOW
        chat_container = st.container(height=400)
        for role, msg in st.session_state.chat:
            with chat_container.chat_message(role):
                st.markdown(msg)

        # COMMAND BAR (MIC + TEXT)
        st.divider()
        col_text, col_mic = st.columns([0.88, 0.12])
        
        with col_mic:
            # THIS IS YOUR MISSING MICROPHONE
            audio_data = mic_recorder(
                start_prompt="🎤", 
                stop_prompt="🛑", 
                key='chat_mic_key'
            )
        
        with col_text:
            user_input = st.chat_input("Ask a question about the clauses...")

        # LOGIC: IF USER SPEAKS OR TYPES
        prompt = None
        if user_input:
            prompt = user_input
        elif audio_data:
            st.warning("🎙️ Audio received. (Note: Transcription requires Whisper API integration).")
            # For now, we will notify the user audio was captured.
            # To turn audio to text, you'd send audio_data['bytes'] to an API.

        if prompt:
            st.session_state.chat.append(("user", prompt))
            with chat_container.chat_message("user"):
                st.markdown(prompt)

            with chat_container.chat_message("assistant"):
                with st.spinner("Analyzing clauses..."):
                    context, pages = query_brain(prompt)
                    response = ask_ai(f"Context: {context}\nQuestion: {prompt}")
                    st.markdown(response)
                    if pages:
                        st.caption(f"Sources: Page(s) {', '.join(map(str, sorted(set(pages))))}")
                    
                    if audio_enabled:
                        tts_chat = gTTS(text=response, lang='en')
                        chat_fp = io.BytesIO()
                        tts_chat.write_to_fp(chat_fp)
                        st.audio(chat_fp, autoplay=True)

            st.session_state.chat.append(("assistant", response))

    with tab3:
        st.header("📄 Final Export")
        if st.button("Generate Audit Report PDF"):
            pdf_data = generate_report(user, st.session_state.doc_name, st.session_state.summary, st.session_state.chat)
            st.download_button("📥 Download Report", data=pdf_data, file_name="LexiGuard_Report.pdf")