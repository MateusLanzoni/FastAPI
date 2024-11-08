import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import psycopg2
import boto3
from psycopg2.extras import RealDictCursor
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Acceder a las variables de entorno
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
aws_s3_bucket = os.getenv('AWS_S3_BUCKET')


DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}"

app = FastAPI()

class Movie(BaseModel):
    popularity: str
    release_date: date
    title: str
    vote_average: float


def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")
    

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/movies/fecha/")
def read_movies_by_date(start_date: str, end_date: str):
    try:
        start_date_obj = datetime.strptime(start_date, "%m-%d-%Y")
        end_date_obj = datetime.strptime(end_date, "%m-%d-%Y")
    except ValueError:
        return {"error": "Formato de fecha inválido. Use MM-DD-YYYY."}

    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT popularity, release_date, title, vote_average
        FROM movies 
        WHERE release_date BETWEEN %s AND %s
        LIMIT 100
    """, (start_date, end_date))
    
    movies = cursor.fetchall()
    conn.close()
    
    result = [
        {
            "popularity": movie[0],
            "release_date": movie[1],
            "title": movie[2],
            "vote_average": movie[3],
        }
        for movie in movies
    ]
    
    return {"movies": result}



@app.get("/movie/{movie_name}")
def read_movie(movie_name: str):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT popularity,release_date,title,vote_average FROM movies WHERE title = %s", (movie_name,))
    movie = cursor.fetchone()
    conn.close()
    
    if movie is None:
        return {"error": "Pelicula no encontrado"}
    
    result = {
        "popularity": movie[0],
        "release_date": movie[1],
        "title": movie[2],
        "vote_average": movie[3],
    }
    
    return {"movie":result}

@app.post("/post/")
def create_movie(movies: List[Movie]):
    conn = connect_to_db()
    cursor = conn.cursor()

    registros_agregados = 0
    total_registros = 0

    try:
        for movie in movies:
            try:
                cursor.execute("""
                    INSERT INTO movies (popularity, release_date, title, vote_average)
                    VALUES (%s, %s, %s, %s)
                """, (movie.popularity, movie.release_date, movie.title, movie.vote_average))

                movie_data = {
                    "popularity": movie.popularity,
                    "release_date": movie.release_date.isoformat(),
                    "title": movie.title,
                    "vote_average": movie.vote_average
                }
                
                s3_client.put_object(
                    Bucket=os.getenv('AWS_S3_BUCKET'),
                    Key=f"movies/{movie.title}.json",
                    Body=json.dumps(movie_data),
                    ContentType='application/json'
                )

                registros_agregados += 1
            except Exception as e:
                print(f"Error al insertar la pelicula {movie.title}: {e}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error al insertar la pelicula {movie.title}.")

        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM movies")
        total_registros = cursor.fetchone()[0]

    except Exception as e:
        print(f"Error general: {e}")
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error general durante la operación")

    finally:
        cursor.close()
        conn.close()

    return {
        "registros_agregados": registros_agregados,
        "total_registros": total_registros
}
