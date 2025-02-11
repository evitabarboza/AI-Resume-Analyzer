from flask import Flask, request, jsonify, send_file
import mysql.connector
import os
import spacy
import PyPDF2

app = Flask(__name__)

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "EVita@#$&2004",  # Change this to your MySQL root password
    "database": "resume_db"
}

# Establish database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/resumes', methods=['GET'])
def get_resumes():
    """Fetch all uploaded resumes from the database"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, filename, filepath, uploaded_at FROM resumes")
    resumes = cursor.fetchall()
    
    conn.close()
    return jsonify({"resumes": resumes})

@app.route('/upload', methods=['POST'])
def upload_resume():
    """Upload a resume and store it in the database"""
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)  # Ensure upload folder exists
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Extract text from PDF
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    # Extract skills from text
    skills = extract_skills_from_text(text)

    # Store in database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    cursor.execute("INSERT INTO resumes (filename, filepath, skills) VALUES (%s, %s, %s)", 
                   (file.filename, file_path, ", ".join(skills)))
    conn.commit()
    conn.close()

    return jsonify({"message": "File uploaded successfully", "skills_extracted": skills})

@app.route('/download/<filename>', methods=['GET'])
def download_resume(filename):
    """Download a resume from the uploads folder"""
    file_path = os.path.join("uploads", filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

# Root route to check server status
@app.route('/')
def home():
    return "Flask App is Running!"

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def extract_skills_from_text(text):
    """Extract skills from a given resume text"""
    skills_list = ["Python", "Java", "C++", "Machine Learning", "SQL", "Flask", "Django", "JavaScript", "React", "HTML", "CSS", "Cloud Computing", "Data Analysis"]
    
    extracted_skills = []
    doc = nlp(text)
    
    for token in doc:
        if token.text in skills_list:
            extracted_skills.append(token.text)
    
    return list(set(extracted_skills))  # Remove duplicates

if __name__ == '__main__':
    app.run(debug=True)
