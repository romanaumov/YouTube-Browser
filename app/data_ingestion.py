import json
from tqdm.auto import tqdm
from config import DATASET_PATH, ES_INDEX, ES_URL, SENTENCE_TRANSFORMERS_MODEL
import logging

from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/data_ingestion.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)
logger = logging.getLogger(__name__)

# Read json file
def read_json(path):
    try:
        # Open JSON file
        with open(path, 'r') as file:
            data = json.load(file)
            logger.debug(f"JSON file was read successfully from {path} ")
        return data

    except FileNotFoundError:
        return logger.debug(f"File {path} not found.")
    except Exception as e:
        return logger.debug(f"An error occurred: {str(e)}")

# Load dataset from json file
def load_dataset():
    data = read_json(DATASET_PATH)
    documents = []

    for doc in data["audio_segments"]:
        documents.append(doc)
    return documents

# Create an ElasticSearch index and Indexing the dataset chunks
def es_create_and_indexing(es_client, encoding_model):
    if es_client.indices.exists(index=ES_INDEX):
        logger.debug(f"ES index has already exist with name: {ES_INDEX}")
        logger.debug(f"Delete ES index with name: {ES_INDEX} ... ")
        es_client.indices.delete(index=ES_INDEX, ignore_unavailable=True)
        
    logger.debug(f"Creating a new ES index with name: {ES_INDEX} ... ")
    
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "id": {"type": "text"},
                "text": {"type": "text"},
                "video": {"type": "keyword"},
                "start_time": {"type": "text"},
                "youtube_id": {"type": "text"},
                "youtube_link": {"type": "text"},
                "question1": {"type": "text"},
                "question2": {"type": "text"},
                "question3": {"type": "text"},
                "question4": {"type": "text"},
                "question5": {"type": "text"},
                "question6": {"type": "text"},
                "question7": {"type": "text"},
                "question8": {"type": "text"},
                "question9": {"type": "text"},
                "question10": {"type": "text"},
                "text_vector": {"type": "dense_vector",
                                "dims": 384,
                                "index": True,
                                "similarity": "cosine"
                                },
            }
        }
    }
    
    # Create ElasticSearch index
    es_client.indices.create(index=ES_INDEX, body=index_settings)
    logger.debug(f"A new ES index with name: {ES_INDEX} was created.")
    
    logger.debug(f"Starting load a dataset...")
    # Load dataset from json file
    chunks = load_dataset()
    logger.debug(f"Dataset was loaded.")
    
    # ElasticSearch documents indexing
    logger.debug(f"Starting indexing a dataset into {ES_INDEX} ...")
    for chunk in tqdm(chunks):
    # for chunk in chunks:
        chunk["text_vector"] = encoding_model.encode(chunk["text"])
        
        es_client.index(index=ES_INDEX, document=chunk)
        
    logger.debug(f"Indexing a dataset was completed.")
    logger.debug(f"Data ingestion was completed.")


def data_ingestion():
    try:
        logger.debug("Starting Dataset ingestion ... ")
        model = SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL)
        es_client = Elasticsearch([ES_URL])
        es_client.info()
        es_create_and_indexing(es_client, model)
        logger.debug("Dataset ingestion was completed.")
    except Exception as e:
        return logger.debug(f"An error occurred with data ingestion: {str(e)}")
    
data_ingestion()