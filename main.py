import tkinter as tk
from tkinter import ttk
import pyaudio
import numpy as np

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

meter = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
meter.pack(padx=20, pady=20)

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
        meter["value"] = min(volume, 300)
        label.config(text=f"volume: {int(volume)}")

    except Exception as e:
        # Print any unexpected errors and continue running
        print("Error:", e)
        volume = 0

    # Schedule the next update after 50 ms
    root.after(100, update_meter)

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

