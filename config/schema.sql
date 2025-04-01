CREATE DATABASE IF NOT EXISTS cinedb;

USE cinedb;

CREATE TABLE cinema (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE room (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cinema_id INT,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cinema_id) REFERENCES cinema(id)
);

CREATE TABLE admin_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    admin_level INT NOT NULL
);

CREATE TABLE manage (
    admin_id INT,
    cinema_id INT,
    PRIMARY KEY (admin_id, cinema_id),
    FOREIGN KEY (admin_id) REFERENCES admin_user(id),
    FOREIGN KEY (cinema_id) REFERENCES cinema(id)
);

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    birthdate DATE
);

CREATE TABLE booking (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    booking_id VARCHAR(255) UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE movie (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    synopsis TEXT,
    duration INT NOT NULL,
    rating VARCHAR(50),
    release_date DATE,
    photo_url VARCHAR(255)
);

CREATE TABLE functions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    movie_id INT,
    room_id INT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    FOREIGN KEY (room_id) REFERENCES room(id)
);

CREATE TABLE seat (
    id INT PRIMARY KEY AUTO_INCREMENT,
    function_id INT,
    number INT NOT NULL,
    seat_row VARCHAR(10) NOT NULL,
    status ENUM('available', 'reserved', 'occupied') NOT NULL,
    FOREIGN KEY (function_id) REFERENCES functions(id)
);

CREATE TABLE booking_seat (
    id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT,
    seat_id INT,
    FOREIGN KEY (booking_id) REFERENCES booking(id),
    FOREIGN KEY (seat_id) REFERENCES seat(id)
);

CREATE TABLE genre (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE movie_genre (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    FOREIGN KEY (genre_id) REFERENCES genre(id)
);

CREATE TABLE actor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    biography TEXT,
    photo_url VARCHAR(255)
);

CREATE TABLE movie_actor (
    movie_id INT,
    actor_id INT,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movie(id),
    FOREIGN KEY (actor_id) REFERENCES actor(id)
);
