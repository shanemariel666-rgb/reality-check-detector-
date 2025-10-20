# Use Python base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the Render port
EXPOSE 10000

# Start Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "main:app"]