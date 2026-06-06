import requests
import time

from bot.config import WALLET_ADDRESS

from bot.database import (
    connect_db,
    activate_subscription
)

TRON_API = (
    "https://apilist.tronscanapi.com/api/transaction"
)


# =========================
# GET PENDING PAYMENTS
# =========================
def get_pending_payments():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, user_id, service_name, amount
        FROM orders
        WHERE status = 'pending'
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


# =========================
# MARK PAYMENT SUCCESS
# =========================
def mark_payment_success(order_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET status = 'paid'
        WHERE id = ?
        """,
        (order_id,)
    )

    conn.commit()
    conn.close()


# =========================
# CHECK BLOCKCHAIN
# =========================
def check_transactions():

    try:

        url = (
            f"{TRON_API}"
            f"?address={WALLET_ADDRESS}"
        )

        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        transactions = data.get(
            "data",
            []
        )

        pending = get_pending_payments()

        for payment in pending:

            order_id = payment[0]
            user_id = payment[1]
            service_name = payment[2]
            amount = float(payment[3])

            for tx in transactions:

                try:

                    tx_amount = (
                        float(
                            tx.get("amount", 0)
                        ) / 1000000
                    )

                    if round(tx_amount, 2) == round(amount, 2):

                        activate_subscription(
                            user_id,
                            service_name
                        )

                        mark_payment_success(
                            order_id
                        )

                        print(
                            f"[+] Payment confirmed "
                            f"for user {user_id}"
                        )

                except:
                    continue

    except Exception as e:

        print(
            "[ERROR]",
            e
        )


# =========================
# LOOP
# =========================
def start_checker():

    print(
        "[+] Payment checker started..."
    )

    while True:

        check_transactions()

        time.sleep(20)


# =========================
# START
# =========================
if __name__ == "__main__":

    start_checker()
