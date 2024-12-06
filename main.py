import requests
import time
import openai

# Set up your API keys
ASSEMBLYAI_API_KEY = "dfa079a3948c41beade4881e5ec67472"
OPENAI_API_KEY = "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"

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
