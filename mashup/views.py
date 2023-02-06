from django.shortcuts import render
from django.contrib import messages

from moviepy.editor import *
from pytube import YouTube
from threading import Thread
from youtubesearchpython import VideosSearch
from zipfile import ZipFile

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

SAVE_PATH = "mashup/static/mashup/"


def get_videos(singer_name, num_videos):
    """
    Get videos from youtube
    """
    prefix = "https://www.youtube.com/watch?v="
    videosSearch = VideosSearch(singer_name, limit=num_videos)
    videos = videosSearch.result()["result"]
    videos = [prefix + video["id"] for video in videos]
    return videos


def download_video(video_url, save_path=SAVE_PATH):
    save_path = save_path + "/videos"
    yt = YouTube(video_url)
    video = yt.streams.first()
    video_title = video.default_filename.replace(" ", "_")
    video.download(save_path, video_title)
    return video_title


def convert_to_mp3(video_title, save_path=SAVE_PATH):
    mp3_save_path = save_path
    video_path = save_path + "/videos/" + video_title
    mp3_path = mp3_save_path + "/" + video_title.split(".")[0] + ".mp3"
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(mp3_path)
    audio_clip.close()
    video_clip.close()
    return mp3_path


def trim_mp3(mp3_path, duration):
    audio_clip = AudioFileClip(mp3_path)
    audio_clip = audio_clip.subclip(0, duration)
    audio_clip.write_audiofile(mp3_path)
    audio_clip.close()
    print("Done trimming " + mp3_path)


def download_and_process_video(video_url, save_path, duration):
    video_title = download_video(video_url, save_path)
    audio_title = convert_to_mp3(video_title, save_path)
    trim_mp3(audio_title, duration)


def merge_mp3s(singer_name, save_path=SAVE_PATH):
    final_mp3_path = save_path + "/" + singer_name + ".mp3"
    mp3s = [
        save_path + "/" + mp3 for mp3 in os.listdir(save_path) if mp3.endswith(".mp3")
    ]
    final_clip = concatenate_audioclips([AudioFileClip(mp3) for mp3 in mp3s])
    final_clip.write_audiofile(final_mp3_path)
    final_clip.close()
    print("Done merging mp3s to " + final_mp3_path)
    return final_mp3_path


def convert_to_zip(mp3_path):
    zip_path = mp3_path.split(".")[0] + ".zip"
    with ZipFile(zip_path, "w") as zipObj:
        zipObj.write(mp3_path)
    print("Done converting to zip " + zip_path)
    return zip_path


def send_email(email, zip_path):
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.starttls()
    s.login("noreply.rupanshi@gmail.com", "vfqxhcaeaihrbjay")
    msg = MIMEMultipart()
    msg["From"] = "noreply.rupanshi@gmail.com"
    msg["To"] = email
    msg["Subject"] = "Mashup"
    body = "Here is your mashup."
    msg.attach(MIMEText(body, "plain"))
    attachment = open(zip_path, "rb")
    p = MIMEBase("application", "octet-stream")
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment; filename= %s" % zip_path)
    msg.attach(p)
    text = msg.as_string()
    s.sendmail(msg["From"], email, text)
    s.quit()
    print("Done sending email to " + email)


def mashup(singer_name, num_videos, duration, email):
    save_path = SAVE_PATH + singer_name
    videos = get_videos(singer_name, num_videos)

    threads = []
    for video in videos:
        t = Thread(target=download_and_process_video, args=(video, save_path, duration))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # merge mp3s
    final_mp3_path = merge_mp3s(singer_name, save_path)

    # convert to zip
    zip_path = convert_to_zip(final_mp3_path)

    # send email
    send_email(email, zip_path)


def index(request):
    if request.method == "POST":
        singer_name = request.POST.get("singer_name")
        num_videos = int(request.POST.get("num_videos"))
        duration = request.POST.get("duration")
        email = request.POST.get("email")

        t = Thread(target=mashup, args=(singer_name, num_videos, duration, email))
        t.start()

        # flash message to user
        messages.success(request, "Your mashup is being created. You will receive an email when it is ready.")
        return render(request, "mashup/index.html", {})

    return render(request, "mashup/index.html", {})
