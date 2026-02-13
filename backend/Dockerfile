# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for building some python packages if needed)
# libpq-dev is for psycopg2/asyncpg potentially
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
# We use a start script to run migration/init then app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
