from flask import Flask, jsonify, request
from datetime import datetime, timezone
app = Flask(__name__)
API_KEY = "loni-secret-api-key-123"
slots = []
bookings = []
idempotency = {}

def require_api_key():
    key = request.headers.get("X-API-key")
    if key != API_KEY:
        return jsonify({"error" : "Unauthorized"}), 401
    return None
@app.route("/")
def home():
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    return jsonify({
        "message" : "Clinic Booking API",
        "status" : "Level 1 Under Construction"
    })

@app.route("/slots", methods=["GET"])
def get_slots():
    auth_error = require_api_key()
    if auth_error:
        return auth_error

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
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()

    if not data or "slots" not in data:
        return jsonify({"error" : "slots data is required"}), 400

    bookings.clear()
    slots[:] = data["slots"]
    return jsonify({"success" : "Slots have been reset to your New data"})

@app.route("/bookings", methods=["POST"])
def input_bookings():
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()

    if (not data or
        "slot_id" not in data or not data["slot_id"] or
        "name" not in data or not data["name"] or
        "email" not in data or not data["slot_id"]):

        return jsonify({"error" : "bookings data is required"}), 400

    for slot in slots:
        if data["slot_id"] == slot["id"]:

            for booking in bookings:

                if booking["slot_id"] == data["slot_id"] and booking["status"] == "confirmed":
                    return jsonify({"error": "slot already taken"}), 409
            new_booking = {
                "id" : f"user_{len(bookings) + 1}",
                "slot_id" : data["slot_id"],
                "name" : data["name"],
                "email" : data["email"],
                "status" : "confirmed",
                "created_at" : datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            bookings.append(new_booking)
            return jsonify(new_booking), 201



    return jsonify({"error" : "slot not found"}), 404

@app.route("/bookings/<booking_id>", methods=["GET"])
def view_bookings(booking_id):
    auth_error = require_api_key()
    if auth_error:
        return auth_error

    for booking in bookings:
        if booking["id"] == booking_id:
            return jsonify(booking), 200

    return jsonify({"error" : "booking not found"}), 404

@app.route("/bookings/<booking_id>", methods=["DELETE"])
def del_bookings(booking_id):
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    for booking in bookings:
        if booking["id"] == booking_id:
            booking["status"] = "cancelled"
            return jsonify({"success" : "your booked slot has been cancelled"}), 200
    return jsonify({"error" : "booking does not exist"}), 404


@app.route("/bookings", methods=["GET"])
def email_bookings():
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    email_list = []
    email = request.args.get("email")

    if not email:
        return jsonify({"error" : "email is required"}), 400
    for booking in bookings:
        if booking["email"] == email:
            email_list.append(booking)
        return jsonify({"error" : "email does not exist"}), 404
    return jsonify({"email owned bookings" : email_list}), 200













if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

