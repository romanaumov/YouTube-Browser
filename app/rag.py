
from openai import OpenAI
import es
import logging
import time
from config import OPENAI_API_KEY, OPENAI_MODEL


# Configure logging to save logs to a file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/rag.log"),   # Save logs to a file named app.log
        # logging.StreamHandler()           # Output logs to console as well
    ]
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY)

def llm(prompt):
    logger.debug("Starting the sending the query to OpenAI .....")
    messages = [{"role": "user", "content": prompt}]
    
    start_time = time.time()
    response = client.chat.completions.create(
        model = OPENAI_MODEL,
        messages = messages, 
        max_tokens = 1024,
        n = 1,
        stop = None,
        temperature = 0.7)
    
    generated_text = response.choices[0].message.content
    end_time = time.time()
    response_time = end_time - start_time
    
    stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    logger.debug("Sending the query to OpenAI was completed.")
    logger.debug(f"Answer from OpenAI: {generated_text} ")
    return generated_text, stats, response_time


def build_prompt(query, search_results):
    logger.debug("Starting the build prompt .....")
    context_template = """
    Q1: {question1}
    Q2: {question2}
    Q3: {question3}
    Q4: {question4}
    Q5: {question5}
    Q6: {question6}
    Q7: {question7}
    Q8: {question8}
    Q9: {question9}
    Q10: {question10}
    A: {text}
    V: {video}
    L: {youtube_link}
    """.strip()

    prompt_template = """
    You're a teaching assistant. Answer the QUESTION based on the CONTEXT from the video transcripts database.
    Use only the facts from the CONTEXT when answering the QUESTION. 
    If you find the answer in CONTEXT, contain a video link and the video name from the CONTEXT below.
    Format of the answer should be an answer firstly, and then provide video name and link to the video, if you found it.

    QUESTION: {question}

    CONTEXT:
    {context}
    """.strip()
    
    context = ""
    
    for doc in search_results:
        context = context + context_template.format(question1=doc['_source']['question1'],
                                                    question2=doc['_source']['question2'],
                                                    question3=doc['_source']['question3'],
                                                    question4=doc['_source']['question4'],
                                                    question5=doc['_source']['question5'],
                                                    question6=doc['_source']['question6'],
                                                    question7=doc['_source']['question7'],
                                                    question8=doc['_source']['question8'],
                                                    question9=doc['_source']['question9'],
                                                    question10=doc['_source']['question10'],
                                                    text=doc['_source']['text'],
                                                    video=doc['_source']['video'],
                                                    youtube_link=doc['_source']['youtube_link']).strip() + "\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    logger.debug("Building prompt was completed.")
    logger.debug(f"The prompt to OpenAI is: {prompt}")
    return prompt

# Calculate cost for OpenAI gpt-4o-mini model
def calculate_openai_cost(stats):
    cost = 0
    cost = (stats['prompt_tokens'] * 0.03 + stats['completion_tokens'] * 0.06) / 1000

    return cost

def get_answer(query, playlist, search_type):
    logger.debug("Starting the RAG query .....")
    search_results = es.search_answer(query, playlist, search_type)
    prompt = build_prompt(query, search_results)
    answer, stats, response_time = llm(prompt)
    openai_cost = calculate_openai_cost(stats)
    
    logger.debug("RAG query was completed.")

    return {
        'answer': answer,
        'response_time': response_time,
        'openai_cost': openai_cost
    }





# query = "What is MFCC?"
# query = "How Mel-Spectrogram can be used in applications?"
# query = "How Spatial-Frequency parameters can be retrieval from an audio? What methods and approaches I should use?"
# query = "What author of the course think about Universe?"
# query = "What is the name of the author of the video series?"
# query = "What information is there about the author of the video series?"
# query = "What is this video series about?"

# print(f"Question: {query}")

# playlist = "Audio Signal Processing for ML"

# search_type = "Text"
# response = elastic_rag(query, playlist, search_type)

# print("---------------------------- RESPONSE BELOW FROM LLM ---------------------------------:\n")
# print(response)
# print("\n---------------------------- RESPONSE BELOW FROM LLM ---------------------------------:\n")


# number of tokens
# num_input_tokens = len(tokens)
# num_output_tokens = len(response_tokens)

# # the cost per 1000 tokens for OpenAI
# input_cost = 0.005
# output_cost = 0.015

# our_cost = (input_cost/1000*num_input_tokens + output_cost/1000*num_output_tokens)
# print(f"The cost of our request for gpt-4o is {round(our_cost, 7)} US dollars")
