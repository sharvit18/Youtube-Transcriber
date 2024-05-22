from flask import Flask, render_template, request
import os
import speech_recognition as sr
import pytube
import moviepy.editor as mp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    video_url = request.form['video_url']
    output_path = "audio_files"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    audio_file = download_youtube_audio(video_url, output_path)
    if audio_file:
        wav_file = convert_to_wav(audio_file)
        if wav_file:
            transcribed_text = recognize_speech_from_audio(wav_file)
            if transcribed_text:
                return render_template('result.html', transcribed_text=transcribed_text)
            else:
                return "Error transcribing speech."
        else:
            return "Error converting audio to WAV."
    else:
        return "Error downloading YouTube audio."

def download_youtube_audio(video_url, output_path):
    try:
        yt = pytube.YouTube(video_url)
        stream = yt.streams.filter(only_audio=True).first()
        stream.download(output_path)
        audio_file = os.path.join(output_path, stream.default_filename)
        return audio_file
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        return None

def convert_to_wav(audio_file):
    try:
        audio_clip = mp.AudioFileClip(audio_file)
        output_file = os.path.splitext(audio_file)[0] + ".wav"
        audio_clip.write_audiofile(output_file)
        return output_file
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        return None

def recognize_speech_from_audio(audio_file):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            print("Transcribing audio...")
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Error fetching results; {e}")
        return None
    except Exception as e:
        print(f"Error recognizing speech: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
