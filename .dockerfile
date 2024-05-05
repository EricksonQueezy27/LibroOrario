# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential python3-dev

# Create a virtual environment and activate it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Collect static files and run migrations
RUN python manage.py collectstatic --noinput && \
    python manage.py makemigrations && \
    python manage.py migrate

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "config.wsgi", "--log-file", "-"]
