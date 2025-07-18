# Use a lightweight official Python image as the base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and import script
COPY app/    ./app/
COPY import_players.py .

# Copy (and make executable) the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the port that Flask will run on
EXPOSE 5000

# Entrypoint runs import then starts Flask
ENTRYPOINT ["/app/entrypoint.sh"]
# Start the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]     # Run on all interfaces

# Note: Flask will automatically use the app.py file as the application entry point
#       if the FLASK_APP environment variable is set to "app.py" (default behavior).
#       If you want to specify it explicitly, you can set it in the Dockerfile:
# ENV FLASK_APP=app.py
#       But this is not necessary if the file is named app.py and Flask is run in the same directory.
#       Flask will automatically discover it.
#       The entrypoint script will handle the import and then start the Flask server.
#       This allows the import script to run before the Flask app starts.
#       The entrypoint script is responsible for running the import_players.py script before starting the Flask server.
#       This ensures that the database is populated with player data before the application starts serving requests.
#       The entrypoint script is executed when the container starts, allowing for any necessary setup before running the application.
#       The entrypoint script is a shell script that runs the import script and then starts the Flask server.
#       The entrypoint script is responsible for running the import_players.py