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

    def insert_cherry(self, unique_task_id, title, url, timestamp=datetime.now(),
                      keywords=None, priority=None, is_cherry=False, status="Active"):
        self.connect()
        self.cur.execute(
            "INSERT INTO search_results (uniquetaskid, Title, URL, IsCherry, Keywords, Timestamp, "
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

    def update_cherry_status_by_title(self, title, status="Active", is_cherry=True):
        self.connect()
        query = "UPDATE search_results SET Status = %s, IsCherry = %s WHERE LOWER(title) LIKE %s"
        self.cur.execute(query, (status, is_cherry, f"%{title.lower()}%"))
        updated_rows = self.cur.rowcount
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

