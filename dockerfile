# Using a specific Python version on the required AMD64 platform
FROM --platform=linux/amd64 python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main processing script
COPY process_pdfs.py .

# Set the command to execute when the container starts
CMD ["python", "process_pdfs.py"]
