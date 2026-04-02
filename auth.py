import streamlit as st

def login_system():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "login_clicked" not in st.session_state:
        st.session_state.login_clicked = False

    st.sidebar.header("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        st.session_state.login_clicked = True

    if st.session_state.login_clicked:
        if username == "ak47" and password == "1143":
            st.session_state.user = username
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Incorrect username/password")
        st.session_state.login_clicked = False

    return st.session_state.user