#!/bin/bash

# Crear entorno virtual
python3 -m venv env

# Activar entorno virtual
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt