# Use a stable Python version compatible with FastAPI + SQLAlchemy
FROM python:3.11-slim

# Create working directory for the app
WORKDIR /app

# Install system dependencies (SQLite, build tools)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    && apt-get clean

# Copy backend code into container
COPY . /app

# Create a virtual environment inside the container
RUN python3 -m venv /venv

# Ensure venv paths come first
ENV PATH="/venv/bin:$PATH"

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Install backend dependencies (excluding TTS, handled in separate TTS container)
RUN pip install fastapi uvicorn[standard] sqlalchemy httpx pydantic

# Expose FastAPI port
EXPOSE 5000

# Default command to run the backend
CMD ["/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
