import boto3
import time
import requests
import os
import json
import credentials as cr
from pathlib import Path

# Check access to S3
def check_access_to_s3():
    # List existing S3 buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    print("Existing S3 Buckets:")
    for bucket in response['Buckets']:
        print(bucket["Name"])

# Upload audio file into s3 bucket
def upload_file_into_s3(bucket_name, amazon_path, local_path, region="ap-southeast-2"):
    
    s3 = boto3.client('s3')
    check_access_to_s3()
    
    # Upload the CSV file to the S3 bucket
    s3.put_object(
        Bucket=bucket_name,
        Key=amazon_path,
        Body=open(local_path, 'rb'),
    )
    # Construct the s3 URL
    s3_uri = f"s3://{bucket_name}/{amazon_path}"
    print(f"Public URL: {s3_uri}")
    
    return s3_uri
    
# Transcribe audio file
def transcribe_audio(job_name, file_uri, region="ap-southeast-2"):
    
    # Initialize Boto3 client for Amazon Transcribe
    transcribe = boto3.client('transcribe', region_name=region)
    
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": file_uri},
        MediaFormat="mp3",
        LanguageCode="en-US",
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        
        if job_status in ["COMPLETED", "FAILED"]:
            print(f"Job {job_name} is {job_status}.")
            
            if job_status == "COMPLETED":
                transcription_url = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
                transcription_response = requests.get(transcription_url)
            break
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(10)
        
    return transcription_response
        
# Get audio segments from JSON transcribed data
def get_audio_segments(data):
            
    results = data.get('results', [])
    del results['items']
    
    # Iterate through each audio segment and remove the 'items' field
    for segment in results.get('audio_segments', []):
        if 'items' in segment:
            del segment['items']

    print(f"The audio segments were extracted from JSON data")
    return data

# Delete Amazon transcription job
def delete_transcription_job(job_name):
    # Initialize the Transcribe client
    transcribe = boto3.client('transcribe')
    
    try:
        # Delete the transcription job
        transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        print(f"Transcription job '{job_name}' was deleted successfully.")
        
    except Exception as e:
        print(f"Error deleting transcription job: {str(e)}")
        
# Save json file
def save_json(data, path):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Save data to a JSON file
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
            print(f"JSON data was saved to {path}.")

    except FileNotFoundError:
        return f"File {path} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Main function for transcribing an audio file
def transcribe_audio_main(audio_path, filename):
    
    # Amazon Transcribe service parameters
    s3_path = f"audio/AI-Audio-Assistant/{filename}.mp3"
    s3_bucket_name = 'audio-assistant-transcript'
    transcription_job_name = "transcript-job-audio-assistant"
    
    # Delete transcription job on Amazon Transcribe service
    delete_transcription_job(transcription_job_name)

    # Upload audio file into s3 bucket
    file_uri = upload_file_into_s3(s3_bucket_name, s3_path, audio_path)
    
    # Transcribe audio file
    transcription = transcribe_audio(transcription_job_name, file_uri)
    
    # Get audio segments from transcription
    transcription = get_audio_segments(transcription.json())
    
    # Delete transcription job on Amazon Transcribe service
    delete_transcription_job(transcription_job_name)
    
    return transcription


if __name__ == "__main__":
    
    # Set AWS credentials from the JSON file
    # cr.set_aws_credentials_from_json(cr.aws_credentials_path)
    
    # Paths for audio and transcript directories
    audio_root = "./data/The-Sound-of-AI - audio"
    transcript_root = "./data/The-Sound-of-AI - transcripts"

    # Ensure the transcript directory exists
    Path(transcript_root).mkdir(parents=True, exist_ok=True)

    # Loop through directories in the audio folder
    for root, dirs, files in os.walk(audio_root):
        for file in files:
            if file.endswith(".mp3"):
                # Full path to the audio file
                audio_file_path = os.path.join(root, file)
                
                # Extract relative path of the audio file and create corresponding transcript directory
                relative_path = os.path.relpath(root, audio_root)
                transcript_dir = os.path.join(transcript_root, relative_path)
                Path(transcript_dir).mkdir(parents=True, exist_ok=True)
                
                filename = os.path.splitext(file)[0]
                # Define transcript file name (e.g., for 'file.mp3' -> 'file.json')
                transcript_file_name = filename + ".json"
                transcript_file_path = os.path.join(transcript_dir, transcript_file_name)
                
                # Check if transcript already exists to avoid redundant work
                if not os.path.exists(transcript_file_path):
                    print(f"Processing: {audio_file_path}")

                    # Transcribe the audio (replace this with the actual transcription call)
                    transcription = transcribe_audio_main(audio_file_path, filename)
                    
                    with open(transcript_file_path, 'w') as json_file:
                        json.dump(transcription, json_file, indent=4)

                    print(f"Transcription saved to: {transcript_file_path}")
                else:
                    print(f"Transcript already exists for {audio_file_path}")
