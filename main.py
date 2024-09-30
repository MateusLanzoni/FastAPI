from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
# from database import SessionLocal
from models import Movie
from typing import List, Optional
from datetime import date
import psycopg2

app = FastAPI()

# Dependencia para obtener la base de datos
# Conexión a la base de datos
def connect_to_db():
    conn = psycopg2.connect(
    host="localhost",
    database="sisopTaller",
    user="postgres",
    password="dollarfen54"
    )
    return conn

# Dependencia para obtener la conexión a la base de datos
def get_db():
    conn = connect_to_db()
    try:
        yield conn
    finally:
        conn.close()

@app.get("/movies/", response_model=List[Movie])
def get_movies(skip: int = 0, limit: int = 100, 
               title: Optional[str] = None,
               popularity: Optional[float] = None, 
               release_date: Optional[str] = None, 
	           vote_average: Optional[float] = None, 
               db: Session = Depends(get_db)):
    
    if limit > 100:
        limit = 100  # Limitar a un máximo de 100 resultados por página
    
    # Empezamos construyendo la consulta
    query = db.query(Movie)
    
    # Agregar filtros si se pasan como parámetros
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    if popularity:
        query = query.filter(Movie.popularity >= popularity)
    if release_date:
        query = query.filter(Movie.release_date == release_date)
    
    # Obtener los resultados con paginación
    movies = query.offset(skip).limit(limit).all()
    
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found")
    
    return movies
