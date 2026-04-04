import streamlit as st
from auth import login_system
from ai_module import ask_ai
from file_handler import read_pdf, read_txt
from voice import get_voice_input
import datetime

st.set_page_config(page_title="Smart Assistant Pro", page_icon="🤖", layout="wide")
st.title("💥 Smart Assistant Pro")

# Login
user = login_system()
if not user:
    st.stop()

# Initialize chat state
if "chat" not in st.session_state:
    st.session_state.chat = []
if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# Sidebar actions
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat = []
    st.session_state.file_text = ""

if st.sidebar.button("💾 Save Conversation"):
    filename = f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for role, msg in st.session_state.chat:
            f.write(f"{role.upper()}: {msg}\n\n")
    st.sidebar.success(f"Saved as {filename}")

if st.button("🎤 Record Voice"):
    voice_text = get_voice_input(duration=5)
    if voice_text:
        st.session_state.chat.append(("user", voice_text))
        response = ask_ai(voice_text)
        st.session_state.chat.append(("assistant", response))

# File upload
uploaded_file = st.file_uploader("📎 Upload Document", type=["pdf", "txt"])
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        st.session_state.file_text = read_pdf(uploaded_file)
    else:
        st.session_state.file_text = read_txt(uploaded_file)

# Chat input
user_input = st.chat_input("💬 Ask something...")
if user_input:
    st.session_state.chat.append(("user", user_input))
    prompt = f"{st.session_state.file_text}\n\nQuestion: {user_input}" if st.session_state.file_text else user_input
    response = ask_ai(prompt)
    st.session_state.chat.append(("assistant", response))

# Display chat
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)

if "paid" not in st.session_state:
    st.session_state.paid = False

if not st.session_state.paid:
    st.warning("🔒 Upgrade to Pro")
    st.markdown("[💳 Pay Here](https://buy.stripe.com/28E4gtfnX9Fm8DV2rAfUQ00)")

    code = st.text_input("Enter payment code")

    if code == "PRO123":  # temporary manual unlock
        st.session_state.paid = True
        st.success("Unlocked!")

    st.stop()

if "usage" not in st.session_state:
    st.session_state.usage = 0

st.session_state.usage += 1

if st.session_state.usage > 20:
    st.warning("Limit reached. Upgrade required.")
    st.stop()

c.execute("""CREATE TABLE IF NOT EXISTS chats (
    user TEXT,
    message TEXT
)""")

c.execute("INSERT INTO chats VALUES (?, ?)", (st.session_state.user, user_input))
conn.commit()

st.sidebar.success(f"👤 {st.session_state.user}")

with st.spinner("Thinking..."):
    response = ask_ai(prompt)

