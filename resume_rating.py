import pdfplumber
import re
from extract_skills import extract_skills

# ✅ Define skill list to avoid NameError
SKILLS_LIST = ["Python", "Java", "C++", "SQL", "Flask", "Django", "React", "Machine Learning", "Cloud Computing"]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip() if text else None

def check_ats_friendly(text):
    """
    Checks if a resume is ATS-friendly based on key sections and formatting issues.
    """
    # ✅ Define standard ATS sections
    required_sections = ["education", "experience", "skills", "projects", "certifications"]

    # ✅ Check if all required sections exist
    found_sections = [section for section in required_sections if section.lower() in text.lower()]
    missing_sections = [section for section in required_sections if section.lower() not in text.lower()]

    # ✅ Check for non-ATS-friendly formatting (tables, images, special characters)
    non_ats_patterns = [r"\[.*?\]", r"\{.*?\}", r"<.*?>"]  # Patterns indicating tables or non-text elements
    non_ats_issues = any(re.search(pattern, text) for pattern in non_ats_patterns)

    # ✅ Generate ATS Score
    ats_score = (len(found_sections) / len(required_sections)) * 100

    return {
        "ATS Score": round(ats_score, 2),
        "Missing Sections": missing_sections,
        "Non-ATS Issues Found": non_ats_issues
    }

def rate_resume(pdf_path):
    """Rate the resume based on extracted skills and ATS compatibility."""
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return {"error": "Failed to extract text from the PDF."}

    extracted_skills = extract_skills(text)

    # ✅ Ensure SKILLS_LIST is not empty
    if not SKILLS_LIST:
        return {"error": "Skill list is empty. Cannot rate resume."}

    # ✅ Avoid division by zero
    score = (len(extracted_skills) / len(SKILLS_LIST)) * 100 if SKILLS_LIST else 0
    score = round(score, 2)

    feedback = []
    if score < 50:
        feedback.append("Consider adding more technical skills and certifications.")
    if "Python" not in extracted_skills:
        feedback.append("Python is in high demand. Consider learning and adding it.")
    if "SQL" not in extracted_skills:
        feedback.append("SQL is crucial for data-related jobs. Consider improving your SQL knowledge.")

    # ✅ Run ATS compatibility check
    ats_result = check_ats_friendly(text)

    return {
        "score": score,
        "skills_detected": extracted_skills,
        "feedback": feedback,
        "ATS Compatibility": ats_result
    }
