from flask import Flask, request, jsonify
import sys
import os

# Point Python to your orchestrator script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'skills/audit-orchestrator/scripts')))
from run_audit import run_orchestrator

app = Flask(__name__)

@app.route('/')
def home():
    return "Marketplace API is running. Go to /audit?url=YOUR_URL to test."

@app.route('/audit', methods=['GET'])
def audit():
    target = request.args.get('url')
    if not target:
        return jsonify({"error": "Please provide a URL parameter, e.g., ?url=https://example.com"}), 400
    
    # Run your existing marketplace logic
    result = run_orchestrator(target)
    return jsonify(result)

if __name__ == '__main__':
    # Port 10000 is required by Render's free tier
    app.run(host='0.0.0.0', port=10000)