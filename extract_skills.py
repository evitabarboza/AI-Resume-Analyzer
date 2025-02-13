import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_skills(text):
    """Extract skills from resume text."""
    skills_list = ["Python", "Java", "C++", "Machine Learning", "SQL", "Flask", "Django", "JavaScript", "React", "HTML", "CSS", "Cloud Computing", "Data Analysis"]
    extracted_skills = []
    
    doc = nlp(text)
    for token in doc:
        if token.text in skills_list:
            extracted_skills.append(token.text)

    return list(set(extracted_skills))
