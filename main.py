from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Replace this with your actual Hive API key
HIVE_API_KEY = os.getenv("HIVE_API_KEY", "YOUR_HIVE_API_KEY_HERE")

@app.route('/')
def home():
    return render_template_string(open('index.html').read())

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    files = {'media': (file.filename, file.stream, file.mimetype)}
    headers = {"Authorization": f"Token {HIVE_API_KEY}"}

    response = requests.post(
        "https://api.thehive.ai/api/v2/task/sync",
        headers=headers,
        files=files
    )

    if response.status_code == 200:
        result = response.json()
        return jsonify(result)
    else:
        return jsonify({
            "error": "Hive API request failed",
            "details": response.text
        }), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)