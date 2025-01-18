# Use the official Python image from the Docker Hub
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1  

# Set the working directory in the container
WORKDIR /app

# Copy the rest of your application code into the container
COPY . /app/

RUN pip install Django psycopg2-binary httpx django-ratelimit djangorestframework-simplejwt python-dotenv djangorestframework asyncio


# expose the port of the container
EXPOSE 8000

# Specify the command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
