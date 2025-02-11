CREATE DATABASE resume_db;
USE resume_db;

CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    skills TEXT NOT NULL
);
