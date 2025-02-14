-- Select the resume_db database
USE resume_db;

-- Create the users table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
);


-- Create the resumes table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- Link to the user who uploaded the resume
    filename VARCHAR(255) NOT NULL,
    skills TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- Foreign key to user
);

-- Create the plagiarism_scores table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS plagiarism_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT,
    plagiarism_score REAL,
    uniqueness_score REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);
