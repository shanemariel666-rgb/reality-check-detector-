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

    headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

    try:
        response = requests.post(
            HUGGINGFACE_API,
            headers=headers,
            data=image_bytes,
            timeout=60
        )

        if response.status_code == 404:
            return jsonify({"error": "Model not found (404). Try a different model URL."}), 404

        if response.status_code != 200:
            return jsonify({
                "error": f"Hugging Face API error {response.status_code}",
                "details": response.text
            }), 500

        try:
            data = response.json()
        except ValueError:
            return jsonify({"error": "Invalid JSON from Hugging Face"}), 502

        return jsonify(data)

    except requests.exceptions.Timeout:
        return jsonify({"error": "Hugging Face request timed out"}), 504
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route("/")
def home():
    return "<h2>Reality Check API is running ✅</h2>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)