# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy requirement list and install them
COPY .env .
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Flask app into the container
COPY app/ ./app/

# Set the default command to run the app
CMD ["python", "app/main.py"]
