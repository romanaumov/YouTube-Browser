
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from config import ES_INDEX, ES_URL, SENTENCE_TRANSFORMERS_MODEL
import logging

# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/es.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)
logger = logging.getLogger(__name__)

model = SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL)
es_client = Elasticsearch([ES_URL])
es_client.info()

# Search documents by query
def keyword_search(query, playlist, num_results=5):
    logger.debug("Starting the sending Keyword search query .....")
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
    logger.debug("Sending Keyword search query was completed.")
    logger.debug(f"Answer from ElasticSearch for Keyword search is: {result_docs}")
    return result_docs

def knn_search(query_vector, playlist, num_results=5):
    logger.debug("Starting the sending KNN search query .....")
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
    logger.debug("Sending KNN search query was completed.")
    logger.debug(f"Answer from ElasticSearch for KNN search is: {result_docs}")
    return result_docs

# Search answer based on two possible approaches - keyword and vector search
def search_answer(query, playlist, search_type):
    logger.debug(f"Starting the sending search query with the type: {search_type}")
    if search_type == "Text":
        answer = keyword_search(query, playlist)
        
    if search_type == "Vector":
        query_vector = model.encode(query)
        answer = knn_search(query_vector, playlist)
    logger.debug(f"Sending search query with the type: {search_type} was completed.")
    return answer
