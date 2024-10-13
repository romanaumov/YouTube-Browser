
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

from config import ES_INDEX, ES_URL, SENTENCE_TRANSFORMERS_MODEL, APP_LOGS_PATH
from config import setup_logging

logger = setup_logging(APP_LOGS_PATH)
model = SentenceTransformer(SENTENCE_TRANSFORMERS_MODEL)
es_client = Elasticsearch([ES_URL])

# Logging responses
def log_search_response(response, query_type):
    if 'hits' in response and 'hits' in response['hits']:
        logger.info(f"{query_type} search query returned {len(response['hits']['hits'])} results.")
    else:
        logger.warning(f"No results found for {query_type} search.")

# Search documents by query
def keyword_search(query, playlist, num_results=5):
    logger.info("Starting the sending Keyword search query .....")
    search_query = {
        "size": num_results,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text^4", "video^2", "playlist", "youtube_link"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "playlist": playlist
                    }
                }
            }
        }
    }
    
    response = es_client.search(index=ES_INDEX, body=search_query)

    result_docs = []
    if 'hits' in response and 'hits' in response['hits']:
        for hit in response['hits']['hits']:
            result_docs.append(hit['_source'])
    else:
        logger.warning("No hits found in the Elasticsearch response.")
    
    log_search_response(response, "Keyword")
    return result_docs

def knn_search(query_vector, playlist, num_results=5):
    logger.info("Starting the sending KNN search query .....")
    
    knn = {
        "field": "text_vector",     # options: "text_vector", "video_vector", "text_video_vector"
        "query_vector": query_vector,
        "k": num_results,
        "num_candidates": 10000, 
        "filter": {
            "term": {
                "playlist": playlist
            }
        }
    }
    
    search_query = {
        "knn": knn,
        "_source": ["id", "text", "video", "playlist", "youtube_link"]
    }
    
    response = es_client.search(index=ES_INDEX, body=search_query)

    result_docs = []
    if 'hits' in response and 'hits' in response['hits']:
        for hit in response['hits']['hits']:
            result_docs.append(hit['_source'])
    else:
        logger.warning("No hits found in the Elasticsearch response.")
    
    log_search_response(response, "KNN")
    return result_docs

# Search answer based on two possible approaches - keyword and vector search
def search_answer(query, playlist, search_type):
    logger.info(f"Starting the sending search query with the type: {search_type}")
    answer = None
    
    logger.debug(f"QUERY: {query}")
    logger.debug(f"PLAYLIST: {playlist}")
    
    if search_type == "Text":
        answer = keyword_search(query, playlist)
        
    elif search_type == "Vector":
        query_vector = model.encode(query)
        answer = knn_search(query_vector, playlist)
    
    else:
        logger.error(f"Invalid search type provided: {search_type}")
        raise ValueError(f"Unsupported search type: {search_type}")
    
    logger.info(f"Sending search query with the type: {search_type} was completed.")
    return answer
