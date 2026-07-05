# Christmas Menu Generator - Backend Dockerfile
# Ottimizzato per Render.com Free Tier

FROM python:3.12-slim

# Imposta directory di lavoro
WORKDIR /app

# Variabili d'ambiente per Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice backend
COPY backend/ ./backend/

# Espone la porta (Render usa $PORT)
EXPOSE 8000

# Comando di avvio - usa $PORT fornito da Render
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
