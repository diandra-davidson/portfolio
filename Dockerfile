FROM python:3.12.3-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Gunicorn
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "__init__:create_app()", "--bind", "0.0.0.0:8000"]
