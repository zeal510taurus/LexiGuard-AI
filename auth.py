import streamlit as st
import sqlite3
import bcrypt

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    return conn, c

conn, c = get_db_connection()

# --- SECURITY UTILS ---
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# --- MAIN AUTH SYSTEM ---
def login_system():
    st.sidebar.header("🔐 Auth")

    # Handle Logged In State
    if "user" in st.session_state:
        st.sidebar.success(f"👋 Welcome {st.session_state.user}")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            del st.session_state["user"]
            st.rerun()
        return st.session_state.user

    # Tabs for Login/Signup
    tab1, tab2 = st.sidebar.tabs(["Login", "Signup"])

    with tab1:
        with st.form("login_form"):
            user_in = st.text_input("Username")
            pass_in = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                c.execute("SELECT password FROM users WHERE username=?", (user_in,))
                result = c.fetchone()
                if result and check_password(pass_in, result[0]):
                    st.session_state.user = user_in
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid credentials")

    with tab2:
        with st.form("signup_form"):
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create Account", use_container_width=True):
                if new_pass != confirm:
                    st.error("❌ Passwords do not match")
                elif len(new_pass) < 6:
                    st.error("❌ Password too short")
                elif new_user:
                    try:
                        hashed = hash_password(new_pass)
                        c.execute("INSERT INTO users VALUES (?, ?)", (new_user, hashed))
                        conn.commit()
                        st.success("✅ Created! Now Login.")
                    except sqlite3.IntegrityError:
                        st.error("❌ User exists")
    return None