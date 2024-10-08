    
import yt_dlp
import os

# Audio Signal Processing for Machine Learning playlist
# output_path = "./Valerio Velardo youtube channel/Audio Signal Processing for ML/"
# url = "https://www.youtube.com/watch?v=iCwMQJnKk2c&list=PL-wATfeyAMNqIee7cH3q1bh4QJFAaeNv0"

# Sound Generation with Neural Networks playlist
# output_path = "./Valerio Velardo youtube channel/Sound Generation with Neural Networks/"
# url = "https://www.youtube.com/watch?v=Ey8IZQl_lKs&list=PL-wATfeyAMNpEyENTc-tVH5tfLGKtSWPp"

# Generative Music AI course playlist
# output_path = "./Valerio Velardo youtube channel/Generative Music AI course/"
# url = "https://www.youtube.com/watch?v=NpJWprrqlFw&list=PL-wATfeyAMNqAPjwGT3ikEz3gMo23pl-D"

# AI Audio Application - From Design to Deployment playlist
# output_path = "./Valerio Velardo youtube channel/AI Audio Application - From Design to Deployment/"
# url = "https://www.youtube.com/watch?v=CA0PQS1Rj_4&list=PL-wATfeyAMNpCRQkKgtOZU_ykXc63oyzp"

# Audio Deep Learning with Python playlist
output_path = "./The Sound of AI - audio/Audio Deep Learning with Python/"
url = "https://www.youtube.com/watch?v=fMqL5vckiU0&list=PL-wATfeyAMNrtbkCNsLcpoAyBBRJZVlnf"

# Ensure the directory exists, if not, create it
if not os.path.exists(output_path):
    os.makedirs(output_path)

# yt-dlp options for downloading the best audio and converting to .wav format
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',  # Save as MP3
        'preferredquality': '192',
    }],
    'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Save in the specified folder
    'socket_timeout': 300,  # Timeout in seconds (increase this value if needed)
    'retries': 5,  # Number of retries for failed connections
}

# Download the audio
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

