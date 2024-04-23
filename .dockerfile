# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y python3-dev

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Create a virtual environment and activate it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Run migrations and collectstatic
RUN python manage.py collectstatic --noinput && \
    python manage.py makemigrations && \
    python manage.py migrate

# Expose port 8000
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run Gunicorn when the container launches
CMD ["gunicorn", "Libro01.wsgi", "--bind", "0.0.0.0:8000", "--log-file", "-"]
