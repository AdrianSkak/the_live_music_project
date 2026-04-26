from psycopg import connect

from app.config import DATABASE_URL


def get_connection():
    return connect(DATABASE_URL)