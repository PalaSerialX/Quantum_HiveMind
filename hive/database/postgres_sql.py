import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime


# Load the environment variables
load_dotenv()

# Set up OpenAI API credentials
password = os.getenv("POSTGRES_PASS")


class BaseDatabase:
    def __init__(self):
        self.host = "localhost"
        self.database = "postgres"
        self.user = "postgres"
        self.password = password

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()


class CherryDatabase(BaseDatabase):
    def insert_cherry(self, unique_task_id, title, url, timestamp=datetime.now(),
                      keywords=None, priority=None, is_cherry=False, status="Active", scraped_text=None):
        self.connect()
        self.cur.execute(
            "INSERT INTO search_results (uniquetaskid, Title, URL, IsCherry, Keywords, Timestamp, "
            "Priority, Status, scraped_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (unique_task_id, title, url, is_cherry, keywords, timestamp, priority, status, scraped_text))
        self.conn.commit()
        self.close()

    def fetch_cherries(self):
        self.connect()
        self.cur.execute("SELECT * FROM search_results")
        rows = self.cur.fetchall()
        self.close()
        return rows

    def update_cherry_status_by_title(self, title, status="Active", is_cherry=True):
        self.connect()
        query = "UPDATE search_results SET Status = %s, IsCherry = %s WHERE LOWER(title) LIKE %s"
        self.cur.execute(query, (status, is_cherry, f"%{title.lower()}%"))
        updated_rows = self.cur.rowcount
        self.conn.commit()
        self.close()

    def update_cherry_scraped_text(self, url, scraped_text):
        self.connect()
        self.cur.execute(
            "UPDATE search_results SET scraped_text = %s WHERE URL = %s",
            (scraped_text, url))
        self.conn.commit()
        self.close()

    def fetch_cherries_by_partial_title(self, partial_title):
        self.connect()
        query = "SELECT * FROM search_results WHERE LOWER(title) LIKE %s"
        self.cur.execute(query, [f"%{partial_title.lower()}%"])
        records = self.cur.fetchall()
        self.close()
        return records

    def clean_up_database(self):
        # delete duplicate cherries and non cherries
        self.connect()
        # Delete duplicate cherries
        query_delete_duplicates = """
        DELETE FROM search_results
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM search_results
            GROUP BY Title, URL
        );
        """
        self.cur.execute(query_delete_duplicates)
        # Delete non-cherries
        self.cur.execute("DELETE FROM search_results WHERE IsCherry = false")
        self.conn.commit()
        self.close()


class ChatContextManager(BaseDatabase):
    def save_chat_history(self, user_id, role, content):
        self.connect()
        self.cur.execute(
            "INSERT INTO chat_history (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, role, content))
        self.conn.commit()
        self.close()

    def fetch_chat_history(self, user_id):
        self.connect()
        self.cur.execute("SELECT * FROM chat_history WHERE user_id = %s ORDER BY timestamp ASC", [user_id])
        rows = self.cur.fetchall()
        self.close()
        return rows

    def delete_chat_history(self, user_id):
        self.connect()
        self.cur.execute("DELETE FROM chat_history WHERE user_id = %s", [user_id])
        self.conn.commit()
        self.close()
