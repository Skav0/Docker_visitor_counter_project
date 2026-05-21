📄 Project Requirements Document

# Project Title: Containerizing a Flask Web App with Redis Using Docker

📌 Objective
The goal of this project is to demonstrate your ability to containerize a Python web application using Docker and Docker Compose. 
You will set up a multi-container application that includes:
A Flask-based web app
A Redis key-value store
Persistent volumes
Environment variable configuration
Internal service communication via Docker networks

Note: The actual Flask application and HTML template are provided below (towards the end of the file). Your task focuses on Docker-related configuration and deployment.

🚧 Project Overview
You are provided with a basic visitor counter application code built using Flask and Redis. 

The app:
Increments and displays a visit counter
Logs each visitor’s country (via IP) and displays the country
Stores logs in Redis
Displays results in an HTML page

Your responsibility is to package and deploy this solution using Docker.

✅ Requirements
1. Dockerfile

Create a Dockerfile to:
Use a lightweight Python image (python:3.x-slim)
Install dependencies from requirements.txt
Copy application files into the container
Set appropriate environment variables
Expose the app on port 5000
Start the Flask app with host 0.0.0.0

2. requirements.txt

Must include at minimum:
Flask
redis
requests

3. .env File and Example
Use a .env file to store configuration variables:
FLASK_APP, FLASK_ENV, REDIS_HOST, REDIS_PORT
Use the env_file attribute in the docker compose YAML file to point to this file

4. docker-compose.yml
Must define two services:
web: your Flask app container
redis: Redis container
Use named volumes to persist Redis data
Use depends_on to control service order
Map web container port 5000 to any host port (e.g., 9000)
Load environment variables from .env

5. Volumes
Redis data should be stored persistently using Docker volumes (redis-data)
Volumes should be defined in docker-compose.yml

6. Networking
Containers must communicate over Docker’s default bridge network
The Flask app should use the hostname redis to reach Redis

⚠️ Constraints / Out of Scope
Do not write or modify the actual Flask logic or HTML/CSS templates.
Assume the Flask app (app.py) and templates are provided.

💯 Evaluation Criteria
Criteria	Points
Correct Dockerfile implementation	= 20 points
Valid Docker Compose configuration = 25 points
Use of environment variables = 10 points
Redis volume persistence = 10 points
Functional application via localhost = 10 points
Clean project structure and README = 10 points
GitHub best practices	= 15 points
Total	100

########### Application Code #############
import time
import redis
import requests
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def homepage():
    count = get_hit_count()

    ip = request.remote_addr
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # Get geolocation data
    geo_data = requests.get(f'http://ip-api.com/json/{ip}').json()
    country = geo_data.get('country', 'Unknown')
    country_code = geo_data.get('countryCode', 'ZZ')

    # Construct the flag emoji
    flag = chr(0x1F1E6 + ord(country_code[0]) - ord('A')) + chr(0x1F1E6 + ord(country_code[1]) - ord('A'))

    log_entry = f"{timestamp}|{ip}|{country}|{flag}"
    cache.lpush('visit_logs', log_entry)
    cache.ltrim('visit_logs', 0, 49)

    logs = cache.lrange('visit_logs', 0, 49)
    decoded_logs = [entry.decode('utf-8').split('|') for entry in logs]

    return render_template('index.html', count=count, logs=decoded_logs)

@app.route('/reset')
def reset_counter():
    cache.set('hits', 0)
    cache.delete('visit_logs')
    return redirect('/')


########### index.html file #################
<!DOCTYPE html>
<html>
<head>
    <title>DolfinED Visitor Counter</title>
    <style>
        body {
            background-color: #f4f4f4;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 40px;
        }
        .counter {
            font-size: 60px;
            margin: 20px auto;
            color: #333;
            padding: 20px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: fit-content;
        }
        .reset-button {
            display: inline-block;
            margin-top: 15px;
            padding: 8px 16px;
            font-size: 14px;
            background-color: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .reset-button:hover {
            background-color: #218838;
        }
        table {
            margin: 40px auto;
            border-collapse: collapse;
            width: 60%;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: center;
        }
        th {
            background-color: #eee;
        }
    </style>
</head>
<body>
    <h1>👋 Welcome to DolfinED Academy</h1>
    <div class="counter">
        🔢 Page visited <strong>{{ count }}</strong> times.
        <br>
        <a class="reset-button" href="/reset">🔁 Reset Counter</a>
    </div>

    <h2>🧾 Recent Visitors (Last 50)</h2>
    <table>
        <tr>
            <th>Timestamp (UTC)</th>
            <th>Country</th>
        </tr>
        {% for time, _, country, flag in logs %}
        <tr>
            <td>{{ time }}</td>
            <td>{{ flag }} {{ country }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>

