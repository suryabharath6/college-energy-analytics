# ---------------- LOGIN SYSTEM ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_login(username, password):

    users = st.secrets["users"]

    if username in users:
        return users[username] == hash_password(password)

    return False


# ---------------- INITIALIZE LOGIN STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.title("🔐 Campus Energy Analytics")

    st.subheader("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login", type="primary"):

        if check_login(username, password):

            # Save login state
            st.session_state.logged_in = True
            st.session_state.username = username

            # Record successful login
            log_activity(
                username,
                "Login successful"
            )

            st.rerun()

        else:

            # Record failed login
            log_activity(
                username,
                "Failed login attempt"
            )

            st.error("❌ Invalid username or password")

    st.stop()


# ---------------- LOGGED-IN USER ----------------

st.sidebar.success(
    f"👤 Logged in as: {st.session_state.username}"
)


# ---------------- LOGOUT ----------------

if st.sidebar.button("🚪 Logout"):

    log_activity(
        st.session_state.username,
        "Logout"
    )

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()
