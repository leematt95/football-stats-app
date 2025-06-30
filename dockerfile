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

# Set environment variables required by Flask
ENV FLASK_APP=app.main         
ENV FLASK_RUN_HOST=0.0.0.0     
ENV FLASK_RUN_PORT=5000        

# Set the default command to run the Flask development server
CMD ["flask", "run"]
