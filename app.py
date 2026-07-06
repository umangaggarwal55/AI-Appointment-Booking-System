from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

app = Flask(__name__)

CORS(app,
origins=[
    "https://eu1.make.com/"
])

# ✅ Webhook URL is safely stored in .env file — NOT in frontend code
WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/book", methods=["POST"])
def book_meeting():
    try:
        data = request.get_json()

        # Validate required fields
        required = ["name", "email", "meeting_title", "date", "time"]
        for field in required:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

        payload = {
            "name":          data["name"],
            "email":         data["email"],
            "meeting_title": data["meeting_title"],
            "date":          data["date"],
            "time":          data["time"],
            "notes":         data.get("notes", ""),
        }

        # 🔒 Webhook URL never leaves the server
        response = requests.get(WEBHOOK_URL, params=payload, timeout=10)

        print(f"✅ Webhook called | Status: {response.status_code} | Payload: {payload}")

        return jsonify({"success": True, "message": "Booking sent successfully!"})

    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "message": "Could not reach Make.com. Check your internet."}), 502
    except requests.exceptions.Timeout:
        return jsonify({"success": False, "message": "Make.com took too long to respond."}), 504
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ ERROR: MAKE_WEBHOOK_URL not set in .env file!")
    else:
        print("✅ Webhook URL loaded from .env")
        print("🚀 Server running at http://localhost:5000")
    app.run(debug=False, port=5000)
