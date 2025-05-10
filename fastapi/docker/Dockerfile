FROM python:3.10-slim

WORKDIR /app

# Copia solo requirements
COPY fastapi/docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia solo la cartella fastapi (non tutto il progetto!)
COPY fastapi/ /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
