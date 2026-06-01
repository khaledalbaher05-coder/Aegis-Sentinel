import sqlite3

DB_NAME = "database.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tx_hash TEXT PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()


def create_user(user_id):
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        INSERT OR IGNORE INTO users (user_id, balance)
        VALUES (?, 0)
        """, (user_id,))

        conn.commit()


def get_user_balance(user_id):
    create_user(user_id)

    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        SELECT balance FROM users
        WHERE user_id = ?
        """, (user_id,))

        res = c.fetchone()

        return res[0] if res else 0


def add_balance(user_id, amount):
    create_user(user_id)

    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        UPDATE users
        SET balance = balance + ?
        WHERE user_id = ?
        """, (amount, user_id))

        conn.commit()


def deduct_balance(user_id, amount):
    create_user(user_id)

    current_balance = get_user_balance(user_id)

    if current_balance < amount:
        return False

    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        UPDATE users
        SET balance = balance - ?
        WHERE user_id = ?
        """, (amount, user_id))

        conn.commit()

    return True


def get_all_services():
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        SELECT id, name, price FROM services
        """)

        return c.fetchall()


def transaction_exists(tx_hash):
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        SELECT tx_hash FROM transactions
        WHERE tx_hash = ?
        """, (tx_hash,))

        return c.fetchone() is not None


def save_transaction(tx_hash, user_id, amount):
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("""
        INSERT INTO transactions (
            tx_hash,
            user_id,
            amount
        )
        VALUES (?, ?, ?)
        """, (tx_hash, user_id, amount))

        conn.commit()
