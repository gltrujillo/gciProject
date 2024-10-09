import deepspeech
import numpy as np
import pyaudio
import wave

# Set up DeepSpeech model paths
model_file_path = 'deepspeech-0.9.3-models.pbmm'
scorer_file_path = 'deepspeech-0.9.3-models.scorer'

# Load the model
model = deepspeech.Model(model_file_path)
model.enableExternalScorer(scorer_file_path)

# Audio settings
sample_rate = 16000
chunk_size = 1024  # Number of frames per buffer

# PyAudio setup
p = pyaudio.PyAudio()

# Open microphone stream
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk_size)

print("Start speaking...")

# Create a stream for the model
ds_stream = model.createStream()

try:
    while True:
        audio_data = stream.read(chunk_size)
        # Convert audio data to 16-bit integers
        audio_buffer = np.frombuffer(audio_data, dtype=np.int16)
        # Feed the audio buffer to DeepSpeech
        ds_stream.feedAudioContent(audio_buffer)
        # Get the intermediate transcription
        text = ds_stream.intermediateDecode()
        print("Recognized: ", text)
except KeyboardInterrupt:
    # End the stream
    print("\nStopping...")
finally:
    # Finalize the transcription
    final_text = ds_stream.finishStream()
    print("Final Transcription: ", final_text)
    # Close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
