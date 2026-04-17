CREATE DATABASE IF NOT EXISTS blood_donation;
USE blood_donation;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'donor', 'hospital') DEFAULT 'donor'
);

CREATE TABLE donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    age INT,
    phone VARCHAR(20),
    address TEXT,
    location VARCHAR(255),
    last_donation DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(255),
    contact VARCHAR(50)
);

CREATE TABLE blood_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    units_available INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    UNIQUE(hospital_id, blood_group)
);

CREATE TABLE blood_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    units_required INT NOT NULL,
    urgency ENUM('low', 'medium', 'high') DEFAULT 'medium',
    status ENUM('pending', 'completed', 'rejected') DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

CREATE TABLE camps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(255) NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    camp_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
    FOREIGN KEY (camp_id) REFERENCES camps(id) ON DELETE CASCADE
);

-- Sample Data
INSERT INTO users (name, email, password, role) VALUES ('Admin', 'admin@blooddonate.com', '$2b$12$N9uYmO4J/SxykO9Fh/vMmeJ9hXGEfL3O4ZEY9VqAHzg2/5y6eS3Vq', 'admin');
INSERT INTO hospitals (name, location, contact) VALUES ('Central Blood Bank', 'Downtown, NY', '123-456-7890');
INSERT INTO hospitals (name, location, contact) VALUES ('City General Hospital', 'Uptown, NY', '098-765-4321');

-- Default blood groups for Central Blood Bank (ID=1)
INSERT INTO blood_stock (hospital_id, blood_group, units_available) VALUES 
(1, 'A+', 50), (1, 'A-', 15), (1, 'B+', 40), (1, 'B-', 10), 
(1, 'O+', 60), (1, 'O-', 2), (1, 'AB+', 25), (1, 'AB-', 0);

-- Default requests
INSERT INTO blood_requests (hospital_id, blood_group, units_required, urgency) VALUES
(2, 'O-', 5, 'high'),
(2, 'A+', 10, 'medium');
