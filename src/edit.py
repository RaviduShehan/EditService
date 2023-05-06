from datetime import datetime
import os
import time
from flask import Flask, request, jsonify
import openai
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials
from prometheus_client import Counter, Gauge, start_http_server

# Setup Firebase credentials
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)
database = os.environ.get('FIREBASE_DATABASE_COLLECTION')

# Load OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Initialize Firestore client with explicit project ID
project_id = "apiservices-384019"
db = firestore.Client(project=project_id)

# Define metrics
requests_total = Counter('requests_total', 'Total number of requests')
request_duration_seconds = Gauge('request_duration_seconds', 'Duration of request in seconds')

app = Flask(__name__)

@app.route('/')
def edit():
    # Increment request counter and start timing request
    requests_total.inc()
    start_time = time.time()

    # Add service name, status, and timestamp to Firestore
    service_ref = db.collection(database).document('EditService_Status')
    print("Edit Service starting...")
    service_data = {
        'service_name': 'Edit',
        'status': 'Starting',
        'timestamp': datetime.now()
    }
    service_ref.set(service_data)
    prompt = request.args.get('prompt')
    if not prompt:
        service_ref.update({'status': 'Empty prompt'})
        return jsonify(error="Prompt parameter is missing"), 400
    service_ref.update({'status': 'Running'})
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.5
        )
        # Record request duration and return response
        request_duration_seconds.observe(time.time() - start_time)
        return jsonify(response=response.choices[0].text.strip())
    except Exception as e:
        # Update service status to 'error' if an exception occur
        service_ref.update({'status': 'Error'})
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    # Start HTTP server for metrics exposition
    start_http_server(8000)

    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5003)
