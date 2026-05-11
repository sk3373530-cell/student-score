import streamlit as st
import joblib
import pandas as pd
import hashlib
import json
import os
from datetime import datetime
import plotly.graph_objects as go

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

        .auth-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 20px; padding: 2.5rem;
            max-width: 440px; margin: 2rem auto;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 40px rgba(0,0,0,0.4);
        }
        .auth-title  { font-size:2rem; font-weight:700; color:#fff; text-align:center; margin-bottom:.3rem; }
        .auth-subtitle { font-size:.9rem; color:rgba(255,255,255,.5); text-align:center; margin-bottom:2rem; }
        .stTextInput>label { color:rgba(255,255,255,.75)!important; font-size:.85rem; font-weight:600; }
        .stTextInput>div>div>input {
            background:rgba(255,255,255,.07)!important;
            border:1px solid rgba(255,255,255,.15)!important;
            color:white!important; border-radius:10px!important; padding:.6rem 1rem!important;
        }
        div.stButton>button {
            width:100%; background:linear-gradient(135deg,#7c3aed,#a78bfa);
            color:white; border:none; padding:.7rem 1.5rem; font-size:1rem;
            font-weight:600; border-radius:10px; cursor:pointer; transition:all .3s ease; margin-top:.5rem;
        }
        div.stButton>button:hover {
            background:linear-gradient(135deg,#6d28d9,#8b5cf6);
            transform:translateY(-1px); box-shadow:0 6px 20px rgba(124,58,237,.5);
        }
        .divider { display:flex; align-items:center; gap:.8rem; margin:1.2rem 0; color:rgba(255,255,255,.3); font-size:.8rem; }
        .divider::before,.divider::after { content:''; flex:1; height:1px; background:rgba(255,255,255,.12); }
        .switch-link { text-align:center; color:rgba(255,255,255,.5); font-size:.88rem; margin-top:1rem; }
        .badge-success {
            background:rgba(52,211,153,.15); border:1px solid rgba(52,211,153,.3);
            color:#34d399; padding:.4rem .9rem; border-radius:30px; font-size:.8rem; font-weight:600; display:inline-block;
        }
        .score-box {
            background:linear-gradient(135deg,rgba(124,58,237,.2),rgba(167,139,250,.1));
            border:1px solid rgba(167,139,250,.4); border-radius:16px;
            padding:1.5rem; text-align:center; margin-top:1rem;
        }
        .score-number {
            font-size:3.5rem; font-weight:700;
            background:linear-gradient(135deg,#a78bfa,#f0abfc);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        }
        .stat-card {
            background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08);
            border-radius:14px; padding:1.2rem 1.4rem; text-align:center;
        }
        .stat-label { color:rgba(255,255,255,.45); font-size:.78rem; font-weight:600; letter-spacing:.06em; text-transform:uppercase; margin-bottom:.4rem; }
        .stat-value { font-size:1.9rem; font-weight:700; color:#a78bfa; }
        .tip-card {
            background:rgba(167,139,250,.08); border-left:3px solid #a78bfa;
            border-radius:0 10px 10px 0; padding:.8rem 1.1rem;
            margin-bottom:.6rem; color:rgba(255,255,255,.8); font-size:.88rem;
        }
        .trend-up   { color:#34d399; font-weight:700; }
        .trend-down { color:#f87171; font-weight:700; }
        .trend-flat { color:#facc15; font-weight:700; }
        .history-row {
            display:flex; justify-content:space-between; align-items:center;
            padding:.65rem 1rem; border-radius:10px; margin-bottom:.4rem;
            background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.06);
            font-size:.86rem; color:rgba(255,255,255,.75);
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# DATA FILES
# =========================
USERS_FILE   = "users.json"
HISTORY_FILE = "history.json"

def load_users():
    if not os.path.exists(USERS_FILE): return {}
    with open(USERS_FILE) as f: return json.load(f)

def save_users(u):
    with open(USERS_FILE,"w") as f: json.dump(u,f)

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def register_user(username, password):
    u = load_users()
    if username in u: return False, "Username already exists."
    u[username] = hash_password(password); save_users(u)
    return True, "Account created!"

def login_user(username, password):
    u = load_users()
    if username not in u: return False, "Username not found."
    if u[username] != hash_password(password): return False, "Incorrect password."
    return True, "Login successful!"

def load_history():
    if not os.path.exists(HISTORY_FILE): return {}
    with open(HISTORY_FILE) as f: return json.load(f)

def save_history(h):
    with open(HISTORY_FILE,"w") as f: json.dump(h,f)

def append_prediction(username, score, inputs):
    h = load_history()
    if username not in h: h[username] = []
    h[username].append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "score": score, **inputs})
    save_history(h)

def get_user_history(username):
    return load_history().get(username, [])

# =========================
# HELPERS
# =========================
for k,v in [("logged_in",False),("username",""),("auth_mode","login")]:
    if k not in st.session_state: st.session_state[k]=v

def grade_info(s):
    if s>=90: return "A+","🏆","#34d399"
    if s>=80: return "A","🥇","#a78bfa"
    if s>=70: return "B","🎯","#60a5fa"
    if s>=60: return "C","📘","#facc15"
    return "D","📖","#f87171"

# =========================
# AUTH
# =========================
def show_login():
    st.markdown('<div class="auth-title">Welcome Back 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Sign in to access your predictor</div>', unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user", placeholder="Your username")
    password = st.text_input("Password", type="password", key="login_pass", placeholder="Your password")
    if st.button("Sign In", key="login_btn"):
        if not username or not password: st.error("Fill in all fields.")
        else:
            ok,msg = login_user(username,password)
            if ok:
                st.session_state.logged_in=True; st.session_state.username=username; st.rerun()
            else: st.error(msg)
    st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">No account yet?</div>', unsafe_allow_html=True)
    if st.button("Create an Account →", key="go_signup"):
        st.session_state.auth_mode="signup"; st.rerun()

def show_signup():
    st.markdown('<div class="auth-title">Create Account 🎓</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-subtitle">Join and start predicting scores</div>', unsafe_allow_html=True)
    username = st.text_input("Username", key="signup_user", placeholder="e.g. student_raj")
    password = st.text_input("Password", type="password", key="signup_pass", placeholder="Min 6 characters")
    confirm  = st.text_input("Confirm Password", type="password", key="signup_confirm")
    if st.button("Sign Up", key="signup_btn"):
        if not username or not password or not confirm: st.error("Fill in all fields.")
        elif len(password)<6: st.error("Password must be ≥ 6 characters.")
        elif password!=confirm: st.error("Passwords don't match.")
        else:
            ok,msg = register_user(username,password)
            if ok:
                st.success(msg+" Please log in."); st.session_state.auth_mode="login"; st.rerun()
            else: st.error(msg)
    st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)
    st.markdown('<div class="switch-link">Already have an account?</div>', unsafe_allow_html=True)
    if st.button("← Back to Login", key="go_login"):
        st.session_state.auth_mode="login"; st.rerun()

# =========================
# PREDICTOR TAB
# =========================
def show_predictor(model, columns):
    st.markdown("#### 📋 Student Information")
    c1,c2 = st.columns(2)
    with c1:
        hours      = st.number_input("Hours Studied",  0.0,24.0, step=0.5)
        attendance = st.number_input("Attendance (%)", 0.0,100.0,step=1.0)
        previous   = st.number_input("Previous Score", 0.0,100.0,step=1.0)
        sleep      = st.number_input("Sleep Hours",    0.0,12.0, step=0.5)
        motivation = st.selectbox("Motivation Level",  ["Low","Medium","High"])
        teacher    = st.selectbox("Teacher Quality",   ["Poor","Average","Good"])
        school     = st.selectbox("School Type",       ["Public","Private"])
    with c2:
        internet   = st.selectbox("Internet Access",           ["Yes","No"])
        income     = st.selectbox("Family Income",             ["Low","Medium","High"])
        parent     = st.selectbox("Parental Involvement",      ["Low","Medium","High"])
        education  = st.selectbox("Parent Education",          ["School","College"])
        peer       = st.selectbox("Peer Influence",            ["Negative","Neutral","Positive"])
        resources  = st.selectbox("Learning Resources",        ["Low","Medium","High"])
        activities = st.selectbox("Extracurricular Activities",["Yes","No"])

    st.markdown("")
    if st.button("🔮 Predict Score"):
        inputs = {
            "Hours_Studied":hours,"Attendance":attendance,"Previous_Scores":previous,
            "Sleep_Hours":sleep,"Motivation_Level":motivation,"Teacher_Quality":teacher,
            "School_Type":school,"Internet_Access":internet,"Family_Income":income,
            "Parental_Involvement":parent,"Parental_Education_Level":education,
            "Peer_Influence":peer,"Learning_Resources":resources,"Extracurricular_Activities":activities
        }
        df = pd.DataFrame([inputs])
        df = pd.get_dummies(df)
        df = df.reindex(columns=columns, fill_value=0)
        raw   = model.predict(df)[0]
        score = int(round(max(40,min(100,raw))))
        grade,emoji,color = grade_info(score)
        append_prediction(st.session_state.username, score, inputs)

        st.markdown(f"""
        <div class="score-box">
            <div style="color:rgba(255,255,255,.6);font-size:.9rem;margin-bottom:.3rem;">Predicted Exam Score</div>
            <div class="score-number">{score}</div>
            <div style="color:{color};font-size:1.1rem;margin-top:.3rem;">{emoji} Grade: {grade}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 💡 Instant Improvement Tips")
        tips=[]
        if hours<4:       tips.append("📚 Study at least 4–6 hours/day — strongest predictor of score.")
        if attendance<75: tips.append("🏫 Attendance below 75% significantly hurts performance. Aim for 90%+.")
        if sleep<6:       tips.append("😴 Too little sleep. 7–8 hours boosts retention and focus.")
        if motivation=="Low":      tips.append("🔥 Low motivation — set small daily goals to build momentum.")
        if peer=="Negative":       tips.append("👥 Negative peer influence drags scores. Consider study groups.")
        if resources=="Low":       tips.append("📖 Explore more resources — YouTube, NCERT, Khan Academy.")
        if not tips: tips.append("✅ You're doing great! Stay consistent to maintain your score.")
        for t in tips:
            st.markdown(f'<div class="tip-card">{t}</div>', unsafe_allow_html=True)

# =========================
# PROGRESS TAB
# =========================
def show_progress():
    history = get_user_history(st.session_state.username)
    if not history:
        st.info("📭 No predictions yet. Head to **🔮 Predictor** to make your first prediction!")
        return

    df     = pd.DataFrame(history)
    df["attempt"] = range(1, len(df)+1)
    scores = df["score"].tolist()

    best   = max(scores)
    worst  = min(scores)
    avg    = round(sum(scores)/len(scores),1)
    latest = scores[-1]
    trend  = scores[-1]-scores[-2] if len(scores)>=2 else 0
    trend_html = (
        f'<span class="trend-up">▲ +{trend} from last attempt</span>'  if trend>0 else
        f'<span class="trend-down">▼ {trend} from last attempt</span>' if trend<0 else
        f'<span class="trend-flat">→ No change from last attempt</span>'
    )

    # ── Stat Cards ──
    c1,c2,c3,c4 = st.columns(4)
    for col,label,val in [(c1,"Latest Score",latest),(c2,"Best Score",best),(c3,"Average Score",avg),(c4,"Total Attempts",len(scores))]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value">{val}</div></div>', unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:right;margin-top:.5rem;font-size:.83rem;color:rgba(255,255,255,.45);'>{trend_html}</div>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Score Trend Line ──
    st.markdown("##### 📈 Score Trend Over Time")
    grade_colors = [grade_info(s)[2] for s in scores]
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df["attempt"], y=df["score"], mode="lines+markers",
        line=dict(color="#a78bfa",width=3),
        marker=dict(size=10, color=grade_colors, line=dict(color="white",width=2)),
        hovertemplate="Attempt %{x}<br>Score: %{y}<extra></extra>"
    ))
    fig_line.add_hline(y=avg, line_dash="dot", line_color="rgba(255,255,255,.25)",
                       annotation_text=f"Avg {avg}", annotation_font_color="rgba(255,255,255,.4)")
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,.7)",
        xaxis=dict(title="Attempt #", gridcolor="rgba(255,255,255,.05)", tickmode="linear"),
        yaxis=dict(title="Score", range=[35,105], gridcolor="rgba(255,255,255,.05)"),
        margin=dict(l=10,r=10,t=10,b=10), height=300
    )
    st.plotly_chart(fig_line, use_container_width=True)

    left, right = st.columns(2)

    # ── Grade Distribution Pie ──
    with left:
        st.markdown("##### 🏅 Grade Distribution")
        gcnt={"A+":0,"A":0,"B":0,"C":0,"D":0}
        for s in scores:
            g,_,_ = grade_info(s); gcnt[g]+=1
        gcnt = {k:v for k,v in gcnt.items() if v>0}
        cmap = {"A+":"#34d399","A":"#a78bfa","B":"#60a5fa","C":"#facc15","D":"#f87171"}
        fig_pie = go.Figure(go.Pie(
            labels=list(gcnt.keys()), values=list(gcnt.values()),
            marker_colors=[cmap[g] for g in gcnt],
            hole=0.45, textfont_size=13,
            hovertemplate="%{label}: %{value} attempt(s)<extra></extra>"
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="rgba(255,255,255,.75)",
            margin=dict(l=10,r=10,t=10,b=10), height=280,
            legend=dict(orientation="h",y=-0.1)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Radar — latest attempt factors ──
    with right:
        st.markdown("##### 🔍 Factor Snapshot (Latest)")
        last = df.iloc[-1]
        norms = {
            "Study Hours":  (float(last.get("Hours_Studied",0))/24)*100,
            "Attendance":   float(last.get("Attendance",0)),
            "Prev Score":   float(last.get("Previous_Scores",0)),
            "Sleep":        (float(last.get("Sleep_Hours",0))/12)*100,
        }
        cats = list(norms.keys())+[list(norms.keys())[0]]
        vals = list(norms.values())+[list(norms.values())[0]]
        fig_r = go.Figure(go.Scatterpolar(
            r=vals, theta=cats, fill="toself",
            fillcolor="rgba(167,139,250,.15)",
            line=dict(color="#a78bfa",width=2),
            marker=dict(size=6,color="#a78bfa")
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(255,255,255,.08)",tickfont_color="rgba(255,255,255,.35)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,.08)",tickfont_color="rgba(255,255,255,.7)")
            ),
            paper_bgcolor="rgba(0,0,0,0)", font_color="rgba(255,255,255,.7)",
            margin=dict(l=40,r=40,t=20,b=20), height=280
        )
        st.plotly_chart(fig_r, use_container_width=True)

    # ── Improvement Bar — avg vs ideal ──
    st.markdown("##### 📊 Your Average vs Ideal Targets")
    categories = ["Study Hours (norm)","Attendance","Prev Score","Sleep (norm)"]
    user_vals  = [
        round((float(df["Hours_Studied"].mean())/24)*100,1)  if "Hours_Studied"  in df.columns else 0,
        round(float(df["Attendance"].mean()),1)               if "Attendance"     in df.columns else 0,
        round(float(df["Previous_Scores"].mean()),1)          if "Previous_Scores" in df.columns else 0,
        round((float(df["Sleep_Hours"].mean())/12)*100,1)    if "Sleep_Hours"    in df.columns else 0,
    ]
    ideal_vals = [83, 90, 85, 67]   # 20h/24, 90%, 85, 8h/12
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="Your Average", x=categories, y=user_vals,
                             marker_color="#a78bfa", opacity=0.85))
    fig_bar.add_trace(go.Bar(name="Ideal Target", x=categories, y=ideal_vals,
                             marker_color="rgba(255,255,255,0.15)", marker_line_color="#a78bfa",
                             marker_line_width=1.5))
    fig_bar.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,.7)",
        xaxis=dict(gridcolor="rgba(255,255,255,.05)"),
        yaxis=dict(range=[0,110], gridcolor="rgba(255,255,255,.05)"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10,r=10,t=10,b=10), height=280
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Progress Insights ──
    st.markdown("##### 🧭 Progress Insights")
    if len(scores)>=2:
        ot = scores[-1]-scores[0]
        if ot>10:  st.markdown('<div class="tip-card">🚀 Excellent progress! Your score has improved significantly.</div>', unsafe_allow_html=True)
        elif ot>0: st.markdown('<div class="tip-card">📈 Steady improvement! Small consistent gains add up.</div>', unsafe_allow_html=True)
        elif ot==0:st.markdown('<div class="tip-card">⚖️ Score is stable. Try increasing study hours to break the plateau.</div>', unsafe_allow_html=True)
        else:      st.markdown('<div class="tip-card">⚠️ Score has dipped. Review study habits and sleep schedule.</div>', unsafe_allow_html=True)
    if avg>=80:   st.markdown('<div class="tip-card">🌟 Top-tier average — focus on consistency to maintain it.</div>', unsafe_allow_html=True)
    elif avg>=60: st.markdown('<div class="tip-card">📘 Passing zone — pushing study hours above 5/day can move you to A grade.</div>', unsafe_allow_html=True)
    else:         st.markdown('<div class="tip-card">🆘 Average below 60 — prioritise attendance, sleep, and daily revision first.</div>', unsafe_allow_html=True)

    # ── History Table ──
    st.markdown("---")
    st.markdown("##### 📋 Prediction History")
    for row in reversed(df.to_dict("records")):
        g,emoji,color = grade_info(row["score"])
        st.markdown(f"""
        <div class="history-row">
            <span>🕐 {row.get('timestamp','—')}</span>
            <span>Hours: {row.get('Hours_Studied','—')} &nbsp;|&nbsp; Attendance: {row.get('Attendance','—')}%</span>
            <span style="color:{color};font-weight:700;">{emoji} {row['score']} ({g})</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    if st.button("🗑️ Clear My History"):
        h=load_history(); h[st.session_state.username]=[]; save_history(h)
        st.success("History cleared."); st.rerun()

# =========================
# MAIN
# =========================
def show_app():
    c1,c2 = st.columns([4,1])
    with c1:
        st.markdown("### 🎓 Student Score Predictor")
        st.markdown(f'<span class="badge-success">✓ {st.session_state.username}</span>', unsafe_allow_html=True)
    with c2:
        if st.button("Log Out"):
            st.session_state.logged_in=False; st.session_state.username=""; st.rerun()
    st.markdown("---")

    try:
        model   = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
    except Exception as e:
        st.error(f"⚠️ Model files not found: {e}")
        st.info("Place `student_model.pkl` and `model_columns.pkl` in the same directory.")
        return

    tab1, tab2 = st.tabs(["🔮 Predictor", "📊 Progress Analysis"])
    with tab1: show_predictor(model, columns)
    with tab2: show_progress()

# =========================
# ROUTING
# =========================
if st.session_state.logged_in:
    show_app()
else:
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    if st.session_state.auth_mode=="login": show_login()
    else: show_signup()
    st.markdown('</div>', unsafe_allow_html=True)
