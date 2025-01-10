# Use the official Python image from the Docker Hub
FROM python:3.12.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /code/

# Expose the port if needed (optional)
# EXPOSE 8000

# Run the watch.py script
CMD ["python", "watch.py"]
