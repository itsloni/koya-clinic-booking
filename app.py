from flask import Flask, jsonify, request

app = Flask(__name__)

slots = []
bookings = []

@app.route("/")
def home():
    return jsonify({
        "message" : "Clinic Booking API",
        "status" : "Level 1 Under Construction"
    })

@app.route("/slots", methods=["GET"])
def get_slots():
    return jsonify({
        "slots": slots
    })

@app.route("/reset", methods=["POST"])
def reset_slots():
    data = request.get_json()

    if not data or "slots" not in data:
        return jsonify({"error" : "slots data is required"}), 400

    bookings.clear()
    slots[:] = data["slots"]
    return jsonify({"success" : "Slots have been reset to your New data"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

