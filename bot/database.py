import sqlite3

DB_NAME = "bot_data.db"


# =========================
# CONNECT DATABASE
# =========================
def connect_db():

    return sqlite3.connect(DB_NAME)


# =========================
# INIT DATABASE
# =========================
def init_db():

    conn = connect_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        username TEXT,
        balance REAL DEFAULT 0
    )
    """)

    # SERVICES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL
    )
    """)

    # ORDERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_name TEXT,
        amount REAL,
        status TEXT
    )
    """)

    conn.commit()

    # =========================
    # DEFAULT SERVICES
    # =========================
    cursor.execute(
        "SELECT COUNT(*) FROM services"
    )

    count = cursor.fetchone()[0]

    if count == 0:

        services = [

            (
                "🛡️ Aegis Basic Shield",
                "حماية أساسية للمجموعات",
                29
            ),

            (
                "⚡ Aegis Pro Security",
                "Anti Spam + Link Block",
                59
            ),

            (
                "👑 Aegis Elite Defense",
                "حماية متقدمة كاملة",
                149
            ),

            (
                "🌐 Dark Web Monitoring",
                "مراقبة التسريبات",
                79
            ),

            (
                "🔎 OSINT Intelligence",
                "تحليل معلومات استخباراتية",
                99
            ),

            (
                "💣 Penetration Testing",
                "اختبار اختراق احترافي",
                199
            )
        ]

        cursor.executemany(
            """
            INSERT INTO services
            (name, description, price)
            VALUES (?, ?, ?)
            """,
            services
        )

    conn.commit()
    conn.close()


# =========================
# ADD USER
# =========================
def add_user(
    user_id,
    username
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, username)
        VALUES (?, ?)
        """,
        (
            user_id,
            username
        )
    )

    conn.commit()
    conn.close()


# =========================
# REGISTER USER
# =========================
def register_user(
    user_id,
    username
):

    add_user(
        user_id,
        username
    )


# =========================
# GET ALL SERVICES
# =========================
def get_all_services():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM services"
    )

    services = cursor.fetchall()

    conn.close()

    return services


# =========================
# CREATE ORDER
# =========================
def create_order(
    user_id,
    service_name,
    amount=0,
    status="pending"
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (user_id, service_name, amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            service_name,
            amount,
            status
        )
    )

    conn.commit()
    conn.close()


# =========================
# SAVE PAYMENT
# =========================
def save_payment(
    user_id,
    service_name,
    amount,
    txid
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (user_id, service_name, amount, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            service_name,
            amount,
            "paid"
        )
    )

    conn.commit()
    conn.close()

    activate_subscription(
        user_id,
        service_name
    )


# =========================
# ACTIVATE SUBSCRIPTION
# =========================
def activate_subscription(
    user_id,
    service_name
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET balance = balance + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()


# =========================
# GET USER BALANCE
# =========================
def get_user_balance(
    user_id
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT balance
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return 0


# =========================
# UPDATE BALANCE
# =========================
def update_balance(
    user_id,
    amount
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET balance = ?
        WHERE user_id = ?
        """,
        (
            amount,
            user_id
        )
    )

    conn.commit()
    conn.close()


# =========================
# DEDUCT BALANCE
# =========================
def deduct_balance(
    user_id,
    amount
):

    balance = get_user_balance(
        user_id
    )

    new_balance = balance - amount

    if new_balance < 0:
        new_balance = 0

    update_balance(
        user_id,
        new_balance
    )


# =========================
# GET USERS COUNT
# =========================
def get_users_count():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =========================
# GET ORDERS COUNT
# =========================
def get_orders_count():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


# =========================
# GET TOTAL PAYMENTS
# =========================
def get_total_payments():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SUM(amount)
        FROM orders
        WHERE status = 'paid'
        """
    )

    result = cursor.fetchone()[0]

    conn.close()

    if result:
        return result

    return 0


# =========================
# GET ALL ORDERS
# =========================
def get_all_orders():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM orders"
    )

    orders = cursor.fetchall()

    conn.close()

    return orders


# =========================
# ADD SERVICE
# =========================
def add_service(
    name,
    description,
    price
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO services
        (name, description, price)
        VALUES (?, ?, ?)
        """,
        (
            name,
            description,
            price
        )
    )

    conn.commit()
    conn.close()

