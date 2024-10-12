
from openai import OpenAI
import es
import time
import json
from config import OPENAI_API_KEY, OPENAI_MODEL, APP_LOGS_PATH
from config import setup_logging

logger = setup_logging(APP_LOGS_PATH)
client = OpenAI(api_key=OPENAI_API_KEY)

# Generate answer to the question (prompt)
def llm(prompt):
    logger.info("Starting the sending the query to OpenAI .....")
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
    logger.info("Sending the query to OpenAI was completed.")
    logger.info(f"Answer from OpenAI: {generated_text} ")
    return generated_text, stats, response_time

# Build prompt for LLM based on question and context
def build_prompt(query, search_results):
    logger.info("Starting the build prompt .....")
    context_template = """
    Answer: {text}
    Video Title: {video}
    YouTube Link: {youtube_link}
    """.strip()

    prompt_template = """
        You're a teaching assistant. Answer the QUESTION based on the CONTEXT from the video transcripts database.
        Use only the facts from the CONTEXT when answering the QUESTION. 
        If you find the answer in CONTEXT, provide to user youtube video link and the video title from the CONTEXT below.
        If you didn't find any answer in CONTEXT, don't ask user to provide additional information and don't provide any links and video titles, just return only answer.
        Format of the answer should be an answer firstly, and then provide video title and youtube link to the video from CONTEXT.
        

    QUESTION: {question}

    CONTEXT: {context}
    """.strip()
    
    context = ""
    
    for doc in search_results:
        context = context + context_template.format(text=doc['text'],
                                                    video=doc['video'],
                                                    youtube_link=doc['youtube_link']).strip() + "\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    logger.info("Building prompt was completed.")
    logger.info(f"The prompt to OpenAI is: {prompt}")
    return prompt

# Evaluate the relevance of the answer from RAG system 
def rag_evaluation(query, answer):
    logger.info("Starting RAG evaluation .....")
    prompt_template = """
        You are an expert evaluator for the Retrieval-Augmented Generation (RAG) system. 
        Your task is to analyze the relevance of the generated answer to the given question. 
        Based on the relevance of the generated answer, you classify it as 
        "NOT_RELEVANT", "PARTICULARLY_RELEVANT", or "RELEVANT".

        Here is the data to evaluate:

        Question: {question}
        Generated answer: {answer}

        Analyze the content and context of the generated answer in relation to the question 
        and provide your evaluation as parsable JSON without using code blocks:

        {{
            "Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
            "Explanation": "[Provide a brief explanation for your evaluation]"
        }}
    """.strip()

    prompt = prompt_template.format(question=query, answer=answer)
    evaluation, tokens, _ = llm(prompt)
    
    try:
        json_eval = json.loads(evaluation)
        logger.info("RAG evaluation was completed.")
        logger.info(f"Relevance: {json_eval['Relevance']}, Explanation: {json_eval['Explanation']}")
        return json_eval['Relevance'], json_eval['Explanation'], tokens
    except json.JSONDecodeError:
        logger.error("RAG evaluation failed.")
        return "UNKNOWN", "Failed to parse evaluation", tokens


# Calculate cost for OpenAI gpt-4o-mini model
def openai_cost(stats):
    logger.info("OpenAI costs calculation started ...")
    cost = 0
    cost = (stats['prompt_tokens'] * 0.03 + stats['completion_tokens'] * 0.06) / 1000
    logger.info("OpenAI costs calculation was completed.")
    return cost

def get_answer(query, playlist, search_type):
    logger.info("Starting the RAG query .....")
    
    search_results = es.search_answer(query, playlist, search_type)
    prompt = build_prompt(query, search_results)
    answer, stats, response_time = llm(prompt)
    relevance, explanation, eval_tokens = rag_evaluation(query, answer)
    
    cost = openai_cost(stats)
    
    logger.info("RAG query was completed.")

    return {
        'answer': answer,
        'response_time': response_time,
        'relevance': relevance,
        'relevance_explanation': explanation,
        'prompt_tokens': stats['prompt_tokens'],
        'completion_tokens': stats['completion_tokens'],
        'total_tokens': stats['total_tokens'],
        'eval_prompt_tokens': eval_tokens['prompt_tokens'],
        'eval_completion_tokens': eval_tokens['completion_tokens'],
        'eval_total_tokens': eval_tokens['total_tokens'],
        'openai_cost': cost
    }
