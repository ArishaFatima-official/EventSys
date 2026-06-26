CREATE DATABASE IF NOT EXISTS eventdb;
USE eventdb;

-- Students table (for signup/login)
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    sapid VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    eventid INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    venue VARCHAR(200) NOT NULL,
    capacity INT NOT NULL
);

-- Registrations table
CREATE TABLE IF NOT EXISTS registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sapid VARCHAR(20) NOT NULL,
    studentname VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    eventid INT,
    status VARCHAR(50) DEFAULT 'Registered',
    FOREIGN KEY (eventid) REFERENCES events(eventid) ON DELETE CASCADE
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    attendanceid INT AUTO_INCREMENT PRIMARY KEY,
    sapid VARCHAR(20) NOT NULL,
    studentname VARCHAR(100) NOT NULL,
    eventid INT,
    attendance_status VARCHAR(50) DEFAULT 'Not Marked',
    FOREIGN KEY (eventid) REFERENCES events(eventid) ON DELETE CASCADE
);

-- Default admin account (username: admin, password: admin123)
INSERT IGNORE INTO admins (username, password) VALUES ('admin', 'admin123');

-- Sample events
INSERT IGNORE INTO events (eventid, title, date, venue, capacity) VALUES
(1, 'Tech Fest 2025', '2025-06-15', 'Main Auditorium', 200),
(2, 'AI Workshop', '2025-07-10', 'Lab Block A', 50),
(3, 'Hackathon Spring', '2025-08-01', 'Innovation Hub', 100);
