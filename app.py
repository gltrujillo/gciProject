import os
import time
import openai
import requests
import secrets
from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify

# Set up your API keys
ASSEMBLYAI_API_KEY = ""
OPENAI_API_KEY = ""

openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket support
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

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


def transcribe_and_summarize(file_path, output_path="notes.txt"):
    try:
        print("Transcribing audio...")
        transcript = transcribe_audio(file_path)
        print("Transcription completed.")
        
        print("Summarizing transcript...")
        summary = summarize_text(transcript)
        
        # Save summary to a file
        with open(output_path, "w") as f:
            f.write(summary)
        
        print(f"Summary saved to {output_path}.")
    except Exception as e:
        print("Error:", e)

# Route to trigger transcription and summarization for Recording.mp3
@app.route("/generate_notes", methods=["GET"])
def generate_notes():
    try:
        # Path to the file
        audio_file_path = "Recording.mp3"  # Replace with your file path
        output_file_path = "notes.txt"
        
        # Perform transcription and summarization
        transcribe_and_summarize(audio_file_path, output_file_path)
        
        return jsonify({"message": f"Notes generated and saved to {output_file_path}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        # Perform transcription and summarization
        output_file_path = "notes.txt"
        transcribe_and_summarize(file_path, output_file_path)

        # Return success message
        return jsonify({"message": f"Notes generated and saved to {output_file_path}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Route to serve the homepage
@app.route("/")
def index():
    return render_template("index.html")  # Serve the index.html page

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "connect-src 'self' ws: wss:; "  # Allow WebSocket connections
        "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
        "img-src 'self' data:; "  # Allow images, including data URIs
        "font-src 'self' data: fonts.googleapis.com fonts.gstatic.com; "  # Allow fonts
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline';"  # Allow external and inline scripts
    )
    return response

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

# Example WebSocket event handler for testing
@socketio.on("message")
def handle_message(data):
    print(f"Message received from client: {data}")
    socketio.send("Message received on server!")

# Run the app
if __name__ == "__main__":
    socketio.run(app, debug=True, log_output=True, use_reloader=True)
