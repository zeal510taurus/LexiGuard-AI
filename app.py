import streamlit as st
import datetime
import sqlite3
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt

# 1. Page Config & Setup
st.set_page_config(page_title="Smart Assistant Pro", page_icon="🤖", layout="wide")

# Database Connection (Using a context manager is safer)
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chats (user TEXT, role TEXT, message TEXT, timestamp DATETIME)")

# 2. Authentication
user = login_system()
if not user:
    st.info("Please login via the sidebar to continue.")
    st.stop()

# 3. Initialize Session State
if "chat" not in st.session_state:
    st.session_state.chat = []
if "file_text" not in st.session_state:
    st.session_state.file_text = ""
if "usage" not in st.session_state:
    st.session_state.usage = 0
if "paid" not in st.session_state:
    st.session_state.paid = False

# 4. Sidebar - User Info & Controls
with st.sidebar:
    st.divider()
    st.subheader(f"👤 {user}")
    
    col1, col2 = st.columns(2)
    if col1.button("🧹 Clear", use_container_width=True):
        st.session_state.chat = []
        st.session_state.file_text = ""
        st.rerun()

    if col2.button("💾 Save", use_container_width=True):
        history = "\n".join([f"{r.upper()}: {m}" for r, m in st.session_state.chat])
        st.download_button("Download TXT", history, file_name=f"chat_{user}_{datetime.datetime.now().strftime('%H%M')}.txt")

    # Paywall Logic
    if not st.session_state.paid:
        st.warning("🔒 Free Tier")
        st.progress(st.session_state.usage / 20, text=f"Usage: {st.session_state.usage}/20")
        
        with st.expander("Upgrade to Pro"):
            st.markdown("[💳 Click here to Pay](https://buy.stripe.com/example)")
            code = st.text_input("Enter License Code", type="password")
            if code == "PRO123":
                st.session_state.paid = True
                st.success("Unlocked! Rerunning...")
                st.rerun()
    else:
        st.success("🌟 Pro Account Active")

# 5. File Upload Logic
uploaded_file = st.file_uploader("📎 Upload Document for Context", type=["pdf", "txt"])
if uploaded_file and not st.session_state.file_text: # Process only once
    with st.spinner("Reading file..."):
        if uploaded_file.type == "application/pdf":
            st.session_state.file_text = read_pdf(uploaded_file)
        else:
            st.session_state.file_text = read_txt(uploaded_file)
    st.toast("File uploaded successfully!")

# 6. Chat Display
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

# 7. Chat Input & Processing
if prompt := st.chat_input("💬 Ask something..."):
    # Check Limits
    if not st.session_state.paid and st.session_state.usage >= 20:
        st.error("❌ Limit reached. Please upgrade to Pro to continue.")
    else:
        # Add User Message
        st.session_state.chat.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = f"Context: {st.session_state.file_text}\n\nUser: {prompt}" if st.session_state.file_text else prompt
                response = ask_ai(