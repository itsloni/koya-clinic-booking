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
    result = []

    for slot in slots:
        is_available = True

        for booking in bookings:
            if slot["id"] == booking["slot_id"] and booking["status"] == "confirmed":
                is_available = False
                break

        slot_copy = slot.copy()
        slot_copy["available"] = is_available
        result.append(slot_copy)

    return jsonify({"slots" : result})

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

            for booking in bookings:

                if booking["slot_id"] == data["slot_id"] and booking["status"] == "confirmed":
                    return jsonify({"error": "slot already taken"}), 409
            new_booking = {
                "id" : f"User_{len(bookings) + 1}",
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
def view_bookings():








if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

