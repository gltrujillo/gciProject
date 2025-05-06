import os
import requests
import time
import openai

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
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=150
    )
    summary = response.choices[0].message['content'].strip()
    return summary

# Function to translate text using OpenAI API
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

# Main function to transcribe audio, summarize it, and save the summary
def transcribe_and_summarize(file_path, output_path="summary.txt"):
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

# Example usage
if __name__ == "__main__":
    audio_file_path = "Recording.mp3"  # Replace with your file path
    transcribe_and_summarize(audio_file_path)