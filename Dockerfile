# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir pika


# Define environment variable
ENV PYTHONUNBUFFERED=1

# Set execute permissions for the working directory
RUN chmod -R 755 /app

# Run the Python script when the container launches
CMD ["python", "consumer.py"]