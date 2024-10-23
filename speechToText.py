import requests
import time

# Your AssemblyAI API key
API_KEY = 'dfa079a3948c41beade4881e5ec67472'

# Function to upload audio file to AssemblyAI
def upload_audio(file_path):
    headers = {'authorization': API_KEY}
    with open(file_path, 'rb') as audio_file:
        response = requests.post('https://api.assemblyai.com/v2/upload',
                                 headers=headers, files={'file': audio_file})
    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        raise Exception('Error uploading audio file')

# Function to request transcription
def request_transcription(audio_url):
    headers = {'authorization': API_KEY, 'content-type': 'application/json'}
    data = {'audio_url': audio_url}
    response = requests.post('https://api.assemblyai.com/v2/transcript',
                             headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['id']
    else:
        raise Exception('Error requesting transcription')

# Function to get the transcription result
def get_transcription_result(transcription_id):
    headers = {'authorization': API_KEY}
    url = f'https://api.assemblyai.com/v2/transcript/{transcription_id}'
    
    while True:
        response = requests.get(url, headers=headers)
        result = response.json()

        if result['status'] == 'completed':
            return result['text']
        elif result['status'] == 'failed':
            raise Exception('Transcription failed')
        else:
            time.sleep(5)  # Wait for 5 seconds before checking again

# Main function to perform speech-to-text
def speech_to_text(file_path):
    print("Uploading audio file...")
    audio_url = upload_audio(file_path)
    
    print("Requesting transcription...")
    transcription_id = request_transcription(audio_url)
    
    print("Waiting for transcription to complete...")
    transcription_text = get_transcription_result(transcription_id)
    
    print("Transcription completed!")
    print("Transcribed text:")
    print(transcription_text)

# Example usage:
audio_file_path = 'Recording.mp3'  # Path to your audio file
speech_to_text(audio_file_path)
