import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime


# Load the environment variables
load_dotenv()

# Set up OpenAI API credentials
password = os.getenv("POSTGRES_PASS")


class CherryDatabase:
    def __init__(self):
        self.host = "localhost"
        self.database = "postgres"
        self.user = "postgres"
        self.password = "fromhell04"

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

    def insert_cherry(self, unique_task_id, title, url, timestamp=datetime.now(),
                      keywords=None, priority=None, is_cherry=False, status="Active"):
        self.connect()
        self.cur.execute(
            "INSERT INTO search_results (UniqueTaskID, Title, URL, IsCherry, Keywords, Timestamp, "
            "Priority, Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (unique_task_id, title, url, is_cherry, keywords, timestamp, priority, status))
        self.conn.commit()
        self.close()

    def fetch_cherries(self):
        self.connect()
        self.cur.execute("SELECT * FROM search_results")
        rows = self.cur.fetchall()
        self.close()
        return rows

    def update_cherry_status(self, unique_task_id, title, url, status="Active", is_cherry=True):
        self.connect()
        self.cur.execute(
            "UPDATE search_results SET Status = %s, IsCherry = %s WHERE UniqueTaskID = %s AND Title = %s AND URL = %s",
            (status, is_cherry, unique_task_id, title, url)
        )
        self.conn.commit()
        self.close()

    def fetch_cherries_by_partial_title(self, partial_title):
        self.connect()
        query = "SELECT * FROM search_results WHERE LOWER(title) LIKE %s"
        self.cur.execute(query, [f"%{partial_title.lower()}%"])
        records = self.cur.fetchall()
        self.close()
        return records

