import text_helpers as th
import os
import hashlib
from collections import defaultdict

# Construct a YouTube link with start time
def construct_youtube_link(video_id, start_time):
    time = int(start_time.split('.')[0])
    return f"https://www.youtube.com/watch?v={video_id}&t={time}s"

# Generate an unique id for each chunk
def generate_id(doc):
    combined_fields = f"{doc['youtube_video_id']}-{doc['video']}-{doc['text'][:30]}"
    hash_object = hashlib.md5(combined_fields.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id

# Merge audio segments and add video_id and youtube_link
def merge_audio_segments(input_path, playlist, video_ids_path):
    
    data = th.read_json(input_path)
    video_ids_file = th.read_json(video_ids_path)
    
    filename = input_path.split('/')[-1].replace('.json', '')
    
    audio_segments = data["results"]["audio_segments"]
    merged_segments = []
    
    hashes = defaultdict(list)
    
    # Merge every three consecutive chunks
    for i in range(len(audio_segments) - 2):
        merged_text = (
            audio_segments[i]["transcript"] + " " + 
            audio_segments[i+1]["transcript"] + " " + 
            audio_segments[i+2]["transcript"]
        )
            
        youtube_video_id = video_ids_file[filename]
        youtube_link = construct_youtube_link(youtube_video_id, audio_segments[i]["start_time"])
        
        # Create the new chunk structure
        new_segment = {
            "id": i,
            "text": merged_text,
            "video": filename,
            "playlist": playlist,
            "youtube_video_id": youtube_video_id,
            "youtube_link": youtube_link,
            "start_time": audio_segments[i]["start_time"]
        }
        merged_segments.append(new_segment)
        
    # Update id with generated hash id
    for doc in merged_segments:
        doc["id"] = generate_id(doc)
        doc_id = doc["id"]
        hashes[doc_id].append(doc)
    
    if len(hashes) != len(merged_segments):
        print(f"---- WARNING ----: lengths are different! \nLen hashes: {len(hashes)},  Len docs: {len(merged_segments)}")
    return merged_segments


if __name__ == "__main__":
    
    yt_channel = "The Sound of AI"
    yt_channel_dir = f"./{yt_channel}/{yt_channel} - transcripts"
    video_ids_path = f"./{yt_channel}/video_ids.json"
    dataset_path = f"./{yt_channel}/dataset.json"
    
    # final dataset
    dataset = []
    # counter of chunks
    count = 1
    
    # Loop through directories in the audio folder
    for root, dirs, files in os.walk(yt_channel_dir):
        for playlist in dirs:
            playlist_dir = os.path.join(root, playlist)
            for file in os.listdir(playlist_dir):
                
                print(f"-------- Processing the file: {file}, {count} --------")
                count += 1
                
                if file.endswith(".json"):
                    # Full path to the transcript file
                    transcript_path = os.path.join(playlist_dir, file)
                    transcript_segments = merge_audio_segments(transcript_path, playlist, video_ids_path)
                    dataset.extend(transcript_segments)
                    
    th.save_json(dataset, dataset_path)