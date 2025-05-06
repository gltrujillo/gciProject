import os
import time
import openai
import requests
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket support
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Load API keys from environment variables
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API keys
if not ASSEMBLYAI_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing API keys. Please set ASSEMBLYAI_API_KEY and OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY

# Function to transcribe audio using AssemblyAI
def transcribe_audio(file_path):
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    with open(file_path, "rb") as f:
        response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, files={"file": f})
    
    audio_url = response.json()["upload_url"]

    # Request transcription
    response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        headers=headers,
        json={"audio_url": audio_url},
    )
    
    transcript_id = response.json()["id"]

    # Poll AssemblyAI for the transcription result
    while True:
        result = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcript_id}", headers=headers).json()
        if result["status"] == "completed":
            return result["text"]
        elif result["status"] == "failed":
            raise Exception("Transcription failed")
        time.sleep(5)

# Function to summarize text using OpenAI API
def summarize_text(text):
    prompt = f"Summarize the following lecture into concise notes for a student:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise

def translate_text(text, target_language="es"):
    prompt = f"Translate the following text to {target_language}:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        translated_text = response['choices'][0]['message']['content'].strip()
        return translated_text
    except Exception as e:
        print(f"OpenAI Translation Error: {e}")
        raise

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Get the language from the form data (default to English)
    language = request.form.get("language", "en")

    # Save the uploaded file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        # Perform transcription and summarization
        output_file_path = "notes.txt"
        transcript = transcribe_audio(file_path)
        summary = summarize_text(transcript)
        
        # If language is not English, translate the summary
        if language != "en":
            summary = translate_text(summary, language)

        # Save the summary to a file
        with open(output_file_path, "w") as f:
            f.write(summary)

        # Return success message
        return jsonify({"message": f"Notes generated and saved to {output_file_path}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return render_template("index.html")  # Serve the index.html page

@app.route("/get_notes", methods=["GET"])
def get_notes():
    try:
        # Path to the notes.txt file
        notes_file_path = "notes.txt"

        # Read the notes file
        with open(notes_file_path, "r") as f:
            notes_content = f.read()

        # Return the content of the notes
        return jsonify({"notes": notes_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket events
@socketio.on("connect")
def handle_connect():
    print("Client connected to WebSocket")
    socketio.send("Welcome to the WebSocket server!")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("message")
def handle_message(data):
    print(f"Message received from client: {data}")
    socketio.send("Message received on server!")

if __name__ == "__main__":
    socketio.run(app, debug=True, log_output=True, use_reloader=True)