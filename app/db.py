
import psycopg2
from psycopg2.extras import DictCursor
import logging
from config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, TZ
from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo(TZ)

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/db.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)
logger = logging.getLogger(__name__)

# Get Postgres DB connection
def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT
    )

# Initialize Postgres DB (create tables if they doesn't exist)
def init_db():
    conn = get_db_connection()
    try:
        logger.debug("Trying to create table conversations and feedback...")
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    playlist TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
        conn.commit()
        logger.debug("Tables was successfully created.")
    finally:
        logger.debug("Creation of tables failed.")
        conn.close()

# Save conversations into Postgres DB
def save_conversation(conversation_id, question, answer_data, playlist, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    conn = get_db_connection()
    try:
        logger.debug("Trying to save conversation...")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations (
                    id, question, answer, playlist, response_time, openai_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    playlist,
                    answer_data["response_time"],
                    answer_data["openai_cost"],
                    timestamp,
                ),
            )
        conn.commit()
        logger.debug("Conversations was successfully saved.")
    finally:
        logger.debug("Saving of the conversation failed.")
        conn.close()

# Save feedback into Postgres DB
def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        logger.debug("Trying to save feedback...")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (
                    conversation_id, feedback, timestamp) 
                VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
                """,
                (
                    conversation_id, 
                    feedback, 
                    timestamp
                ),
            )
        conn.commit()
        logger.debug("Feedback was successfully saved.")
    finally:
        logger.debug("Saving of the feedback failed.")
        conn.close()

# Get up to 5 recent conversations from Postgres DB
def get_recent_conversations(limit=5):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
                ORDER BY c.timestamp DESC LIMIT %s
            """

            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()

# Get feedback statistics from Postgres DB
def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()