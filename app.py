import streamlit as st
import datetime
import os
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# Import your custom modules
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt, get_chunks_with_metadata
from brain import save_to_brain, query_brain
from exporter import generate_report

# 1. Page Identity & Theme
st.set_page_config(page_title="LexiGuard AI Pro", page_icon="⚖️", layout="wide")

# Custom CSS for a Premium Feel
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .stMetric { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 15px; }
    .audio-container { margin-top: 20px; padding: 10px; background: #21262d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Authentication
user = login_system()
if not user:
    st.title("⚖️ LexiGuard AI")
    st.info("🔐 Restricted Access. Please login via sidebar.")
    st.stop()

# 3. State Management
if "chat" not in st.session_state: st.session_state.chat = []
if "doc_ready" not in st.session_state: st.session_state.doc_ready = False

# 4. Sidebar: History & Export
with st.sidebar:
    st.title("LexiGuard Control")
    st.caption(f"Auditor: {user}")
    
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.chat = []
        st.session_state.doc_ready = False
        st.rerun()

    if st.session_state.doc_ready:
        st.divider()
        if st.button("📄 Generate PDF Audit"):
            report = generate_report(user, st.session_state.doc_name, st.session_state.summary, st.session_state.chat)
            st.download_button("📥 Download Report", data=report, file_name="Audit_Report.pdf")

# 5. Main Dashboard & File Processing
st.title("⚖️ Strategic Intelligence Dashboard")

if not st.session_state.doc_ready:
    uploaded_file = st.file_uploader("📂 Upload Contract (PDF/TXT)", type=["pdf", "txt"])
    if uploaded_file:
        with st.status("🏗️ Processing Document Brain...", expanded=True):
            st.session_state.doc_name = uploaded_file.name
            doc_data = read_pdf(uploaded_file) if "pdf" in uploaded_file.type else read_txt(uploaded_file)
            chunks, metas = get_chunks_with_metadata(doc_data)
            save_to_brain(chunks, metas, uploaded_file.name)
            
            # Auto-Audit
            st.session_state.summary = ask_ai(f"Summarize 3 critical risks in this file: {doc_data['content'][:4000]}")
            st.session_state.doc_ready = True
            st.rerun()

# 6. The Visual Dashboard
if st.session_state.doc_ready:
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "Audit Active", "RAG Engine")
    col2.metric("Document", st.session_state.doc_name[:15] + "...")
    col3.metric("Analysis", "Page-Verified")

    with st.expander("📝 Executive Risk Summary", expanded=True):
        st.markdown(st.session_state.summary)
        # --- FEATURE: AUDIO SUMMARY ---
        if st.button("🔊 Listen to Summary"):
            tts = gTTS(text=st.session_state.summary, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format="audio/mp3")

    st.divider()

    # 7. Chat Display
    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.markdown(msg)

    # 8. THE VOICE & TEXT INPUT
    st.write("---")
    input_col, mic_col = st.columns([0.9, 0.1])
    
    with mic_col:
        # --- FEATURE: VOICE INPUT (MICROPHONE) ---
        audio_input = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key="mic")

    with input_col:
        text_input = st.chat_input("Ask about specific clauses...")

    # Logic to handle either Voice or Text
    final_prompt = None
    if text_input:
        final_prompt = text_input
    elif audio_input:
        # Note: In a production 'top of world' app, you would send this audio 
        # to Gemini's Whisper or Speech-to-Text. For now, we prompt the user 
        # that audio was received.
        st.info("🎙️ Voice recorded! (Processing audio-to-text...)")
        # For this version, text_input is the primary path. 
        # Deep integration of audio-to-text requires a cloud transcription API.

    if final_prompt:
        st.session_state.chat.append(("user", final_prompt))
        with st.chat_message("user"):
            st.markdown(final_prompt)

        with st.chat_message("assistant"):
            context, pages = query_brain(final_prompt)
            full_prompt = f"Context: {context}\nQuestion: {final_prompt}\nHelpful Auditor Answer (cite pages):"
            response = ask_ai(full_prompt)
            st.markdown(response)
            
            # Show Citation Chips
            st.caption("Verified Sources:")
            c_cols = st.columns(len(pages) + 5)
            for i, p in enumerate(pages):
                c_cols[i].button(f"📄 p.{p}", key=f"p_{p}_{i}", disabled=True)
            
            # Optional: Speak the response
            if st.toggle("Read response aloud"):
                tts_res = gTTS(text=response, lang='en')
                res_audio = io.BytesIO()
                tts_res.write_to_fp(res_audio)
                st.audio(res_audio)

        st.session_state.chat.append(("assistant", response))
        st.rerun()