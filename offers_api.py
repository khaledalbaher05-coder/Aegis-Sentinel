from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

OFFERS_FILE = "/home/khaled/landing_page/offers.json"

# =========================
# LOAD OFFERS
# =========================
def load_offers():

    if not os.path.exists(OFFERS_FILE):

        with open(OFFERS_FILE, "w") as f:
            json.dump([], f)

    with open(OFFERS_FILE, "r") as f:
        return json.load(f)

# =========================
# SAVE OFFERS
# =========================
def save_offers(data):

    with open(OFFERS_FILE, "w") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

# =========================
# GET OFFERS
# =========================
@app.route("/offers", methods=["GET"])
def get_offers():

    return jsonify(
        load_offers()
    )

# =========================
# ADD OFFER
# =========================
@app.route("/add_offer", methods=["POST"])
def add_offer():

    data = request.json

    title = data.get("title")
    description = data.get("description")
    price = data.get("price")

    offers = load_offers()

    offers.append({

        "title": title,

        "description": description,

        "price": price,

        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

    })

    save_offers(
        offers
    )

    return jsonify({

        "status": "success"

    })

# =========================
# RUN
# =========================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
