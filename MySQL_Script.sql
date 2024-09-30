
CREATE TABLE movies (
    popularity DECIMAL(10,3),
    release_date VARCHAR(255),
    title VARCHAR(255),
    vote_average DECIMAL(5,3)
);

DROP TABLE IF EXISTS movies;

COPY movies (popularity, release_date, title, vote_average) FROM 'C:\Users\danie\Desktop\Top_Rated_Movies.csv' DELIMITER ',' CSV HEADER;

SELECT * FROM movies;

DROP TABLE movies;