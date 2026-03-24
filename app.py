
import streamlit as st
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# -------------------------
# Helper Functions
# -------------------------

def calculate_match(resume_skills, required_skills):
    if not required_skills:
        return 0
    matched = set(resume_skills).intersection(set(required_skills))
    return int((len(matched) / len(required_skills)) * 100)


def generate_pdf(score, matched, missing, suggestions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Resume Analysis Report", ln=True)
    pdf.cell(200, 10, txt=f"Overall Match Score: {score}%", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Matched Skills:", ln=True)
    for skill in matched:
        pdf.cell(200, 8, txt=f"- {skill}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Missing Skills:", ln=True)
    for skill in missing:
        pdf.cell(200, 8, txt=f"- {skill}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="Recommendations:", ln=True)
    for line in suggestions:
        pdf.multi_cell(0, 8, txt=line)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# -------------------------
# UI Layout
# -------------------------

st.title("💼 Professional Resume Analyzer")
st.write("Upload your resume skills and compare them with job requirements.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Enter Your Resume Skills")
    resume_input = st.text_area(
        "Enter skills separated by commas",
        placeholder="Python, SQL, Machine Learning"
    )

with col2:
    st.subheader("Enter Job Required Skills")
    job_input = st.text_area(
        "Enter required skills separated by commas",
        placeholder="Python, Java, Spring Boot"
    )

analyze = st.button("Analyze Resume")

if analyze:
    resume_skills = [s.strip().lower() for s in resume_input.split(",") if s.strip()]
    required_skills = [s.strip().lower() for s in job_input.split(",") if s.strip()]

    score = calculate_match(resume_skills, required_skills)

    matched = list(set(resume_skills).intersection(set(required_skills)))
    missing = list(set(required_skills) - set(resume_skills))

    st.divider()

    # -------------------------
    # Score Section
    # -------------------------
    st.subheader("📊 Overall Resume Match")
    st.progress(score / 100)
    st.metric(label="Match Score", value=f"{score}%")

    # -------------------------
    # Appreciation Message
    # -------------------------
    if score >= 70:
        st.success("Great job! Your resume is strongly aligned with the job requirements.")
    elif score >= 40:
        st.info("Your resume shows good potential. Adding a few more skills can improve your chances.")
    else:
        st.warning("Your resume needs improvement to match this job profile. Don’t worry — you can improve it easily!")

    # -------------------------
    # Skills Display
    # -------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("✅ Skills Found in Your Resume")
        if matched:
            for skill in matched:
                st.markdown(f"- {skill.title()}")
        else:
            st.write("No matching skills found.")

    with col4:
        st.subheader("⚠️ Skills You Should Consider Adding")
        if missing:
            for skill in missing:
                st.markdown(f"- {skill.title()}")
        else:
            st.write("You have all the required skills. Excellent!")

    # -------------------------
    # Suggestions Section
    # -------------------------
    st.divider()
    st.subheader("🧠 Recommendations to Improve Your Resume")

    suggestions = []

    if missing:
        suggestions.append("Consider adding projects or certifications related to the missing skills.")
        suggestions.append("Mention your hands-on experience with these technologies in your project descriptions.")
    else:
        suggestions.append("Your resume is well aligned with the job requirements. Consider tailoring it further with measurable achievements.")

    for line in suggestions:
        st.write("• " + line)

    # -------------------------
    # PDF Report Download
    # -------------------------
    pdf_file = generate_pdf(score, matched, missing, suggestions)

    st.download_button(
        label="📄 Download Analysis Report (PDF)",
        data=pdf_file,
        file_name="resume_analysis_report.pdf",
        mime="application/pdf"
    )
