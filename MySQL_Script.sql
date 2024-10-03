
CREATE TABLE movies (
    popularity DECIMAL(10,3),
    release_date VARCHAR(255),
    title VARCHAR(255),
    vote_average DECIMAL(5,3)
);

DROP TABLE IF EXISTS movies;

COPY movies (popularity, release_date, title, vote_average) FROM './Top_Rated_Movies.csv' DELIMITER ',' CSV HEADER;

SELECT * FROM movies;

DROP TABLE movies;

#Debes correr este coigo en la terminal para poder acceder a la base de datos, utilizanddo lo instalado en requirements.txt.

#sudo -i -u postgres
#psql

#1: CREATE USER postgres WITH PASSWORD 'dollarfen54'; estos son los datos utilizados si se cambian se debe cambiar en el archivo main.py
#2: CREATE DATABASE sisoptaller owner postgres;
#3: ALTER USER postgres WITH SUPERUSER;
#4: psql -U postgres -d sisoptaller
#5: psql -U miusuario conexion atras de socket local

#cuando termines estos pasos ya deberias tener acceso a la base de datos y poder correr el codigo para crear tabla, luego se puede testear con el select.


