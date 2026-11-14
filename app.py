from flask import Flask, jsonify, request
from datetime import datetime, timezone
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

@app.route("/bookings", methods=["POST"])
def input_bookings():
    data = request.get_json()

    if not data or "slot_id" not in data or "name" not in data or "email"not in data:

        return jsonify({"error" : "bookings data is required"}), 400

    for slot in slots:
        if data["slot_id"] == slot["id"]:
            new_booking = {
                "user_id" : f"User_{len(bookings) + 1}",
                "slot_id" : data["slot_id"],
                "name" : data["name"],
                "email" : data["email"],
                "status" : "confirmed",
                "created_at" : datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            bookings.append(new_booking)
            return jsonify(new_booking), 201

    return jsonify({"error" : "slot not found"}), 404

@app.route("/bookings", methods=["GET"])
def






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

