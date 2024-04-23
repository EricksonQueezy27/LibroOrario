# Use an official Python runtime as a parent image
FROM python:3.9-slim


# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y python3-dev
# Create a virtual environment and activate it
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt\
    python manage.py collectstatic\
    python manage.py makemigrations && \
    python manage.py migrate && \
# Make port 80 available to the world outside this container

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["gunicorn config.wsgi--log-file -"]
EXPOSE 8000