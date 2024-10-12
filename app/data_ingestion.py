import json
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

from config import DATASET_PATH, ES_INDEX, ES_URL, SENTENCE_TRANSFORMERS_MODEL, INGESTION_LOGS_PATH
from config import setup_logging
from db import init_db

logger = setup_logging(INGESTION_LOGS_PATH)

# Read json file
def read_json(path):
    try:
        # Open JSON file
        with open(path, 'r') as file:
            data = json.load(file)
            logger.info(f"JSON file was read successfully from {path} ")
        return data

    except FileNotFoundError:
        return logger.error(f"File {path} not found.")
    except Exception as e:
        return logger.error(f"An error occurred: {str(e)}")

# Load dataset from json file
def load_dataset():
    data = read_json(DATASET_PATH)
    documents = []

    for doc in data:
        documents.append(doc)
    return documents

# Create an ElasticSearch index and Indexing the dataset chunks
def es_create_and_indexing(es_client, encoding_model):
    if es_client.indices.exists(index=ES_INDEX):
        logger.error(f"ES index has already exist with name: {ES_INDEX}")
        logger.info(f"Delete ES index with name: {ES_INDEX} ... ")
        es_client.indices.delete(index=ES_INDEX, ignore_unavailable=True)
        
    logger.info(f"Creating a new ES index with name: {ES_INDEX} ... ")
    
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "text": {"type": "text"},
                "video": {"type": "text"},
                "playlist": {"type": "keyword"},
                "youtube_video_id": {"type": "keyword"},
                "youtube_link": {"type": "keyword"},
                "start_time": {"type": "keyword"},
                "text_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
                "video_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
                "text_video_vector": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                },
            }
        }
    }
    
    # Create ElasticSearch index
    es_client.indices.create(index=ES_INDEX, body=index_settings)
    logger.info(f"A new ES index with name: {ES_INDEX} was created.")
    
    logger.info(f"Starting load a dataset...")
    # Load dataset from json file
    chunks = load_dataset()
    logger.info(f"Dataset was loaded.")
    
    # ElasticSearch documents indexing
    logger.info(f"Starting indexing a dataset into {ES_INDEX} ...")
    
    for chunk in tqdm(chunks):
        text_video = chunk["text"] + chunk["video"]
        
        chunk["text_vector"] = encoding_model.encode(chunk["text"])
        chunk["video_vector"] = encoding_model.encode(chunk["video"])
        chunk["text_video_vector"] = encoding_model.encode(text_video)
        
        es_client.index(index=ES_INDEX, document=chunk)
        
    logger.info(f"Indexing a dataset was completed.")
    logger.info(f"Data ingestion was completed.")


def data_ingestion():
    try:
        logger.info("Starting Dataset ingestion ... ")
        model = SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL)
        es_client = Elasticsearch([ES_URL])
        es_create_and_indexing(es_client, model)
        logger.info("Dataset ingestion was completed.")
    except Exception as e:
        return logger.error(f"An error occurred with data ingestion: {str(e)}")

if __name__ == "__main__":
    
    logger.info("Starting data ingestion service...")
    data_ingestion()
    logger.info("Data ingestion service was completed.")
    
    logger.info("DB initialization stage started ... ")
    init_db()
    logger.info("DB initialization stage was completed.")
    