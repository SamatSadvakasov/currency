FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Poetry specific env vars
    POETRY_VERSION=1.7.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        chromium \
        chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Copy poetry files first for better caching
#COPY pyproject.toml ./
#
## Install dependencies
#RUN poetry install

# Copy project files
COPY . .

COPY pyproject.toml ./
# Install project
RUN poetry install

