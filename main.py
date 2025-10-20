from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ✅ Use your Hugging Face API key here (stored in environment variables)
HF_API_KEY = os.getenv("HF_API_KEY")

@app.route('/')
def home():
    return 'Reality Check API is running. Use /analyze endpoint.'

@app.route('/analyze', methods=['POST'])
def analyze():
    # Check if file was sent
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Send file to Hugging Face AI detector model
        response = requests.post(
            "https://api-inference.huggingface.co/models/umm-maybe/AI-image-detector",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            files={"file": (file.filename, file, file.content_type)},
            timeout=60
        )

        # Try to parse Hugging Face response safely
        try:
            data = response.json()
        except Exception:
            return jsonify({"error": "Failed to parse response from AI model"}), 500

        # Handle cases where model fails or errors
        if response.status_code != 200:
            return jsonify({"error": "AI model error", "details": data}), 500

        return jsonify({"result": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)