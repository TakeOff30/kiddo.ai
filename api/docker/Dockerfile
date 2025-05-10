FROM python:3.10-slim

WORKDIR /app

# Copia solo requirements
COPY api/docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia solo la cartella api (non tutto il progetto!)
COPY api/ /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
