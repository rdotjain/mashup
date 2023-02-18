# mashup
A web app that creates mashup of videos of your favourite singer.

Tasks:
--
1. Search youtube for n number of videos of a singer
2. Download the video files.
3. Convert them to audio
4. Trim the audio files to certain duration
5. Merge all audio files
6. Create a zip file and mail it

Libraries used:
--
|     library/module    |                            description                           |
|:---------------------:|:----------------------------------------------------------------:|
| `youtubesearchpython` | to search for relevant video links.                              |
| `pytube`              | to download video files from youtube <br>                        |
| `moviepy`             | to convert video files to audio (mp3) files, trim and merge them |
| `zipfile`             | module to zip the audio file                                     |
| `smtplib`             | to send mail                                                     |


Usage:
--
To run from cli, use the following command:
```python
python 102017010.py [SingerName] [NumberOfVideos] [AudioDuration] [OutputFileName] 
```
Example:
```py
python 102017010.py zayn_malik 2 20 zayn.mp3  
```
