from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# ===============================
# ROUTES
# ===============================

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login():
    return send_from_directory('.', 'login.html')

@app.route('/register')
def register():
    return send_from_directory('.', 'register.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

# Test route to confirm backend is running
@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "message": "Reality Check backend running!"})

# Upload route (for images/videos)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    path = os.path.join(upload_folder, file.filename)
    file.save(path)

    # Placeholder for analysis logic
    return jsonify({"message": f"File '{file.filename}' uploaded successfully!"})

# ===============================
# START SERVER
# ===============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
import time

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    filename = file.filename

    # (For now, simulate analysis)
    time.sleep(2)
    result = {
        "filename": filename,
        "authenticity_score": "98.7%",
        "verdict": "Likely authentic",
        "details": "No manipulation detected in metadata or visual noise patterns."
    }
    return jsonify(result)
    app.run(host="0.0.0.0", port=port)
