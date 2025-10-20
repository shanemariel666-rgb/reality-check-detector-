from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HUGGINGFACE_API = "https://api-inference.huggingface.co/models/roberta-base-openai-detector"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    image_bytes = file.read()

    try:
        response = requests.post(
            HUGGINGFACE_API,
            headers=headers,
            data=image_bytes,
            timeout=30
        )

        # Log the raw output for debugging
        print("Hugging Face Response:", response.text)

        # Gracefully handle bad or empty responses
        if response.status_code != 200:
            return jsonify({"error": f"Hugging Face returned {response.status_code}"}), 500

        result = response.json()
        return jsonify({"success": True, "result": result})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/")
def home():
    return "<h2>Reality Check API is running ✅</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)