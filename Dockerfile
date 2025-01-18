# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

# expose the port of the container
EXPOSE 8000

# Specify the command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
