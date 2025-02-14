from flask import Flask, request, jsonify, send_file
import mysql.connector
import os
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid
from resume_rating import rate_resume
from extract_text import extract_text_from_pdf
from extract_skills import extract_skills

import requests
from db_functions import store_score, get_past_scores

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
  # Change this!
jwt = JWTManager(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists

# ✅ In-memory rate limiting (No Redis)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]  # Global limit
)

load_dotenv()  # Load environment variables from .env file


# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),  # Use environment variable
    "database": "resume_db"
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# User Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return jsonify({"message": "CORS allowed"}), 200  # Just for testing CORS
    
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# User Login
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Allow max 5 login attempts per minute
def login():
    data = request.json
    email = data['email']
    password = data['password']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        access_token = create_access_token(identity=str(user['id']))
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# Protected Route Example
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": "You accessed a protected route!", "user_id": current_user}), 200

# Resume Upload (Protected)
@app.route('/upload_resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    resume = request.files['resume']
    
    # ✅ 1. Allow Only PDFs
    if not resume.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    user_id = get_jwt_identity()
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)

    # ✅ 2. Generate a Unique Filename
    unique_filename = f"{user_id}_{uuid.uuid4().hex}.pdf"
    resume_path = os.path.join(upload_folder, unique_filename)

    resume.save(resume_path)  # Save the PDF securely

    # ✅ 3. Extract Text from PDF (Using extract_text_from_pdf)
    extracted_text = extract_text_from_pdf(resume_path)

    # ✅ 4. Extract Skills (Using extract_skills)
    skills = extract_skills(extracted_text)

    # ✅ 5. Store File Path & Skills in Database
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO resumes (user_id, filename, filepath, skills) VALUES (%s, %s, %s, %s)", 
            (user_id, unique_filename, resume_path, ", ".join(skills))
        )
        conn.commit()
        return jsonify({"message": "Resume uploaded successfully!", "skills_extracted": skills}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# Resume Download
@app.route('/download/<filename>', methods=['GET'])
def download_resume(filename):
    file_path = os.path.join("uploads", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

# Fetch all resumes
@app.route('/resumes', methods=['GET'])
def get_resumes():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, filename, filepath, uploaded_at, skills FROM resumes")
    resumes = cursor.fetchall()
    conn.close()
    return jsonify({"resumes": resumes})

def validate_links(links):
    """
    Validate LinkedIn and GitHub profile links by checking their HTTP response status.
    """
    validated_links = {}
    
    for platform, url in links.items():
        if url:
            try:
                response = requests.head(url, allow_redirects=True, timeout=5)
                validated_links[platform] = response.status_code == 200
            except requests.RequestException:
                validated_links[platform] = False
        else:
           validated_links[platform] = False  # No link found
    
    return validated_links

@app.route('/rate-resume', methods=['POST'])
@jwt_required()
def rate_resume_api():
    """API endpoint to rate a resume with ATS compatibility and plagiarism check."""
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume = request.files['resume']

    if not resume.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    user_id = get_jwt_identity()  # Extract user_id from JWT token
    unique_filename = f"{user_id}_{uuid.uuid4().hex}.pdf"
    resume_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    resume.save(resume_path)


    # ✅ Call resume rating function (which includes ATS check)
    rating = rate_resume(resume_path)

    return jsonify({
        "message": "Resume rated successfully!",
        "rating": rating,
    }), 200

# Root route to check server status
@app.route("/")
@limiter.limit("5 per minute")  # Custom limit for this route
def home():
    return "Welcome to my Flask app!"

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

if __name__ == '__main__':
    app.run(debug=True)
