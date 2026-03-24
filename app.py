
import streamlit as st
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.title("📄 Resume Analyser")

st.write("Upload a resume and compare it with a job description.")

job_desc = st.text_area("Enter Job Description")

resume = st.file_uploader("Upload Resume", type="pdf")

def extract_text(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

if st.button("Analyze Resume"):
    if resume and job_desc:
        resume_text = extract_text(resume)

        data = [job_desc, resume_text]
        cv = CountVectorizer()
        matrix = cv.fit_transform(data)
        score = cosine_similarity(matrix)[0][1] * 100

        st.success(f"Resume Match Score: {round(score,2)}%")
    else:
        st.warning("Please upload resume and enter job description.")
