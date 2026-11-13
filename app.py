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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

