from flask import Flask, jsonify, request
from datetime import datetime, timezone
from time import time
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
API_KEY = "loni-secret-api-key-123"
slots = []
bookings = []
idempotency_keys = {}
rate_limit = {}

def require_api_key():
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"error" : "Unauthorized"}), 401
    return None
@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/slots", methods=["GET"])
def get_slots():
    auth_error = require_api_key()
    if auth_error:
        return auth_error
    result = []
    provider_filter = request.args.get("provider")

    for slot in slots:

        if provider_filter and slot["provider"] != provider_filter:
            continue

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
        "email" not in data or not data["email"]):

        return jsonify({"error" : "bookings data is required"}), 400

    data["email"] = data["email"].strip().lower()
    data["name"] = data["name"].strip()
    idem_key = request.headers.get("idempotency-key")
    if idem_key and idem_key in idempotency_keys:
        old_booking = idempotency_keys[idem_key]
        if (old_booking["slot_id"] != data["slot_id"] or
            old_booking["name"] != data["name"] or
            old_booking["email"] != data["email"]):

            return jsonify({"error" : "Idempotency-Key reused with a different body"}), 422

        return jsonify(old_booking), 200

    current_time = time()
    email = data["email"]

    attempts = rate_limit.get(email, [])

    attempts = [t for t in attempts if current_time - t < 60]

    if len(attempts) >= 5:
        return jsonify({"error" : "Too many requests"}), 429, {"Retry-After" : "60"}

    attempts.append(current_time)
    rate_limit[email] = attempts

    for slot in slots:
        if data["slot_id"] == slot["id"]:
            slot_start = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)

            if slot_start < now:
                return jsonify({"error": "slot has already started"}), 400

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
            if idem_key:
                idempotency_keys[idem_key] = new_booking
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
            return jsonify(booking), 200
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

    limit = request.args.get("limit", 10)

    try:
        limit = int(limit)
    except TypeError:
        return jsonify({"error": "limit must be a number"}), 400
    if limit < 1 or limit > 50:
        return jsonify({"error": "limit must be between 1 and 50"}), 400

    cursor = request.args.get("cursor")

    for booking in bookings:
        if booking["email"].strip().lower() == email:
            email_list.append(booking)
    if not email_list:
        return jsonify({"error" : "email does not exist"}), 404

    email_list.sort(key=lambda x:x["created_at"])

    if cursor:
        start_index = 0
        for i, booking in enumerate(email_list):
            if booking["id"] == cursor:
                start_index = i + 1
                break
        email_list = email_list[start_index:]

    paginated = email_list[:limit]

    next_cursor = None
    if len(email_list) > limit:
        next_cursor = paginated[-1]["id"]

    return jsonify({
        "bookings" : paginated,
        "next_cursor" : next_cursor
    }), 200














if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

