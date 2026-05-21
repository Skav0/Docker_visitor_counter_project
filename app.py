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

