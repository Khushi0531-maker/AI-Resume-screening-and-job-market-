"""
AI-Based Resume Screening and Job Matching System
Streamlit Web Application with Authentication & Job Preferences Workflow
"""

import os
import io
import glob
import pandas as pd
import streamlit as st
import plotly.express as px

from src.auth import authenticate_user, register_user, update_user_preferences
from src.data_extractor import extract_text
from src.nlp_preprocessor import preprocess_text, clean_text_for_nlp
from src.skill_extractor import extract_skills_from_text, SKILL_TAXONOMY
from src.entity_parser import parse_resume_metadata
from src.matcher import match_resume_to_job, batch_match_resumes
from src.analytics import create_gauge_chart, create_radar_chart, create_leaderboard_chart


# Set page config
st.set_page_config(
    page_title="AI Resume Screening & Job Matching",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI design
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #475569;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .auth-container {
        max-width: 480px;
        margin: 20px auto;
        padding: 30px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .user-profile-badge {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 14px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .skill-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px;
    }
    .skill-match {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
    }
    .skill-missing {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
    }
    .step-banner {
        background: #F1F5F9;
        border-left: 4px solid #2563EB;
        padding: 10px 16px;
        border-radius: 4px;
        font-weight: 600;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_data" not in st.session_state:
    st.session_state["user_data"] = None


# Helper to load sample files
@st.cache_data
def load_sample_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


SAMPLE_JOB_MAP = {
    "Senior Data Scientist": "data/sample_jobs/data_scientist.txt",
    "Lead NLP & GenAI Engineer": "data/sample_jobs/nlp_genai_engineer.txt",
    "Full Stack Software Engineer": "data/sample_jobs/full_stack_developer.txt",
    "Senior Java Backend Engineer": "data/sample_jobs/java_backend_engineer.txt",
    "DevOps & Cloud Engineer": "data/sample_jobs/devops_engineer.txt",
    "Senior Data Engineer": "data/sample_jobs/data_engineer.txt"
}

SAMPLE_RESUME_PRESETS = {
    "Emily Chen (Lead NLP & GenAI Engineer - PDF)": "data/sample_resumes/emily_chen_nlp_genai.pdf",
    "Alex Morgan (Senior Data Scientist - DOCX)": "data/sample_resumes/alex_morgan_sample.docx",
    "David Kim (Senior Java Backend Engineer - DOCX)": "data/sample_resumes/david_kim_java_backend.docx",
    "Priya Sharma (Senior Big Data Engineer - PDF)": "data/sample_resumes/priya_sharma_data_engineer.pdf",
    "Carlos Rodriguez (Cloud Infrastructure Architect - PDF)": "data/sample_resumes/carlos_rodriguez_cloud_architect.pdf",
    "Aisha Patel (Senior Frontend & React Developer - DOCX)": "data/sample_resumes/aisha_patel_frontend_react.docx",
    "Sarah Jenkins (Full Stack Software Developer - TXT)": "data/sample_resumes/sarah_jenkins_fullstack.txt",
    "Marcus Vance (DevOps & Cloud Engineer - TXT)": "data/sample_resumes/marcus_vance_devops.txt",
    "Michael Brown (Cybersecurity & SOC Analyst - TXT)": "data/sample_resumes/michael_brown_cybersecurity.txt",
    "Rachel Green (Cross-Platform Mobile Developer - TXT)": "data/sample_resumes/rachel_green_mobile_dev.txt",
    "Thomas Clark (Business Intelligence & Data Analyst - TXT)": "data/sample_resumes/thomas_clark_bi_analyst.txt",
    "Jordan Lee (Junior Software Intern - TXT)": "data/sample_resumes/jordan_lee_junior_intern.txt"
}


# ==============================================================================
# VIEW 1: AUTHENTICATION / LOGIN PAGE (FIRST PAGE)
# ==============================================================================
if not st.session_state["logged_in"]:
    st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
    st.markdown("<div class='main-header'>🎯 AI-Based Resume Screening & Job Matching</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Natural Language Processing System for Intelligent Candidate-Job Alignment</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col_center, col_auth, col_right = st.columns([1, 1.4, 1])

    with col_auth:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["🔑 Log In", "📝 Create Account"])

        # TAB 1: LOGIN
        with tab_login:
            st.markdown("#### Welcome Back")
            login_email = st.text_input("Email Address", placeholder="e.g. candidate@jobseeker.com", key="login_email")
            login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

            if st.button("Sign In", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please provide both email and password.")
                else:
                    user = authenticate_user(login_email, login_password)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user_data"] = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please try again.")

            st.markdown("---")
            st.markdown("<div style='text-align: center; font-size: 0.9rem; color: #64748B;'>⚡ Quick 1-Click Demo Login:</div>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("👤 Demo Candidate", use_container_width=True):
                    demo_user = authenticate_user("candidate@jobseeker.com", "user123")
                    st.session_state["logged_in"] = True
                    st.session_state["user_data"] = demo_user
                    st.rerun()
            with col_d2:
                if st.button("🏢 Demo Recruiter", use_container_width=True):
                    demo_recruiter = authenticate_user("recruiter@company.com", "admin123")
                    st.session_state["logged_in"] = True
                    st.session_state["user_data"] = demo_recruiter
                    st.rerun()

        # TAB 2: REGISTER
        with tab_register:
            st.markdown("#### New Account Registration")
            reg_name = st.text_input("Full Name", placeholder="e.g. John Doe")
            reg_email = st.text_input("Email Address", placeholder="e.g. john@example.com")
            reg_password = st.text_input("Create Password", type="password")
            reg_role = st.selectbox("I am a:", ["Candidate / Job Seeker", "Recruiter / Hiring Manager"])

            if st.button("Create Account & Log In", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all registration fields.")
                else:
                    created = register_user(reg_name, reg_email, reg_password, reg_role)
                    if created:
                        new_user = authenticate_user(reg_email, reg_password)
                        st.session_state["logged_in"] = True
                        st.session_state["user_data"] = new_user
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("An account with this email already exists.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ==============================================================================
# LOGGED IN STATE - USER PROFILE & NAVIGATION
# ==============================================================================
user = st.session_state["user_data"]
user_prefs = user.get("preferences", {})

# Sidebar Navigation & Profile
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=56)
st.sidebar.title("Resume Matcher AI")

# User Profile Card in Sidebar
st.sidebar.markdown(f"""
<div class='user-profile-badge'>
    <div style='font-weight: 700; color: #1E293B; font-size: 1.05rem;'>👤 {user['name']}</div>
    <div style='font-size: 0.8rem; color: #2563EB; font-weight: 600;'>{user['role']}</div>
    <div style='font-size: 0.78rem; color: #64748B;'>{user['email']}</div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Sign Out", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["user_data"] = None
    st.rerun()

st.sidebar.markdown("---")

# Navigation Options
default_nav_idx = 0 if "Candidate" in user["role"] else 1
nav_mode = st.sidebar.radio(
    "Navigation Menu:",
    [
        "💼 Job Preferences & Profile",
        "👤 Candidate Mode (ATS Optimizer)",
        "🏢 Recruiter Mode (Batch Screening)",
        "🧠 NLP Pipeline Inspector"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Scoring Weights")
skill_w = st.sidebar.slider("Skill Match Weight", 0.0, 1.0, 0.55, 0.05)
tfidf_w = st.sidebar.slider("TF-IDF Similarity Weight", 0.0, 1.0, 0.35, 0.05)
kw_w = round(max(0.0, 1.0 - (skill_w + tfidf_w)), 2)
st.sidebar.caption(f"Keyword Salience Weight: **{kw_w:.2f}**")


# ==============================================================================
# MENU 1: JOB PREFERENCES & PROFILE
# ==============================================================================
if nav_mode == "💼 Job Preferences & Profile":
    st.markdown("<div class='main-header'>💼 Job Preferences & Career Profile</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Configure your targeted career preferences. The system uses these to recommend job matches and personalize resume screening.</div>", unsafe_allow_html=True)

    with st.form("preferences_form"):
        col_p1, col_p2 = st.columns(2, gap="large")

        with col_p1:
            st.markdown("#### 🎯 Target Roles & Seniority")
            available_roles = [
                "Data Scientist",
                "Machine Learning Engineer",
                "Full Stack Software Engineer",
                "Backend Developer",
                "Frontend Developer",
                "DevOps & Cloud Engineer",
                "Data Engineer",
                "AI/NLP Specialist",
                "Cyber Security Analyst"
            ]
            current_roles = user_prefs.get("preferred_roles", ["Data Scientist"])
            selected_roles = st.multiselect(
                "Preferred Job Roles:",
                options=available_roles,
                default=[r for r in current_roles if r in available_roles] or ["Data Scientist"]
            )

            exp_options = ["Entry Level / Fresher (0-2 years)", "Mid-Level (3-5 years)", "Senior Level (5+ years)", "Lead / Manager"]
            curr_exp = user_prefs.get("experience_level", "Mid-Level (3-5 years)")
            selected_exp = st.selectbox(
                "Experience Level:",
                options=exp_options,
                index=exp_options.index(curr_exp) if curr_exp in exp_options else 1
            )

            work_modes = ["Remote", "Hybrid", "On-site"]
            curr_wm = user_prefs.get("work_mode", "Hybrid")
            selected_wm = st.selectbox(
                "Work Mode Preference:",
                options=work_modes,
                index=work_modes.index(curr_wm) if curr_wm in work_modes else 1
            )

        with col_p2:
            st.markdown("#### 🛠️ Core Skills & Tech Stack")
            all_skills_flat = []
            for cat, sk_list in SKILL_TAXONOMY.items():
                all_skills_flat.extend([s.title() for s in sk_list])
            all_skills_unique = sorted(list(set(all_skills_flat)))

            curr_skills = [s.title() for s in user_prefs.get("core_skills", ["Python", "SQL", "Scikit-Learn"])]
            selected_skills = st.multiselect(
                "Core Technology & Tool Preferences:",
                options=all_skills_unique,
                default=[s for s in curr_skills if s in all_skills_unique] or ["Python", "Sql"]
            )

            target_loc = st.text_input(
                "Target Location / Country:",
                value=user_prefs.get("target_location", "Remote / Worldwide")
            )

        submitted = st.form_submit_button("💾 Save Job Preferences", type="primary", use_container_width=True)

        if submitted:
            new_prefs = {
                "preferred_roles": selected_roles,
                "experience_level": selected_exp,
                "work_mode": selected_wm,
                "target_location": target_loc,
                "core_skills": selected_skills
            }
            update_user_preferences(user["email"], new_prefs)
            st.session_state["user_data"]["preferences"] = new_prefs
            st.success("✅ Your job preferences have been saved successfully! They will now automatically pre-populate your Resume Matching sessions.")

    # Preferences Summary Card
    st.markdown("---")
    st.subheader("📋 Active Preference Snapshot")
    c_s1, c_s2, c_s3, c_s4 = st.columns(4)
    with c_s1:
        st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size: 1.25rem;'>{', '.join(user_prefs.get('preferred_roles', ['None']))}</div><div class='metric-label'>Target Roles</div></div>", unsafe_allow_html=True)
    with c_s2:
        st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size: 1.25rem;'>{user_prefs.get('experience_level', 'N/A')}</div><div class='metric-label'>Seniority</div></div>", unsafe_allow_html=True)
    with c_s3:
        st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size: 1.25rem;'>{user_prefs.get('work_mode', 'Hybrid')}</div><div class='metric-label'>Work Mode</div></div>", unsafe_allow_html=True)
    with c_s4:
        st.markdown(f"<div class='metric-card'><div class='metric-value' style='font-size: 1.25rem;'>{len(user_prefs.get('core_skills', []))} Skills</div><div class='metric-label'>Core Stack</div></div>", unsafe_allow_html=True)


# ==============================================================================
# MENU 2: CANDIDATE MODE (ATS RESUME OPTIMIZER)
# ==============================================================================
elif nav_mode == "👤 Candidate Mode (ATS Optimizer)":
    st.markdown("<div class='main-header'>👤 Candidate ATS Resume Optimizer</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Test your resume against target job postings. Pre-synced with your saved job preferences.</div>", unsafe_allow_html=True)

    # Determine default job preset based on saved preference
    user_preferred_role = user_prefs.get("preferred_roles", ["Data Scientist"])[0] if user_prefs.get("preferred_roles") else "Data Scientist"
    
    preset_choice = "Senior Data Scientist"
    if "Full Stack" in user_preferred_role or "Backend" in user_preferred_role or "Frontend" in user_preferred_role:
        preset_choice = "Full Stack Software Engineer"
    elif "DevOps" in user_preferred_role or "Cloud" in user_preferred_role:
        preset_choice = "DevOps & Cloud Engineer"

    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        st.markdown("<div class='step-banner'>Target Job Description</div>", unsafe_allow_html=True)
        job_options = list(SAMPLE_JOB_MAP.keys()) + ["Custom (Paste your own)"]
        cand_job_preset = st.selectbox(
            "Target Job Description:",
            job_options,
            index=job_options.index(preset_choice) if preset_choice in job_options else 0
        )

        cand_default_jd = ""
        if cand_job_preset in SAMPLE_JOB_MAP:
            cand_default_jd = load_sample_file(SAMPLE_JOB_MAP[cand_job_preset])

        cand_job_text = st.text_area("Job Description Text:", value=cand_default_jd, height=230, placeholder="Paste job description text...")

    with c2:
        st.markdown("<div class='step-banner'>Your Resume</div>", unsafe_allow_html=True)
        cand_resume_file = st.file_uploader("Upload your Resume (PDF, DOCX, TXT):", type=["pdf", "docx", "txt"])
        
        sample_choice = st.selectbox(
            "⚡ Or choose from 12 pre-loaded candidate resumes (PDF/DOCX/TXT):",
            ["None (Use uploaded file)"] + list(SAMPLE_RESUME_PRESETS.keys()),
            index=1  # default to Emily Chen or Alex Morgan
        )
        
        cand_resume_text = ""
        if cand_resume_file:
            cand_resume_text = extract_text(cand_resume_file, filename=cand_resume_file.name)
        elif sample_choice != "None (Use uploaded file)":
            sample_path = SAMPLE_RESUME_PRESETS[sample_choice]
            if os.path.exists(sample_path):
                with open(sample_path, "rb") as f:
                    cand_resume_text = extract_text(f, filename=os.path.basename(sample_path))

        if cand_resume_text:
            st.success(f"Resume text loaded ({len(cand_resume_text.split())} words)")

    st.markdown("---")

    if st.button("🔍 Analyze Resume & ATS Match", type="primary", use_container_width=True):
        if not cand_job_text.strip() or not cand_resume_text.strip():
            st.error("Please supply both a Job Description and a Resume to evaluate.")
        else:
            with st.spinner("Analyzing semantic overlap and extracting skills..."):
                analysis = match_resume_to_job(
                    cand_resume_text,
                    cand_job_text,
                    skill_weight=skill_w,
                    tfidf_weight=tfidf_w,
                    keyword_weight=kw_w
                )

            # Match Overview
            col_gauge, col_breakdown = st.columns([1, 1.2], gap="large")
            with col_gauge:
                st.plotly_chart(create_gauge_chart(analysis["composite_score"], title="Overall ATS Match Score"), use_container_width=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.15rem; font-weight: 600; color: {analysis['tier_color']};'>{analysis['tier']}</div>", unsafe_allow_html=True)

            with col_breakdown:
                st.subheader("🎯 Detailed Score Breakdown")
                scores = analysis["scores"]
                st.markdown(f"**Skill Overlap Match:** `{scores['skill_match']}%`")
                st.progress(scores["skill_match"] / 100.0)
                st.markdown(f"**TF-IDF Semantic Similarity:** `{scores['tfidf_similarity']}%`")
                st.progress(scores["tfidf_similarity"] / 100.0)
                st.markdown(f"**Key Term Presence:** `{scores['keyword_match']}%`")
                st.progress(scores["keyword_match"] / 100.0)

            st.markdown("---")

            # Skills Gap & Checklist
            col_sk1, col_sk2 = st.columns(2, gap="medium")
            with col_sk1:
                st.subheader("🔴 Missing Target Skills")
                st.caption("Skills found in the job description that are missing from your resume:")
                if analysis["skills"]["missing"]:
                    missing_badges = " ".join([f"<span class='skill-badge skill-missing'>+ {s}</span>" for s in analysis["skills"]["missing"]])
                    st.markdown(missing_badges, unsafe_allow_html=True)
                else:
                    st.success("Great job! No major skill gaps detected.")

            with col_sk2:
                st.subheader("🟢 Matching Strengths")
                st.caption("Skills you have that align directly with this job posting:")
                if analysis["skills"]["matched"]:
                    matched_badges = " ".join([f"<span class='skill-badge skill-match'>✓ {s}</span>" for s in analysis["skills"]["matched"]])
                    st.markdown(matched_badges, unsafe_allow_html=True)
                else:
                    st.warning("No explicit skills overlapped between resume and job.")

            st.markdown("---")

            # Radar Chart & Recommendations
            c_rad, c_rec = st.columns([1.1, 1], gap="medium")
            with c_rad:
                st.subheader("📊 Skill Domain Coverage")
                radar = create_radar_chart(analysis["skills"]["candidate_categorized"], analysis["skills"]["job_categorized"])
                st.plotly_chart(radar, use_container_width=True)

            with c_rec:
                st.subheader("💡 Actionable ATS Optimization Tips")
                for rec in analysis["recommendations"]:
                    st.info(rec)


# ==============================================================================
# MENU 3: RECRUITER MODE (BATCH SCREENING & RANKING)
# ==============================================================================
elif nav_mode == "🏢 Recruiter Mode (Batch Screening)":
    st.markdown("<div class='main-header'>🏢 Recruiter Batch Screening & Ranking</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Upload a job requisition and evaluate dozens of resumes simultaneously with NLP scoring and CSV export.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.markdown("<div class='step-banner'>Step 1: Select or Paste Job Requisition</div>", unsafe_allow_html=True)
        recruiter_job_options = list(SAMPLE_JOB_MAP.keys()) + ["Custom (Input your own)"]
        job_preset = st.selectbox(
            "Quick-load Job Requisition:",
            recruiter_job_options
        )

        default_job_text = ""
        if job_preset in SAMPLE_JOB_MAP:
            default_job_text = load_sample_file(SAMPLE_JOB_MAP[job_preset])

        job_description_input = st.text_area(
            "Job Description Text:",
            value=default_job_text,
            height=240,
            placeholder="Paste complete Job Description here..."
        )

    with col2:
        st.markdown("<div class='step-banner'>Step 2: Upload Candidate Resumes</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload resumes (PDF, DOCX, TXT) - multiple allowed:",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True
        )
        use_demo_resumes = st.checkbox("⚡ Or screen all 15+ pre-loaded candidate resumes (PDF, DOCX, TXT) for instant ranking", value=False)

    st.markdown("---")

    if st.button("🚀 Screen and Rank Candidates", type="primary", use_container_width=True):
        if not job_description_input.strip():
            st.error("Please supply a Job Description to evaluate candidates against.")
        else:
            candidates_to_screen = []
            if uploaded_files:
                for file in uploaded_files:
                    try:
                        text = extract_text(file, filename=file.name)
                        if text:
                            candidates_to_screen.append({"filename": file.name, "text": text})
                    except Exception as e:
                        st.warning(f"Could not parse {file.name}: {e}")

            if use_demo_resumes or len(candidates_to_screen) == 0:
                demo_paths = glob.glob("data/sample_resumes/*.*")
                for path in demo_paths:
                    filename = os.path.basename(path)
                    if not any(c["filename"] == filename for c in candidates_to_screen):
                        with open(path, "rb") as f:
                            text = extract_text(f, filename=filename)
                            if text:
                                candidates_to_screen.append({"filename": filename, "text": text})

            if not candidates_to_screen:
                st.warning("No resumes detected. Please upload resumes or enable pre-loaded candidates.")
            else:
                with st.spinner("Screening resumes with NLP pipeline..."):
                    results = batch_match_resumes(candidates_to_screen, job_description_input)

                st.success(f"Screened and ranked **{len(results)} candidates**!")

                # Key Metrics
                avg_score = round(sum(c["composite_score"] for c in results) / len(results), 1)
                top_candidate = results[0]
                qualified_count = sum(1 for c in results if c["composite_score"] >= 65.0)

                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{len(results)}</div><div class='metric-label'>Screened</div></div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{top_candidate['composite_score']}%</div><div class='metric-label'>Top Score</div></div>", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_score}%</div><div class='metric-label'>Avg Score</div></div>", unsafe_allow_html=True)
                with m4:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{qualified_count} / {len(results)}</div><div class='metric-label'>Qualified (≥65%)</div></div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Leaderboard
                st.subheader("📊 Candidate Ranking Leaderboard")
                st.plotly_chart(create_leaderboard_chart(results), use_container_width=True)

                # CSV Export
                table_rows = []
                for c in results:
                    meta = c["metadata"]
                    table_rows.append({
                        "Rank": c["rank"],
                        "Candidate Name": meta["name"],
                        "Composite Match (%)": c["composite_score"],
                        "Skill Match (%)": c["scores"]["skill_match"],
                        "TF-IDF Similarity (%)": c["scores"]["tfidf_similarity"],
                        "Matched Skills Count": len(c["skills"]["matched"]),
                        "Missing Skills Count": len(c["skills"]["missing"]),
                        "Experience (Years)": meta["experience_years"],
                        "Email": meta["email"] or "N/A",
                        "Phone": meta["phone"] or "N/A",
                        "File": c["filename"],
                        "Tier": c["tier"]
                    })
                df_results = pd.DataFrame(table_rows)

                csv_bytes = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Screening Report (CSV)",
                    data=csv_bytes,
                    file_name="candidate_rankings.csv",
                    mime="text/csv"
                )

                # Detailed Profiles
                st.markdown("### 🔍 Individual Candidate Profiles")
                for c in results:
                    meta = c["metadata"]
                    with st.expander(f"🏅 #{c['rank']} - {meta['name']} | Match Score: {c['composite_score']}% ({c['tier']}) - File: {c['filename']}", expanded=(c['rank'] == 1)):
                        col_info, col_chart = st.columns([1.3, 1], gap="medium")
                        with col_info:
                            st.markdown(f"**Contact:** 📧 `{meta['email'] or 'Not detected'}` | 📞 `{meta['phone'] or 'Not detected'}`")
                            st.markdown(f"**Experience:** `{meta['experience_years']} years`")
                            if meta["education"]["degrees"]:
                                st.markdown(f"**Degrees:** `{', '.join(meta['education']['degrees'])}`")
                            st.markdown("##### 🟢 Matched Skills:")
                            if c["skills"]["matched"]:
                                matched_html = " ".join([f"<span class='skill-badge skill-match'>✓ {s}</span>" for s in c["skills"]["matched"]])
                                st.markdown(matched_html, unsafe_allow_html=True)
                            st.markdown("##### 🔴 Missing Skills:")
                            if c["skills"]["missing"]:
                                missing_html = " ".join([f"<span class='skill-badge skill-missing'>✗ {s}</span>" for s in c["skills"]["missing"]])
                                st.markdown(missing_html, unsafe_allow_html=True)
                        with col_chart:
                            st.plotly_chart(create_radar_chart(c["skills"]["candidate_categorized"], c["skills"]["job_categorized"]), use_container_width=True)


# ==============================================================================
# MENU 4: NLP PIPELINE INSPECTOR
# ==============================================================================
elif nav_mode == "🧠 NLP Pipeline Inspector":
    st.markdown("<div class='main-header'>🧠 NLP Pipeline & Sandbox</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Test how tokenization, stopword removal, and skill extraction work interactively.</div>", unsafe_allow_html=True)

    user_sample_text = st.text_area(
        "Enter any text to inspect:",
        value="Senior Machine Learning Engineer with 4+ years of experience building NLP pipelines, deep learning models, and microservices in Python, PyTorch, and Docker on AWS.",
        height=100
    )

    if user_sample_text:
        col_tok, col_lem, col_sk = st.columns(3, gap="medium")
        with col_tok:
            st.markdown("##### 1. Cleaned Text (Tech Tokens Protected)")
            st.code(clean_text_for_nlp(user_sample_text), language="text")
        with col_lem:
            st.markdown("##### 2. Lemmatized & Stopword-Free")
            st.code(preprocess_text(user_sample_text), language="text")
        with col_sk:
            st.markdown("##### 3. Skills Detected")
            extracted = extract_skills_from_text(user_sample_text)
            for sk in extracted["flat_skills"]:
                st.markdown(f"- **{sk}**")
