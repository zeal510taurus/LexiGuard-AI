import streamlit as st
import datetime
import sqlite3
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt

# 1. Page Config
st.set_page_config(page_title="Smart Assistant Pro", page_icon="🤖", layout="wide")

# Database for Chat History
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS chats (user TEXT, role TEXT, message TEXT, ts DATETIME)")

# 2. Authentication
user = login_system()
if not user:
    st.info("Please login or signup in the sidebar to begin.")
    st.stop()

# 3. Initialize State
if "chat" not in st.session_state: st.session_state.chat = []
if "file_text" not in st.session_state: st.session_state.file_text = ""
if "usage" not in st.session_state: st.session_state.usage = 0
if "paid" not in st.session_state: st.session_state.paid = False

# 4. Sidebar Controls
with st.sidebar:
    st.divider()
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.chat = []
        st.session_state.file_text = ""
        st.rerun()

    # Paywall Logic
    if not st.session_state.paid:
        st.warning(f"Free Tier: {st.session_state.usage}/20 messages")
        code = st.text_input("Upgrade Code (Try PRO123)", type="password")
        if code == "PRO123":
            st.session_state.paid = True
            st.rerun()
    else:
        st.success("🌟 Pro Member")

# 5. Main UI - File Upload
st.title("💥 Smart Assistant Pro")
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])
if uploaded_file and not st.session_state.file_text:
    with st.spinner("Processing file..."):
        st.session_state.file_text = read_pdf(uploaded_file) if "pdf" in uploaded_file.type else read_txt(uploaded_file)
        st.toast("Document context loaded!")

# 6. Chat Display
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

# 7. Chat Input Logic
if prompt := st.chat_input("Ask me anything..."):
    # Check Usage Limit
    if not st.session_state.paid and st.session_state.usage >= 20:
        st.error("❌ Limit reached. Please upgrade.")
    else:
        # User message
        st.session_state.chat.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_context = f"Context: {st.session_state.file_text}\n\nUser: {prompt}" if st.session_state.file_text else prompt
                response = ask_ai(full_context)
                st.markdown(response)
        
        # Save state and database
        st.session_state.chat.append(("assistant", response))
        st.session_state.usage += 1
        
        now = datetime.datetime.now()
        c.execute("INSERT INTO chats VALUES (?, ?, ?, ?)", (user, "user", prompt, now))
        c.execute("INSERT INTO chats VALUES (?, ?, ?, ?)", (user, "assistant", response, now))
        conn.commit()