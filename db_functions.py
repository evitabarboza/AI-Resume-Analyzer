import sqlite3
from datetime import datetime

db_path = "database/db.sqlite"

# Function to store resume evaluation scores
def store_score(resume_id, evaluation_score):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resume_scores (resume_id, evaluation_score, date)
            VALUES (?, ?, ?)
        """, (resume_id, evaluation_score, datetime.now()))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error storing resume score: {e}")

# Function to fetch past resume scores
def get_past_scores(resume_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT evaluation_score, date 
            FROM resume_scores
            WHERE resume_id = ?
        """, (resume_id,))
        scores = cursor.fetchall()
        conn.close()

        if not scores:
            return {"message": "No scores found for this resume."}

        return {"scores": [{"evaluation_score": score[0], "date": score[1]} for score in scores]}

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}
