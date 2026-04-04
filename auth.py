def login_system():
    st.sidebar.header("🔐 Auth")

    # ✅ Already logged in
    if "user" in st.session_state:
        st.sidebar.success(f"👋 Welcome {st.session_state.user}")

        if st.sidebar.button("🚪 Logout"):
            del st.session_state["user"]
            st.rerun()

        return st.session_state.user

    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    # 🔥 FORM START
    with st.sidebar.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submit = st.form_submit_button("Submit")  # ✅ Enter works here

    # 🔥 FORM SUBMIT LOGIC
    if submit:
        if not username or not password:
            st.sidebar.warning("Enter username & password")
            return None

        hashed = hash_password(password)

        if menu == "Signup":
            try:
                c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
                conn.commit()
                st.sidebar.success("✅ Account created!")
            except:
                st.sidebar.error("❌ User already exists")

        else:
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, hashed)
            )

            if c.fetchone():
                st.session_state.user = username
                st.sidebar.success(f"✅ Welcome {username}")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid login")

    return None