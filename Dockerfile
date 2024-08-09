# Use an official Python runtime as a parent image
FROM python:3.12

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    libgl1-mesa-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Command to run the application
CMD ["streamlit", "run", "app.py"]
