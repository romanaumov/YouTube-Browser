
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
import data_ingestion as di
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from config import (
    ES_INDEX,
    ES_URL,
    SENTENCE_TRANSFORMERS_MODEL,
)

model = SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL)
es_client = Elasticsearch([ES_URL])
es_client.info()

# Run to create a new index and execute data ingestion
# di.es_create_and_indexing(es_client, model)

# Search documents by query
def keyword_search(query, playlist, num_results=5):
    search_query = {
        "size": num_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question1^4",
                                    "question2^4",
                                    "question3^4",
                                    "question4^4",
                                    "question5^4",
                                    "question6^4",
                                    "question7^4",
                                    "question8^4",
                                    "question9^4",
                                    "question10^4", 
                                    "text"],
                        "type": "best_fields"
                    }
                },
                # "filter": {
                #     "term": {
                #         "playlist": "Audio Signal Processing for ML"
                #     }
                # }
            }
        }
    }
    
    response = es_client.search(index=ES_INDEX, body=search_query)
    
    result_docs = []
    for hit in response['hits']['hits']:
        result_docs.append(hit)
    
    return result_docs

def knn_search(query_vector, playlist, num_results=5):
    
    search_query = {
        "field": "text_vector",
        "query_vector": query_vector,
        "k": num_results,
        "num_candidates": 10000, 
    }
    
    response = es_client.search(index=ES_INDEX, knn=search_query, source=["id", 
                                                                        "text", 
                                                                        "video", 
                                                                        "start_time", 
                                                                        "youtube_id", 
                                                                        "youtube_link", 
                                                                        "question1", 
                                                                        "question2",
                                                                        "question3",
                                                                        "question4",
                                                                        "question5",
                                                                        "question6",
                                                                        "question7",
                                                                        "question8",
                                                                        "question9",
                                                                        "question10"])
    
    result_docs = []
    for hit in response['hits']['hits']:
        result_docs.append(hit)
    
    return result_docs

# Search answer based on two possible approaches - keyword and vector search
def search_answer(query, playlist, search_type):
    
    if search_type == "Text":
        answer = keyword_search(query, playlist)
        
    if search_type == "Vector":
        query_vector = model.encode(query)
        answer = knn_search(query_vector, playlist)
        
    return answer
