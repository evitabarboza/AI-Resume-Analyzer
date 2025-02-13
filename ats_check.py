import re

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
