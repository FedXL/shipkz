FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy only the requirements file first
COPY req.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the rest of the application code
COPY . /app/

# Set environment variables to avoid buffering and enable logging
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1