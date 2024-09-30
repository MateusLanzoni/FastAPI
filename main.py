from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Database connection
def connect_to_db():
    conn = psycopg2.connect(
        host="localhost",
        database="sisoptaller",
        user="sistemas",
        password="dollarfen54"
    )
    return conn

# Pydantic model for Movie
class Movie(BaseModel):
    id: Optional[int]
    title: str
    release_date: date
    genre: str

# Create movies table
def create_movies_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100) NOT NULL,
        release_date DATE NOT NULL,
        genre VARCHAR(50) NOT NULL
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

create_movies_table()

# CRUD operations
def get_movies():
    conn = connect_to_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return movies

def get_movie(movie_id: int):
    conn = connect_to_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

def create_movie(movie: Movie):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movies (title, release_date, genre) VALUES (%s, %s, %s) RETURNING id",
        (movie.title, movie.release_date, movie.genre)
    )
    movie_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {**movie.dict(), "id": movie_id}

def update_movie(movie_id: int, movie: Movie):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movies SET title = %s, release_date = %s, genre = %s WHERE id = %s",
        (movie.title, movie.release_date, movie.genre, movie_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return get_movie(movie_id)

def delete_movie(movie_id: int):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Movie deleted successfully"}

# FastAPI endpoints
@app.get("/movies", response_model=List[Movie])
def read_movies():
    return get_movies()

@app.get("/movies/{movie_id}", response_model=Movie)
def read_movie(movie_id: int):
    return get_movie(movie_id)

@app.post("/movies", response_model=Movie)
def add_movie(movie: Movie):
    return create_movie(movie)

@app.put("/movies/{movie_id}", response_model=Movie)
def edit_movie(movie_id: int, movie: Movie):
    return update_movie(movie_id, movie)

@app.delete("/movies/{movie_id}")
def remove_movie(movie_id: int):
    return delete_movie(movie_id)