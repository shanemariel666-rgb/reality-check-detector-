from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Hive API key (set as environment variable in Vercel)
HIVE_API_KEY = os.getenv("HIVE_API_KEY", "YOUR_HIVE_API_KEY_HERE")

@app.route('/')
def home():
    try:
        with open('index.html', 'r') as f:
            return render_template_string(f.read())
    except Exception as e:
        return f"<h1>Error loading homepage</h1><p>{str(e)}</p>"

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        # Send the file to Hive AI
        files = {'media': (file.filename, file.stream, file.mimetype)}
        headers = {"Authorization": f"Token {HIVE_API_KEY}"}

        response = requests.post(
            "https://api.thehive.ai/api/v2/task/sync",
            headers=headers,
            files=files,
            timeout=60
        )

        # Check if the response is valid JSON
        try:
            data = response.json()
        except ValueError:
            return jsonify({
                "error": "Hive API did not return valid JSON.",
                "status_code": response.status_code,
                "text": response.text
            }), 500

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)