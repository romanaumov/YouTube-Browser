import text_helpers as th
from openai import OpenAI

# export OPENAI_API_KEY = "your_openai_api_key"
model = "gpt-4o-mini-2024-07-18"
client = OpenAI()

# Generate questions from LLM for every chunk
def generate_questions(text, n=10):
    
    prompt = f"""
        Generate {n} full completed questions based on the following text:\n\n{text}. 
        The questions should be not too short and not too long. 
        Return only list of questions without numbering.
    """
    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model = model, 
        messages = messages, 
        max_tokens = 300,
        n = 1,
        stop = None,
        temperature = 0.7)
    
    generated_text = response.choices[0].message.content
    questions = generated_text.split("\n")
    # Clean and filter empty lines
    questions = [q.strip() for q in questions if q.strip()]
    
    stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return questions[:n], stats

# Calculate statistic of costs
def openai_costs(model, stats):
    openai_costs = 0

    if model in model:
        openai_costs = (
            stats["prompt_tokens"] * 0.00015 + stats["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_costs


if __name__ == "__main__":
    
    yt_channel = "The Sound of AI"
    dataset_path = f"./{yt_channel}/dataset.json"
    ground_truth_dataset_path = f"./{yt_channel}/ground_truth_dataset.json"
    
    data = th.read_json(dataset_path)
    
    # final ground truth dataset
    ground_truth_dataset = []
    # total openAI cost
    total_costs = 0
    # counter of chunks
    count = 1
    # chunks id list to avoid generate questions twice
    ids_list = []
    
    print(f"Len of dataset: {len(data)}")
    
    # Iterate over all generated audio files in the directory
    for chunk in data:
                
        print(f"-------- Processing the chunk: {chunk['id']}, count: {count} --------")
        # counter of chunks
        count += 1
        
        # avoiding generate questions twice
        doc_id = chunk['id']
        if doc_id in ids_list:
            continue
        ids_list.append(doc_id)
        
        chunk_questions = {}
        
        # Iterate through each segment and add the questions
        text = chunk["text"]
        questions, stats = generate_questions(text, n=10)
        
        for question in questions:
            chunk_questions = {
                "id": chunk["id"],
                "playlist": chunk["playlist"],
                "questions": question
            }
            ground_truth_dataset.append(chunk_questions)
        
        # Save the ground truth dataset with questions after every chunk
        th.save_json(ground_truth_dataset, ground_truth_dataset_path)
    
        req_cost = openai_costs(model, stats)
        total_costs += req_cost
        
        print(f"The costs = {req_cost}. Total costs = {total_costs}")
    
    print(f"Len ground truth dataset: {len(ground_truth_dataset)}")