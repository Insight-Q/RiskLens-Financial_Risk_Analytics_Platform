import os
import pickle
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Model load ──────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(
    os.path.join(BASE_DIR, 'best_model_compressed.joblib')
)

with open(os.path.join(BASE_DIR, 'feature_names.pkl'), 'rb') as f:
    feature_names = pickle.load(f)

print("Model loaded successfully!")
print("Features:", feature_names)

# ── Assigned risk label ───────────────────────────────
def get_risk_label(score):
    if score < 30:
        return "Low Risk"
    elif score < 60:
        return "Medium Risk"
    else:
        return "High Risk"

# ── GET /health ──────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "RiskLens API is running"
    })

# ── GET /model-info ──────────────────────────────────────
@app.route('/model-info', methods=['GET'])
def model_info():
    return jsonify({
        "model_name": type(model).__name__,
        "features": feature_names,
        "roc_auc": "0.87+",
        "dataset": "150,000 customers",
        "description": "Loan Default Prediction Model"
    })

# ── POST /predict ─────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        missing = [f for f in feature_names if f not in data]
        if missing:
            return jsonify({
                "error": f"Missing fields: {missing}"
            }), 400

        input_df = pd.DataFrame([data])[feature_names]

        prob = model.predict_proba(input_df)[0][1]
        risk_score = round(prob * 100, 1)
        risk_label = get_risk_label(risk_score)

        return jsonify({
            "risk_score": risk_score,
            "risk_label": risk_label,
            "default_probability": round(prob, 4),
            "input_received": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Run ───────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)