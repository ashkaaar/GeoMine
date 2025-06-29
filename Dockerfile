# Use official Python base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Make the bash script executable
RUN chmod +x run_pipeline.sh

# Default command to run your pipeline script
CMD ["./run_pipeline.sh"]

