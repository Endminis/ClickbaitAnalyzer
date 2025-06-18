import psycopg2
from psycopg2 import sql, OperationalError
from config import DB_CONFIG

def get_connection(dbname=None):
    cfg = DB_CONFIG.copy()
    if dbname:
        cfg['database'] = dbname
    return psycopg2.connect(
        host=cfg['host'], port=cfg['port'],
        user=cfg['user'], password=cfg['password'],
        dbname=cfg['database']
    )

def init_db():
    """
    Ініціалізація бази даних: створення БД та необхідних таблиць.
    """
    host, port, user, password, dbname = (
        DB_CONFIG['host'], DB_CONFIG['port'],
        DB_CONFIG['user'], DB_CONFIG['password'],
        DB_CONFIG['database']
    )
    # Створення бази, якщо не існує
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname='postgres')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        if not cur.fetchone():
            cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(dbname)))
        cur.close()
        conn.close()
    except OperationalError as e:
        print(f"[Error] База '{dbname}' недоступна: {e}")
        exit(1)
    # Створення таблиць у новоствореній базі
    try:
        conn = get_connection(dbname)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS classification_results (
                id SERIAL PRIMARY KEY,
                user_login TEXT NOT NULL,
                title TEXT NOT NULL,
                probability REAL NOT NULL,
                is_clickbait BOOLEAN NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS extension_results (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                probability REAL NOT NULL,
                is_clickbait BOOLEAN NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        cur.close()
        conn.close()
    except OperationalError as e:
        print(f"[Error] Не вдалося створити таблиці: {e}")
        exit(1)