import streamlit as st
import PyPDF2
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Resume Analyser", layout="wide")

st.title("📄 AI Resume Analyser")
st.markdown("Upload a resume and compare it with a job description to get ATS match score, skills, and suggestions.")

# -------------------------------
# File Upload & Input
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    job_desc = st.text_area("🧾 Job Description", height=200)

with col2:
    resume_file = st.file_uploader("📤 Upload Resume (PDF)", type=["pdf"])

# -------------------------------
# Text Extraction
# -------------------------------
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# -------------------------------
# Skill Extraction
# -------------------------------
skill_db = [
    "python", "java", "c++", "flask", "django", "sql",
    "machine learning", "data analysis", "html", "css",
    "javascript", "react", "nlp", "deep learning"
]

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in skill_db:
        if skill in text:
            found.append(skill)
    return list(set(found))

# -------------------------------
# Keyword Extraction
# -------------------------------
def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return list(set(words))

# -------------------------------
# Similarity Score
# -------------------------------
def calculate_score(resume_text, job_text):
    tfidf = TfidfVectorizer(stop_words="english")
    vectors = tfidf.fit_transform([resume_text, job_text])
    score = cosine_similarity(vectors)[0][1]
    return round(score * 100, 2)

# -------------------------------
# Main Execution
# -------------------------------
if st.button("🔍 Analyze Resume"):

    if not resume_file or not job_desc:
        st.error("Please upload resume and enter job description.")
    else:
        resume_text = extract_text(resume_file)

        score = calculate_score(resume_text, job_desc)
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_desc)

        missing_skills = list(set(job_skills) - set(resume_skills))

        # -------------------------------
        # Display Score
        # -------------------------------
        st.subheader("📊 ATS Match Score")
        st.progress(int(score))
        st.success(f"Overall Resume Match: {score}%")

        # -------------------------------
        # Skills Comparison Table
        # -------------------------------
        st.subheader("🧠 Skills Analysis")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("### Resume Skills")
            st.write(resume_skills)

        with col4:
            st.markdown("### Required Skills")
            st.write(job_skills)

        # -------------------------------
        # Missing Skills
        # -------------------------------
        st.subheader("⚠️ Missing Skills")
        if missing_skills:
            st.warning(", ".join(missing_skills))
        else:
            st.success("Your resume matches all required skills!")

        # -------------------------------
        # Detailed Report Table
        # -------------------------------
        st.subheader("📑 Detailed Comparison Report")

        data = {
            "Required Skills": job_skills,
            "Status": ["Matched" if skill in resume_skills else "Missing" for skill in job_skills]
        }

        df = pd.DataFrame(data)
        st.dataframe(df)

        # -------------------------------
        # Resume Preview
        # -------------------------------
        with st.expander("📄 View Extracted Resume Text"):
            st.write(resume_text[:2000])
