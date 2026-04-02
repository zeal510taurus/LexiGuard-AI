import streamlit as st
from ai_module import ask_ai
from file_handler import read_pdf, read_txt
import datetime

st.set_page_config(page_title="Smart Assistant", page_icon="🤖", layout="wide")

st.title("💥 Smart Assistant Pro")

# ------------------ MEMORY ------------------ #
if "chat" not in st.session_state:
    st.session_state.chat = []

# ------------------ SIDEBAR ------------------ #
st.sidebar.header("⚙ Controls")

if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat = []

save_chat = st.sidebar.button("💾 Save Conversation")

# ------------------ FILE UPLOAD ------------------ #
prompt = f"""
Analyze this document like an expert.

Provide:
1. Summary
2. Key insights
3. Important points
4. Risks or warnings (if any)

Document:
{st.session_state.file_text[:4000]}
"""

# ------------------ SAVE CHAT ------------------ #
if save_chat:
    filename = f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for role, msg in st.session_state.chat:
            f.write(f"{role.upper()}: {msg}\n\n")
    st.sidebar.success(f"Saved as {filename}")

# ------------------ ASSISTANT LOGIC ------------------ #
def smart_assistant(user_input):
    st.session_state.chat.append(("user", user_input))

    try:
        prompt = build_prompt(user_input)
        response = ask_ai(prompt)
    except Exception as e:
        response = f"Error: {str(e)}"

    st.session_state.chat.append(("assistant", response))

# ------------------ INPUT ------------------ #
user_input = st.chat_input("Type your message...")

if user_input:
    smart_assistant(user_input)

# ------------------ DISPLAY ------------------ #
for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(msg)