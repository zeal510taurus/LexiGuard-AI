import streamlit as st
import sqlite3
import hashlib

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)""")

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login_system():
    st.sidebar.header("🔐 Auth")

    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Submit"):
        hashed = hash_password(password)

        if menu == "Signup":
            try:
                c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
                conn.commit()
                st.sidebar.success("Account created!")
            except:
                st.sidebar.error("User exists")

        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
            if c.fetchone():
                st.session_state.user = username
                st.sidebar.success(f"Welcome {username}")
            else:
                st.sidebar.error("Invalid login")

    return st.session_state.get("user", None)