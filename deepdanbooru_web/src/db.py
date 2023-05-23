import os
import sqlite3
from sqlite3 import Error

# SQLite database configuration
DATABASE_FILE = "db/shimarin.db"
TABLE_NAME = "events"
SQL_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS {} (
        event_id TEXT PRIMARY KEY,
        file_hash TEXT,
        tags TEXT
    );
""".format(TABLE_NAME)


def create_database():
    """Create a SQLite database and the events table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(SQL_CREATE_TABLE)
        conn.commit()
    except Error as e:
        print(f"Error creating the database: {e}")
    finally:
        if conn:
            conn.close()


def update_tags(event_id, tags):
    """Update the tags for the specified event ID in the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE {} SET tags = ? WHERE event_id = ?".format(TABLE_NAME), (tags, event_id))
        conn.commit()
    except Error as e:
        print(f"Error updating tags in the database: {e}")
    finally:
        if conn:
            conn.close()


def store_event(event_id, file_hash):
    """Store the event details in the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO {} (event_id, file_hash, tags) VALUES (?, ?, '')".format(TABLE_NAME), (event_id, file_hash))
        conn.commit()
    except Error as e:
        print(f"Error storing event in the database: {e}")
    finally:
        if conn:
            conn.close()


def get_tags(event_id):
    """Retrieve the tags for the specified event ID from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT tags FROM {} WHERE event_id = ?".format(TABLE_NAME), (event_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error retrieving tags from the database: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_event_id(file_hash):
    """Retrieve the tags for the specified event ID from the database."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT event_id FROM {} WHERE file_hash = ?".format(TABLE_NAME), (file_hash,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error retrieving event_id from the database: {e}")
        return None
    finally:
        if conn:
            conn.close()


os.makedirs("db", exist_ok=True)
create_database()
