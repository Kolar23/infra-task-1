from prometheus_client import Gauge, Summary, generate_latest
from flask import Flask, Response
import requests

urls = ["https://httpstat.us/503", "https://httpstat.us/200"]

sample_external_url_up = Gauge('sample_external_url_up', 'Indicates if external URL is up', ['url'])
sample_external_url_response_ms = Summary('sample_external_url_response_ms', 'Response time for external URL in ms', ['url'])

app = Flask(__name__)

def get_metrics():
    for url in urls:
        try:
            response = requests.get(url)

            if response.status_code == 200:
                print(f"URL: {url} is up")
                sample_external_url_up.labels(url).set(1)
            else:
                print(f"URL: {url} is down")
                sample_external_url_up.labels(url).set(0)

            sample_external_url_response_ms.labels(url).observe(response.elapsed.total_seconds() * 1000)

        except requests.exceptions.RequestException as e:
            print(f"Error when trying to make a request to {url}. Error: {e}")
            sample_external_url_up.labels(url).set(0)

@app.route('/metrics')
def display_metrics():
    get_metrics()
    return Response(generate_latest(), mimetype="text/plain")

@app.route('/')
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)