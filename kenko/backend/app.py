from flask import Flask, jsonify, request
from flask_cors import CORS
from simulation import LASimulation
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Backend!"})

# Global simulation instance.
sim = LASimulation()

@app.route("/api/reset", methods=["POST"])
def reset_simulation():
    sim.reset_simulation()
    return jsonify({"status": "Simulation reset", "state": sim.get_simulation_state()})

@app.route("/api/simulate", methods=["GET"])
def get_simulation_state():
    return jsonify(sim.get_simulation_state())

@app.route("/api/step", methods=["POST"])
def step_simulation():
    data = request.get_json()
    if data and "action" in data:
        action = data["action"]
        note = sim.apply_rl_action(action)
    else:
        note = "No RL action applied."
    sim.update_simulation()
    return jsonify({
        "status": "Step completed",
        "actionNote": note,
        "state": sim.get_simulation_state()
    })

@app.route("/api/plan", methods=["GET"])
def get_plan():
    if os.path.exists("policy_plan.json"):
        with open("policy_plan.json", "r") as f:
            plan = json.load(f)
    else:
        plan = []
    return jsonify({"plan": plan})

@app.route("/api/gemini-suggestions", methods=["GET"])
def get_gemini_suggestions():
    suggestions = sim.get_gemini_suggestions()
    return jsonify(suggestions)

@app.route("/api/hospital_history", methods=["GET"])
def get_hospital_history():
    return jsonify(sim.hospital_history)

@app.route("/api/share_info", methods=["POST"])
def share_info():
    info = request.get_json()
    from mongodb_helper import insert_patient_info
    result = insert_patient_info(info)
    return jsonify({"status": "Info shared", "inserted_id": str(result.inserted_id)})

@app.route("/api/patient_info", methods=["GET"])
def get_info():
    from mongodb_helper import get_patient_info
    info = get_patient_info()
    return jsonify(info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
