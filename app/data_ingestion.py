import json
from tqdm.auto import tqdm

from config import (
    DATASET_PATH,
    ES_INDEX,
)

import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Read json file
def read_json(path):
    try:
        # Open JSON file
        with open(path, 'r') as file:
            data = json.load(file)
            print(f"JSON file was read successfully from {path} ")
        return data

    except FileNotFoundError:
        return f"File {path} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

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
        print(f"ES index has already exist with name: {ES_INDEX}")
        print(f"Delete ES index with name: {ES_INDEX} ... ")
        es_client.indices.delete(index=ES_INDEX, ignore_unavailable=True)
        
    print(f"Creating a new ES index with name: {ES_INDEX} ... ")
    
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
    
    # Load dataset from json file
    chunks = load_dataset()
    
    # ElasticSearch documents indexing
    # for chunk in tqdm(dataset["audio_segments"]):
    for chunk in tqdm(chunks):
        chunk["text_vector"] = encoding_model.encode(chunk["text"])
        
        es_client.index(index=ES_INDEX, document=chunk)
