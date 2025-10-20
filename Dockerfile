# Use official Python runtime
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Render port
EXPOSE 10000

# Environment variable for Flask
ENV PORT=10000
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=10000

# Run the Flask app
CMD ["python", "main.py"]
