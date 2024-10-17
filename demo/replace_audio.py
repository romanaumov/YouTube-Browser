
# pip install moviepy

import os
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip

# Replace audio track in a video
def replace_audio_in_video(input_video_path,
                            output_video_path,
                            audio_path):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        
        # Load the video and the new audio files
        video = VideoFileClip(input_video_path)
        new_audio = AudioFileClip(audio_path)

        # Set the new audio to the video
        video_with_new_audio = video.set_audio(new_audio)

        # Export the video with the new audio
        output_path = output_video_path
        video_with_new_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Close the clips to free resources
        video.close()
        new_audio.close()
        
    except FileNotFoundError:
        return f"File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    


# Overlay an audio with original audio track
def overlay_audio_with_volume_control(input_video_path, 
                                        output_video_path,
                                        audio_path, 
                                        original_volume=0.1, 
                                        new_audio_volume=1.5):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
        
        # Load the video file
        video = VideoFileClip(input_video_path)
        
        # Extract the original audio from the video
        original_audio = video.audio
        
        # Load your new audio file
        new_audio = AudioFileClip(audio_path)
        
        # Make both audio files the same length (shorter one)
        min_duration = min(original_audio.duration, new_audio.duration)
        original_audio = original_audio.subclip(0, min_duration)
        new_audio = new_audio.subclip(0, min_duration)
        
        # Adjust the volume of both audio tracks
        original_audio = original_audio.volumex(original_volume)  # Set the original audio volume
        new_audio = new_audio.volumex(new_audio_volume)  # Set the new audio volume (louder)
        
        # Combine both audio clips
        combined_audio = CompositeAudioClip([original_audio, new_audio])
        
        # Set the combined audio as the new audio for the video
        video_with_new_audio = video.set_audio(combined_audio)

        # Export the video with the new overlaid and volume-adjusted audio
        video_with_new_audio.write_videofile(output_video_path, codec="libx264", audio_codec="aac")
        
    except FileNotFoundError:
        return f"File {input_video_path} or {audio_path} not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    
    filename = "demo"
    # Video paths
    input_video_path = f"{filename} - without audio.mp4"
    output_video_path = f"{filename}.mp4"
    
    # Audio track
    audio_path = f"{filename}.mp3"
    
    replace_audio_in_video(input_video_path,
                            output_video_path,
                            audio_path)
