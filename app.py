
import streamlit as st
import PyPDF2
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.title("📄 Resume Analyser System")

st.header("Upload Resume and Enter Job Description")

job_desc = st.text_area("Enter Job Description")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# -------------------------------
# Resume Parsing Module
# -------------------------------
def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# -------------------------------
# Keyword Extraction Module
# -------------------------------
def extract_keywords(text):
    words = re.findall(r'\b[A-Za-z]{3,}\b', text.lower())
    unique_words = list(set(words))
    return unique_words

# -------------------------------
# Skill Matching Module
# -------------------------------
def match_score(resume_text, job_text):
    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform([resume_text, job_text])
    score = cosine_similarity(vectors)[0][1]
    return round(score * 100, 2)

# -------------------------------
# Suggestion Module
# -------------------------------
def missing_skills(job_keywords, resume_keywords):
    return list(set(job_keywords) - set(resume_keywords))

# -------------------------------
# Report Generation Module
# -------------------------------
if st.button("Analyze Resume"):
    if resume_file and job_desc:

        resume_text = extract_text(resume_file)

        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_desc)

        score = match_score(resume_text, job_desc)

        missing = missing_skills(job_keywords, resume_keywords)

        st.subheader("📊 Resume Analysis Report")

        st.write("### Match Score")
        st.success(f"{score}%")

        st.write("### Extracted Resume Keywords")
        st.write(resume_keywords[:30])

        st.write("### Job Description Keywords")
        st.write(job_keywords[:30])

        st.write("### Missing Skills")
        if missing:
            st.warning(missing[:20])
        else:
            st.success("No major skills missing!")

        st.write("### Resume Preview")
        st.text(resume_text[:1000])

    else:
        st.error("Please upload resume and enter job description.")
