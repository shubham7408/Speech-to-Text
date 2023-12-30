# app.py

from flask import Flask, render_template, request, redirect
import os
import moviepy.editor as mp
import speech_recognition as sr

app = Flask(__name__)

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'flv', 'mkv', 'mp3', 'wav', 'ogg', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Save the uploaded file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Convert video to audio (if needed)
        if filename.lower().endswith(('.mp4','.mp3', '.avi', '.flv', '.mkv')):
            video_clip = mp.VideoFileClip(filename)
            audio_clip = video_clip.audio
            audio_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{file.filename}.wav")
            audio_clip.write_audiofile(audio_file)
            audio_clip.close()
            video_clip.close()
        else:
            audio_file = filename

        # Perform speech recognition with error handling
        recognizer = sr.Recognizer()
        text = ""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = "Speech could not be recognized."
        except sr.RequestError as e:
            text = f"Recognition request failed: {e}"

        return render_template('index.html', text=text)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
