CREATE DATABASE IF NOT EXISTS file_sharing;
USE file_sharing;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);

INSERT INTO users (id, username, email, password_hash, role) VALUES ('1', 'admin', 'admin@gmail.com', 'scrypt:32768:8:1$P8R628nAyJN0A4y0$d08255d559b19ba388a2b015c221341c272711f445688b9cd22f7de04569d421ed5b33591e978fc8af4cc2795fb7a6ed7fe19143b83578c85f7140d5506258b3', 'admin');
INSERT INTO users (id, username, email, password_hash, role) VALUES ('2', 'user1', 'user1@gmail.com', 'scrypt:32768:8:1$P8R628nAyJN0A4y0$d08255d559b19ba388a2b015c221341c272711f445688b9cd22f7de04569d421ed5b33591e978fc8af4cc2795fb7a6ed7fe19143b83578c85f7140d5506258b3', 'user');

CREATE TABLE IF NOT EXISTS file_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    creator_id INT NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(255) NOT NULL,
    uploaded_by INT,
    group_id INT,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES file_groups(id)
);

CREATE TABLE IF NOT EXISTS user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    group_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES file_groups(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT,
    user_id INT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);