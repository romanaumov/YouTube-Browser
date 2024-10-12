
import psycopg2
from psycopg2.extras import DictCursor
from config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, TZ, APP_LOGS_PATH
from config import setup_logging
from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo(TZ)
logger = setup_logging(APP_LOGS_PATH)

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
        logger.info("Trying to create table conversations and feedback...")
        with conn.cursor() as cur:
            # cur.execute("DROP TABLE IF EXISTS feedback")
            # cur.execute("DROP TABLE IF EXISTS conversations")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    playlist TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    openai_cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
        conn.commit()
        logger.info("Tables was successfully created.")
    finally:
        logger.error("Creation of tables failed.")
        conn.close()

# Save conversations into Postgres DB
def save_conversation(conversation_id, question, answer_data, playlist, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    conn = get_db_connection()
    try:
        logger.info("Trying to save conversation...")
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (
                    id, question, answer, playlist, response_time, relevance, 
                    relevance_explanation, prompt_tokens, completion_tokens, total_tokens, 
                    eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, openai_cost, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP))
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    playlist,
                    answer_data["response_time"],
                    answer_data["relevance"],
                    answer_data["relevance_explanation"],
                    answer_data["prompt_tokens"],
                    answer_data["completion_tokens"],
                    answer_data["total_tokens"],
                    answer_data["eval_prompt_tokens"],
                    answer_data["eval_completion_tokens"],
                    answer_data["eval_total_tokens"],
                    answer_data["openai_cost"],
                    timestamp,
                ),
            )
        conn.commit()
        logger.info("Conversations was successfully saved.")
    finally:
        logger.error("Saving of the conversation failed.")
        conn.close()

# Save feedback into Postgres DB
def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        logger.info("Trying to save feedback...")
        with conn.cursor() as cur:
            # First, check if the conversation ID exists in the conversations table
            cur.execute("""
                SELECT 1 FROM conversations WHERE id = %s
                """, (conversation_id,))
            if not cur.fetchone():
                logger.error(f"Conversation ID {conversation_id} does not exist in conversations table.")
                raise ValueError(f"Conversation ID {conversation_id} not found in conversations table.")
            
            # Now, insert the feedback into the feedback table
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
        logger.info("Feedback was successfully saved.")
    finally:
        logger.error("Saving of the feedback failed.")
        conn.close()

# Get up to 5 recent conversations from Postgres DB       
def get_recent_conversations(limit=5, relevance=None):
    conn = get_db_connection()
    try:
        logger.info("Trying to get recent conversations ...")
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            if relevance:
                query += f" WHERE c.relevance = '{relevance}'"
            query += " ORDER BY c.timestamp DESC LIMIT %s"

            cur.execute(query, (limit,))
            return cur.fetchall()
        logger.info("Conversations were successfully extracted.")
    finally:
        logger.error("Getting the conversations failed.")
        conn.close()

# Get feedback statistics from Postgres DB
def get_feedback_stats():
    conn = get_db_connection()
    try:
        logger.info("Trying to get feedbacks ...")
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
        logger.info("Feedbacks were successfully extracted.")
    finally:
        logger.error("Getting the Feedbacks failed.")
        conn.close()
    