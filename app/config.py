import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18")

#Sentence Transformers
SENTENCE_TRANSFORMERS_MODEL = os.getenv("SENTENCE_TRANSFORMERS_MODEL", "paraphrase-MiniLM-L6-v2")

# Timezone
TZ = os.getenv("TZ", "Pacific/Auckland")

# ElasticSearch configuration
ES_URL = os.getenv("ES_URL", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "youtube-questions")
# ES_INDEX = os.getenv("ES_INDEX", "audio_assistant_index")

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# pgAdmin configuration
PGADMIN_DEFAULT_EMAIL = os.getenv("PGADMIN_DEFAULT_EMAIL")
PGADMIN_DEFAULT_PASSWORD = os.getenv("PGADMIN_DEFAULT_PASSWORD")

# Grafana configuration
GRAFANA_ADMIN_USER = os.getenv("GRAFANA_ADMIN_USER")
GRAFANA_ADMIN_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD")
GRAFANA_SECRET_KEY = os.getenv("GRAFANA_SECRET_KEY")

# Dataset path
DATASET_PATH = os.getenv("DATASET_PATH", "data/Audio Signal Processing for ML - dataset.json")

# Amazon Transcribe configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
