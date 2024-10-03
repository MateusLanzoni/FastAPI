from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
import os
# from dotenv import load_dotenv

# load_dotenv()

db_host = os.getenv('localhost')
db_name = os.getenv('sisoptaller')
db_user = os.getenv('postgres')
db_password = os.getenv('dollarfen54')

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"

app = FastAPI()

class Movie(BaseModel):
    id: Optional[int]
    title: str
    release_date: date
    genre: str

class MovieIngestion(BaseModel):
    title: str = Field(..., example="Inception")
    release_date: date = Field(..., example="2010-07-16")
    genre: str = Field(..., example="Sci-Fi")

def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")

def get_movies(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = "SELECT * FROM movies LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        movies = cursor.fetchall()
        cursor.close()
        conn.close()
        return movies
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch movies")

def create_movies(movies: List[MovieIngestion]) -> Dict[str, int]:
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        inserted_count = 0

        for movie in movies:
            cursor.execute(
                "INSERT INTO movies (title, release_date, genre) VALUES (%s, %s, %s)",
                (movie.title, movie.release_date, movie.genre)
            )
            inserted_count += 1

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM movies")
        total_count = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {"inserted": inserted_count, "total": total_count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to insert movies")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/movies", response_model=List[Movie])
def read_movies(
    limit: int = Query(100, description="Limit the number of results", le=100),
    offset: int = Query(0, description="Offset for pagination")
):
    return get_movies(limit=limit, offset=offset)

@app.post("/movies", response_model=Dict[str, int])
def add_movies(movies: List[MovieIngestion]):
    return create_movies(movies)

@app.get("/movies/{movie_name}", response_model=Movie)
def read_movie(movie_name: str):
    try:
        conn = connect_to_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM movies WHERE title = %s", (movie_name,))
        movie = cursor.fetchone()
        cursor.close()
        conn.close()

        if not movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

        return movie
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch movie")

@app.put("/movies/{movie_id}", response_model=Movie)
def edit_movie(movie_id: int, movie: Movie):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE movies
            SET title = %s, release_date = %s, genre = %s
            WHERE id = %s
            RETURNING id, title, release_date, genre
        """, (movie.title, movie.release_date, movie.genre, movie_id))
        updated_movie = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not updated_movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

        return updated_movie
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update movie")

@app.delete("/movies/{movie_id}")
def remove_movie(movie_id: int):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = %s RETURNING id", (movie_id,))
        deleted_movie = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not deleted_movie:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

        return {"detail": "Movie deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete movie")