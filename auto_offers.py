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
# GITHUB API URL
# =========================
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_OFFERS_PATH}"

# =========================
# ADD OFFER
# =========================
def add_offer(
    title,
    description,
    price
):

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # =========================
    # GET CURRENT FILE
    # =========================
    response = requests.get(
        API_URL,
        headers=headers
    )

    if response.status_code != 200:

        print("GitHub Read Error")

        return False

    data = response.json()

    sha = data["sha"]

    content = base64.b64decode(
        data["content"]
    ).decode("utf-8")

    offers = json.loads(
        content
    )

    # =========================
    # CHECK DUPLICATES
    # =========================
    for offer in offers:

        if (
            offer["title"] == title
            and
            offer["description"] == description
        ):

            return False

    # =========================
    # NEW OFFER
    # =========================
    new_offer = {

        "title": title,

        "description": description,

        "price": str(price),

        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )
    }

    offers.append(
        new_offer
    )

    # =========================
    # ENCODE FILE
    # =========================
    updated_content = json.dumps(
        offers,
        ensure_ascii=False,
        indent=4
    )

    encoded_content = base64.b64encode(
        updated_content.encode("utf-8")
    ).decode("utf-8")

    # =========================
    # PUSH TO GITHUB
    # =========================
    payload = {

        "message": f"New offer: {title}",

        "content": encoded_content,

        "sha": sha
    }

    push = requests.put(
        API_URL,
        headers=headers,
        json=payload
    )

    if push.status_code in [200, 201]:

        print("Offer uploaded to GitHub")

        return True

    print(push.text)

    return False

