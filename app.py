import streamlit as st
import joblib
import pandas as pd
import hashlib
import json
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="centered"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Sora', sans-serif;
        }

        .main {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
        }

        .auth-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 2.5rem;
            max-width: 440px;
            margin: 2rem auto;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 40px rgba(0,0,0,0.4);
        }

        .auth-title {
            font-size: 2rem;
            font-weight: 700;
            color: #ffffff;
            text-align: center;
            margin-bottom: 0.3rem;
        }

        .auth-subtitle {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.5);
            text-align: center;
            margin-bottom: 2rem;
        }

        .stTextInput > label {
            color: rgba(255,255,255,0.75) !important;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .stTextInput > div > div > input {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.6rem 1rem !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: #a78bfa !important;
            box-shadow: 0 0 0 2px rgba(167,139,250,0.25) !important;
        }

        div.stButton > button {
            width: 100%;
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            color: white;
            border: none;
            padding: 0.7rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 0.5rem;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #6d28d9, #8b5cf6);
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(124,58,237,0.5);
        }

        .divider {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 1.2rem 0;
            color: rgba(255,255,255,0.3);
            font-size: 0.8rem;
        }

        .divider::before, .divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255,255,255,0.12);
        }

        .switch-link {
            text-align: center;
            color: rgba(255,255,255,0.5);
            font-size: 0.88rem;
            margin-top: 1rem;
        }

        .badge-success {
            background: rgba(52,211,153,0.15);
            border: 1px solid rgba(52,211,153,0.3);
            color: #34d399;
            padding: 0.4rem 0.9rem;
            border-radius: 30px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }

        .score-box {
            background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(167,139,250,0.1));
            border: 1px solid rgba(167,139,250,0.4);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            margin-top: 1rem;
        }

        .score-number {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa, #f0abfc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .welcome-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# USER STORE (JSON file)
# =========================
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = hash_password(password)
    save_users(users)
    return True, "Account created successfully!"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if users[username] != hash_password(password):
        return False, "Incorrect password."
    return True, "Login successful!"

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # "login" or "signup"

# =========================
# AUTH PAGES
# =========================
def show_login():
    st.markdown('<div class="auth-title">Welcome Back 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Sign in to access your predictor</div>', unsafe_allow_html=True)

    username = st.text_input("Username", key="login_user", placeholder="Enter your username")
    password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

    if st.button("Sign In", key="login_btn"):
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            ok, msg = login_user(username, password)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">Don\'t have an account?</div>', unsafe_allow_html=True)

    if st.button("Create an Account →", key="go_signup"):
        st.session_state.auth_mode = "signup"
        st.rerun()


def show_signup():
    st.markdown('<div class="auth-title">Create Account 🎓</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Join and start predicting your scores</div>', unsafe_allow_html=True)

    username = st.text_input("Choose a Username", key="signup_user", placeholder="e.g. student_raj")
    password = st.text_input("Create Password", type="password", key="signup_pass", placeholder="At least 6 characters")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Re-enter password")

    if st.button("Sign Up", key="signup_btn"):
        if not username or not password or not confirm:
            st.error("Please fill in all fields.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            ok, msg = register_user(username, password)
            if ok:
                st.success(msg + " Please log in.")
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.error(msg)

    st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">Already have an account?</div>', unsafe_allow_html=True)

    if st.button("← Back to Login", key="go_login"):
        st.session_state.auth_mode = "login"
        st.rerun()


# =========================
# MAIN PREDICTOR PAGE
# =========================
def show_predictor():
    # Header with user info + logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 🎓 Student Score Predictor")
        st.markdown(f'<span class="badge-success">✓ {st.session_state.username}</span>', unsafe_allow_html=True)
    with col2:
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.markdown("---")

    # Load model
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
    except Exception as e:
        st.error(f"⚠️ Model files not found: {e}")
        st.info("Make sure `student_model.pkl` and `model_columns.pkl` are in the same directory.")
        return

    # Input fields
    st.markdown("#### 📋 Student Information")
    col1, col2 = st.columns(2)

    with col1:
        hours = st.number_input("Hours Studied", 0.0, 24.0, step=0.5)
        attendance = st.number_input("Attendance (%)", 0.0, 100.0, step=1.0)
        previous = st.number_input("Previous Score", 0.0, 100.0, step=1.0)
        sleep = st.number_input("Sleep Hours", 0.0, 12.0, step=0.5)
        motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
        teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
        school = st.selectbox("School Type", ["Public", "Private"])

    with col2:
        internet = st.selectbox("Internet Access", ["Yes", "No"])
        income = st.selectbox("Family Income", ["Low", "Medium", "High"])
        parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
        education = st.selectbox("Parent Education", ["School", "College"])
        peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
        resources = st.selectbox("Learning Resources", ["Low", "Medium", "High"])
        activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])

    st.markdown("")
    if st.button("🔮 Predict Score"):
        data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Sleep_Hours": sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet,
            "Family_Income": income,
            "Parental_Involvement": parent,
            "Parental_Education_Level": education,
            "Peer_Influence": peer,
            "Learning_Resources": resources,
            "Extracurricular_Activities": activities
        }

        input_df = pd.DataFrame([data])
        input_df = pd.get_dummies(input_df)
        input_df = input_df.reindex(columns=columns, fill_value=0)

        prediction = model.predict(input_df)
        final_score = max(40, min(100, prediction[0]))
        final_score = int(round(final_score))

        # Grade label
        if final_score >= 90:
            grade, emoji = "A+", "🏆"
        elif final_score >= 80:
            grade, emoji = "A", "🥇"
        elif final_score >= 70:
            grade, emoji = "B", "🎯"
        elif final_score >= 60:
            grade, emoji = "C", "📘"
        else:
            grade, emoji = "D", "📖"

        st.markdown(f"""
        <div class="score-box">
            <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 0.3rem;">Predicted Exam Score</div>
            <div class="score-number">{final_score}</div>
            <div style="color: rgba(255,255,255,0.5); font-size: 1rem; margin-top: 0.3rem;">{emoji} Grade: {grade}</div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# ROUTING
# =========================
if st.session_state.logged_in:
    show_predictor()
else:
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    if st.session_state.auth_mode == "login":
        show_login()
    else:
        show_signup()
    st.markdown('</div>', unsafe_allow_html=True)
