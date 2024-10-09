import text_helpers as th
from openai import OpenAI
import os
import time

# export OPENAI_API_KEY = "your_openai_api_key"
model = "gpt-4o-mini-2024-07-18"
client = OpenAI()

# Function to merge chunks with overlapping chunks
def merge_chunks(data, filename):
    audio_segments = data["audio_segments"]
    merged_segments = []
    
    # Merge every three consecutive chunks
    for i in range(len(audio_segments) - 2):
        merged_text = (
            audio_segments[i]["transcript"] + " " + 
            audio_segments[i+1]["transcript"] + " " + 
            audio_segments[i+2]["transcript"]
        )
        
        # Create the new chunk structure
        new_segment = {
            "id": i,
            "text": merged_text,
            "video": filename,
            "start_time": audio_segments[i]["start_time"]
        }
        merged_segments.append(new_segment)
    
    # Return the new JSON structure
    return {"audio_segments": merged_segments}


def merge_audio_segments(input_path, output_path):
    
    data = th.read_json(input_path)
    filename = input_path.split('/')[-1].replace('.json', '')
    
    # Generate new merged data
    merged_data = merge_chunks(data["results"], filename)

    # Write the merged data to a JSON file
    th.save_json(merged_data, output_path)


def generate_questions(text, n=10):
    
    prompt = f"Generate {n} questions based on the following text:\n\n{text}. Return only list of questions."
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
    questions = [q for q in questions if q.strip()]
    
    stats = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }
    return questions[:n], stats


def openai_costs(model, stats):
    openai_costs = 0

    if model in model:
        openai_costs = (
            stats["prompt_tokens"] * 0.00015 + stats["completion_tokens"] * 0.0006
        ) / 1000
    else:
        print("Model not recognized. OpenAI cost calculation failed.")

    return openai_costs

# Merge json files in one dataset
def merge_json_files(dir_path):
    
    # Initialize an empty structure
    merged_data = {"audio_segments": []}  
    
    # To ensure continuous numbering of 'id'
    current_id = 0  

    # Iterate through all files in the directory
    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            file_path = os.path.join(dir_path, filename)
            data = th.read_json(file_path)
            
            if "audio_segments" in data:
                for segment in data["audio_segments"]:
                    segment["id"] = current_id
                    
                    # Clean questions from numbering
                    segment["questions"] = [q.split('. ', 1)[1] if '. ' in q else q for q in segment["questions"]]
                    
                    merged_data["audio_segments"].append(segment)
                    current_id += 1
                    
    return merged_data

# Construct a YouTube link with start time
def construct_youtube_link(video_id, start_time):
    time = int(start_time.split('.')[0])
    return f"https://www.youtube.com/watch?v={video_id}&t={time}s"

# Add youtube links to dataset with transcription chunks
def add_youtube_link(dataset_path, video_id_path):
    
    video_file = th.read_json(video_id_path)
    data = th.read_json(dataset_path)
    
    # Initialize an empty structure
    data_with_links = {"audio_segments": []}  
    
    # Update transcription JSON with YouTube ID and link
    for segment in data["audio_segments"]:
        video_name = segment["video"]
        if video_name in video_file:
            youtube_id = video_file[video_name]
            segment["youtube_id"] = youtube_id
            segment["youtube_link"] = construct_youtube_link(youtube_id, segment["start_time"])
            
            data_with_links["audio_segments"].append(segment)
            
    return data_with_links

import json

# Function to transform the question list to individual fields
def transform_questions(dataset_path):
    
    data = th.read_json(dataset_path)
    for segment in data["audio_segments"]:
        questions = segment.pop("questions")  # Remove "questions" field from segment
        
        # Add each question as a new field with keys like "question1", "question2", etc.
        for i, question in enumerate(questions, start=1):
            segment[f"question{i}"] = question
    return data



if __name__ == "__main__":

    yt_channel = "The Sound of AI"
    yt_playlist = "Audio Signal Processing for ML"
    # yt_playlist = "Audio Deep Learning with Python"
    yt_playlist_path = f"./{yt_channel} - transcripts/{yt_playlist}/"
    output_yt_playlist_path = f"./{yt_channel} - transcripts/{yt_playlist} - with questions/"
    video_id_path = f"./{yt_channel} - transcripts/video_ids.json"
    
    # Output file to save the merged result
    dataset_path = f"./{yt_channel} - transcripts/{yt_playlist} - dataset.json"

    total_costs = 0
    
    # Iterate over all generated audio files in the directory
    for audio_file in os.listdir(yt_playlist_path):
        if audio_file.endswith(".json"):
            
            filename = audio_file.split(".")[0]
            
            file_with_questions = f"{output_yt_playlist_path}{filename} - with questions.json"
            print(f"Current file: {file_with_questions}")
            
            # Check if transcript already exists to avoid redundant work
            if not os.path.exists(file_with_questions):
                print(f"-------- Processing the file: {filename} --------")
                
                audio_transcription_path = f"./{yt_channel} - transcripts/{yt_playlist}/{filename}.json"

                # Output filename
                audio_segments_path = f"{output_yt_playlist_path}{filename} - with questions.json"
                
                merge_audio_segments(audio_transcription_path, audio_segments_path)
                
                audio_segments_data = th.read_json(audio_segments_path)
                
                for segment in audio_segments_data["audio_segments"]:
                    
                    # Iterate through each segment and add the questions
                    text = segment["text"]
                    questions, stats = generate_questions(text, n=10)
                    segment["questions"] = questions
                    
                    req_cost = openai_costs(model, stats)
                    total_costs += req_cost
                    
                    print(f"The costs = {req_cost}. Total costs = {total_costs}")
                    time.sleep(1)

                # Save the updated JSON file with the questions
                th.save_json(audio_segments_data, audio_segments_path)
                
            else:
                print(f"Transcript already exists for {filename}")
                
        time.sleep(5)
        
    # Merge json files in one dataset
    merged_data = merge_json_files(output_yt_playlist_path)
    th.save_json(merged_data, dataset_path)
    
    # Add youtube links to dataset with transcription chunks
    data_with_links = add_youtube_link(dataset_path, video_id_path)
    th.save_json(data_with_links, dataset_path)
    
    # Transform the JSON data
    transformed_data = transform_questions(dataset_path)
    th.save_json(transformed_data, dataset_path)