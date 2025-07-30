import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Load API key from Streamlit secrets or .env
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

# Check if API key exists and set it as env variable
if not api_key:
    st.error("❌ OpenAI API key not found. Please add it to .env or Streamlit Secrets.")
    st.stop()
else:
    os.environ["OPENAI_API_KEY"] = api_key

# Initialize OpenAI client (no need to pass api_key explicitly)
client = OpenAI()

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text

# Function to get feedback
def get_resume_feedback(resume_text):
    prompt = f"""
You are an expert career coach and recruiter.

Analyze this resume text and provide the following:
1. Strengths in the resume
2. Weaknesses or areas to improve
3. Suggestions to make it better
4. Give a score out of 100 based on resume quality

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="🧠 Resume Feedback AI", layout="centered")
st.title("🧠 AI Resume Feedback App")
st.markdown("Upload your **resume PDF** or paste your resume content below to get instant feedback!")

input_method = st.radio("Choose input method:", ["📄 Upload PDF", "📝 Paste Resume Text"])

resume_text = ""

if input_method == "📄 Upload PDF":
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)

elif input_method == "📝 Paste Resume Text":
    resume_text = st.text_area("Paste your resume content here:", height=300)

if st.button("Get Feedback"):
    if resume_text.strip():
        with st.spinner("Analyzing your resume..."):
            feedback = get_resume_feedback(resume_text)
            st.success("✅ Analysis complete!")
            st.markdown("### 📋 Feedback")
            st.write(feedback)
    else:
        st.warning("⚠️ Please upload a PDF or paste resume text to get feedback.")
