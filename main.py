import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np
from datetime import datetime
import pygame
import time

DETECT_VOLUME = 1000
SLEEP_TIME = 50 #ms
#SOUND_PATH = "./sound/puff.mp3"
SOUND_PATH = "./sound/guwa.mp3"

# PyAudio Settings
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000 # USB microphone rate
DEVICE_ID = 1  # USB microphone index

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=DEVICE_ID,
                frames_per_buffer=CHUNK)

root = tk.Tk()
root.title("title") 

label = tk.Label(root, text="volume: 0", font=("Arial", 20))
label.pack(padx=20, pady=20)

#meter = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
#meter.pack(padx=20, pady=20)

# log_message box (max 5 lines)
log_box = tk.Listbox(root, height=5, width=50)
log_box.pack()

# Play Sound
def play_wav(filename):
    # Open WAV file
    wav_file = wave.open(filename, 'rb')

    # Initialize PyAudio for playback
    audio_player = pyaudio.PyAudio()

    # Open output stream
    playback_stream = audio_player.open(
        format=audio_player.get_format_from_width(wav_file.getsampwidth()),
        channels=wav_file.getnchannels(),
        rate=wav_file.getframerate(),
        output=True
    )
    # Playback chunk size
    playback_chunk = 1024

    # Read first chunk
    playback_data = wav_file.readframes(playback_chunk)

    # Play until no more data
    while playback_data:
        playback_stream.write(playback_data)
        playback_data = wav_file.readframes(playback_chunk)

    # Cleanup
    playback_stream.stop_stream()
    playback_stream.close()
    audio_player.terminate()
    
def play_mp3(filename):
    # Initialize mixer
    pygame.mixer.init()
    # Load MP3 file
    pygame.mixer.music.load(filename)
    # Play
    pygame.mixer.music.play()
    # Cool Down
    time.sleep(0.3)

# Loop Function
def update_meter():
    try:
        # Read audio chunk from the microphone
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # If the buffer is empty, set volume to 0
        if len(audio_data) == 0:
            volume = 0
        else:
            # Compute RMS (convert to float32 to avoid overflow)
            rms = np.mean(audio_data.astype(np.float32)**2)

            # If RMS is NaN or infinity, treat it as silence
            if np.isnan(rms) or np.isinf(rms):
                volume = 0
            else:
                volume = np.sqrt(rms)

        # Update GUI components
        #meter["value"] = min(volume, 300)
        label.config(text=f"volume: {int(volume)}")
        
        if int(volume) >= DETECT_VOLUME:           
            # Create timestamp string
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Format log message
            log_message = f"[{now}] big volume = {volume}"

            # Print to console
            #print(log_message)
            
            # --- Add log to Listbox (max 5 lines) ---
            log_box.insert(tk.END, log_message)
            # If more than 5 lines, remove the oldest one
            if log_box.size() > 5:
                log_box.delete(0)

            # Append to log file
            with open("logs.txt", "a") as f:
                f.write(log_message + "\n")
                
            #Play Sound
            play_mp3(SOUND_PATH)

    except Exception as e:
        # Print any unexpected errors and continue running
        print("Error:", e)
        volume = 0

    # Schedule the next update after 50 ms
    root.after(SLEEP_TIME, update_meter)

update_meter()

try:
    # Searching USB micorphone index
    #for i in range(p.get_device_count()):
    #    print(i, p.get_device_info_by_index(i))
    root.mainloop()
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

