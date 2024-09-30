# Taller FastAPI - Universidad EIA

Este repositorio contiene la implementación de un API utilizando **FastAPI**, basada en los requerimientos del taller de **Sistemas Operativos** de la **Universidad EIA**. 

## Descripción del Proyecto

El objetivo de este taller es crear un API que permita consultar y manipular datos a través de endpoints, utilizando FastAPI. Los datos utilizados deben provenir de un dataset con al menos 1000 registros, que será cargado a una base de datos, y la API debe permitir operaciones como la consulta, el filtrado, la paginación y la ingesta de datos.

### Funcionalidades

1. **Consulta de datos mediante GET**: 
   - El endpoint permite la consulta de datos desde la base de datos.
   - Se puede filtrar los resultados para evitar traer toda la tabla.
   - Se implementa paginación, con un máximo de 100 registros por respuesta.

2. **Ingesta de datos mediante POST**: 
   - El endpoint permite la inserción de nuevos datos en la base de datos.
   - La ingesta de datos es validada utilizando modelos de Pydantic.
   - El response incluye cuántos registros fueron agregados y cuántos están en la base de datos.

3. **Excepciones y manejo de errores**: 
   - Se maneja adecuadamente las excepciones, devolviendo los códigos de error HTTP correspondientes en caso de fallos.

4. **Scripts de pruebas**: 
   - Un script de Bash o Python valida que los endpoints funcionen correctamente.

5. **Integración con NGROK**: 
   - La API se puede exponer al público a través de NGROK para facilitar el acceso remoto.

## Requisitos

- Python 3.x
- FastAPI
- Uvicorn
- PostgreSQL o MySQL (puede usarse otro motor de base de datos como DuckDB)
- NGROK

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/proyecto_fastapi.git
cd proyecto_fastapi
