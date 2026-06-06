from flask import (
    Flask,
    jsonify,
    request
)

from flask_cors import CORS

import json
import base64
import requests

from datetime import datetime

from bot.config import (
    GITHUB_TOKEN,
    GITHUB_REPO,
    GITHUB_OFFERS_PATH
)


# =========================
# APP
# =========================
app = Flask(__name__)

CORS(app)


# =========================
# GITHUB API
# =========================
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_OFFERS_PATH}"


# =========================
# HOME
# =========================
@app.route("/")
def home():

    return jsonify({

        "status": "online",

        "message": "AEGIS DASHBOARD API"
    })


# =========================
# GET OFFERS
# =========================
@app.route("/offers")
def get_offers():

    headers = {

        "Authorization": f"token {GITHUB_TOKEN}"
    }

    response = requests.get(
        API_URL,
        headers=headers
    )

    data = response.json()

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    offers = json.loads(
        content
    )

    return jsonify(
        offers
    )


# =========================
# ADD OFFER
# =========================
@app.route(
    "/add_offer",
    methods=["POST"]
)
def add_offer():

    data = request.json

    title = data.get(
        "title"
    )

    description = data.get(
        "description"
    )

    price = data.get(
        "price"
    )

    headers = {

        "Authorization": f"token {GITHUB_TOKEN}"
    }

    # =========================
    # GET CURRENT FILE
    # =========================
    response = requests.get(
        API_URL,
        headers=headers
    )

    github_data = response.json()

    sha = github_data["sha"]

    content = base64.b64decode(
        github_data["content"]
    ).decode("utf-8")

    offers = json.loads(
        content
    )

    # =========================
    # NEW OFFER
    # =========================
    offers.append({

        "title": title,

        "description": description,

        "price": price,

        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    })

    # =========================
    # UPDATE FILE
    # =========================
    updated_content = json.dumps(
        offers,
        ensure_ascii=False,
        indent=4
    )

    encoded_content = base64.b64encode(
        updated_content.encode("utf-8")
    ).decode("utf-8")

    payload = {

        "message": f"Add offer: {title}",

        "content": encoded_content,

        "sha": sha
    }

    push = requests.put(
        API_URL,
        headers=headers,
        json=payload
    )

    if push.status_code in [200, 201]:

        return jsonify({

            "success": True
        })

    return jsonify({

        "success": False
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )

