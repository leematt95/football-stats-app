# Use a lightweight official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy environment variables and requirements into the container
COPY requirements.txt .

# Install Python dependencies within the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code into the container
COPY app/ ./app/

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Set environment variables required by Flask
ENV FLASK_APP=app.main
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose the port that Flask will run on
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
