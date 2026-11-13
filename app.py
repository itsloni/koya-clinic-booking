from flask import Flask, jsonify, request

app = Flask(__name__)

slot = []
bookings = []

@app.route("/")
def home():
    return "<h1>Clinic Booking API</h1><p>Level 1 is under construction</p>"

@app.route("/slot", methods=["GET"])
def slot():
    return "<h1>Slot Selecting/ Previewing </h1><p>Lets go</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

