import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from moviepy.audio.io import AudioFileClip
import streamlit as st
import requests
import re
import os
from pytube import YouTube
import os
from moviepy.editor import *
from moviepy.audio.io import AudioFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

def get_links(query):
    query = query.replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    response = requests.get(url)
    html = response.text
    links = re.findall('"/watch\?v=(.{11})"', html)
    return [f"https://www.youtube.com/watch?v={link}" for link in links]

# singer = input("Enter the name of a singer: ")
# num_links = int(input("Enter the number of links: "))
# links= get_links(singer)[:num_links]

# print("YouTube links:")
# for link in links:
#     print(link)

def download_video(link, folder):
    yt = YouTube(link)
    stream = yt.streams.first()
    stream.download(folder)
    print("Video downloaded successfully")
    
def convert_to_audio(folder):
    for filename in os.listdir(folder):
        if filename.endswith(".3gpp"):
            video = VideoFileClip(os.path.join(folder, filename))
            audio = video.audio
            audio.write_audiofile(os.path.join(folder, filename.split(".")[0] + ".mp3"))
            print("Converted {} to audio successfully".format(filename))
            
def cut_audio(folder, seconds):
    for audio_file in os.listdir(folder):
        if audio_file.endswith(".mp3"):
            audio_path = os.path.join(folder, audio_file)
            cut_audio_path = os.path.join(folder, audio_file)

        # Load the audio file
            audio = AudioFileClip(audio_path)

        # Cut the audio to the specified duration
            #cut_audio = audio.subclip(seconds, audio.duration)
            cut_audio = audio.subclip(0,seconds)

        # Save the cut audio to a file
            cut_audio.write_audiofile(cut_audio_path)
            
def merge_audio(folder, output_filename):
    audio_clips = []
    for filename in os.listdir(folder):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            audio_clips.append(AudioFileClip(os.path.join(folder, filename)))
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(output_filename)
    print("Merged all audio files in the folder successfully")
    return output_filename


def send_email(to, audio_filename):
    from_email = "kaamkartechlo5050@gmail.com"
    from_password = "fsxjjjwvmklfnzfw"
    subject = "Audio file"
    message = "Attached is the audio file."

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    with open(audio_filename, "rb") as f:
        audio = MIMEAudio(f.read(),_subtype='wav')
    audio.add_header("Content-Disposition", "attachment", filename=audio_filename)
    msg.attach(audio)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, from_password)
    server.sendmail(from_email, to, msg.as_string())
    server.quit()

def folder1(folder,links):
    if not os.path.isdir(folder):
        os.makedirs(folder)
    for link in links:
        download_video(link, folder)


def main():
    st.title("Audio File Cutter")
    st.write("Enter the name of the singer, the number of seconds to cut, and your email address")
    folder = "vid"
    singer = st.text_input("Singer name: ")
    seconds = st.number_input("Number of seconds to cut: ")
    num = st.number_input("Number of videos: ",min_value=10, max_value=50, step=1)
    start_or_end = "start"
    to = st.text_input("Email address: ")

    if st.button("Submit"):
        links= get_links(singer)[:num]
        folder1(folder,links)
        convert_to_audio(folder)
        cut_audio(folder, seconds)
        output_filename=merge_audio(folder, "outfile.mp3")
        #output_filename="outfile.mp3"
        if output_filename:
            send_email(to, output_filename)
            st.success("Audio file sent to your email address successfully")
        else:
            st.error("No audio file found for the singer")

if __name__ == "__main__":
    main()
