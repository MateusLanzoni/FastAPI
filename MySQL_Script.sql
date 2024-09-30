-- Create the table for movies
CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    popularity DECIMAL(10,3),
    release_date DATE,
    title VARCHAR(255),
    vote_average DECIMAL(5,3)
);
