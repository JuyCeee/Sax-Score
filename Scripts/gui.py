import json
import sys
import os
import random
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QPushButton, QMainWindow, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView 
from PySide6.QtCore import QUrl
import sounddevice as sd
from scipy.io import wavfile
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sax Score")
        self.setGeometry(100, 100, 970, 540)

        layout = QVBoxLayout()
        label = QLabel("Welcome to Sax Score!")
        central_widget = QWidget()
        button = QPushButton("Analyze Audio")
        layout.addWidget(label)
        self.setLayout(layout)

        self.browser = QWebEngineView()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file_path = os.path.join(current_dir, "audio_waveform_graph.html")

        self.browser.setUrl(QUrl.fromLocalFile(html_file_path))

        layout.addWidget(self.browser)
        layout.addWidget(button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        button.clicked.connect(self.analyze_audio)

    def analyze_audio(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        audio_file = os.path.join(project_root, "Recordings", "D Sax.wav")
        sample_rate, audio_data = wavfile.read(audio_file)

        alto_pitches = {
            138.59: "B3",   # Low Bb
            146.83: "H3",    # Low B 
            155.56: "C4",    # Low C 
            164.81: "C#4",   # Low C#
            174.61: "D4",    # Low D 
            185.00: "D#4",   # Low D#
            196.00: "E4",    # Low E 
            207.65: "F4",    # Low F 
            220.00: "F#4",   # Low F#
            233.08: "G4",    # Low G 
            246.94: "G#4",   # Low G#
            261.63: "A4",    # Middle A
            277.18: "B4",   # Middle Bb
            293.66: "H4",    # Middle B 
            311.13: "C5",    # Middle C 
            329.63: "C#5",   # Middle C#
            349.23: "D5",    # Middle D 
            369.99: "D#5",   # Middle D#
            392.00: "E5",    # Middle E 
            415.30: "F5",    # Middle F 
            440.00: "F#5",   # Middle F#
            466.16: "G5",    # High G 
            493.88: "G#5",   # High G#
            523.25: "A5",    # High A 
            554.37: "B5",   # High Bb
            587.33: "H5",    # High B 
            622.25: "C6",    # High C 
            659.25: "C#6",   # High C#
            698.46: "D6",    # High D 
            739.99: "D#6",   # High D#
            783.99: "E6",    # High E 
            830.61: "F6",    # High F 
            880.00: "F#6"    # High F#
        }

        alto_frequencies = np.array(list(alto_pitches.keys()))

        if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
        
        # Get min and max instantly
        min = np.min(audio_data)
        max = np.max(audio_data)

        # Filter out only the positive numbers
        positive_values = audio_data[audio_data > 4000]

        # Calculate the average safely using float64 to prevent overflow
        avg = np.mean(positive_values, dtype=np.float64)

        frequencies = np.fft.rfftfreq(len(audio_data), d=1/sample_rate)
        amplitudes = np.abs(np.fft.rfft(audio_data))

        mask = frequencies <= 2000
        vis_freqs = frequencies[mask]
        vis_amps = amplitudes[mask]

        step = 1
        freqs_list = vis_freqs[::step].tolist()
        amps_list = vis_amps[::step].tolist()

        sampled_data = audio_data[100000:100500].tolist() #D
        #sampled_data = audio_data[30000:31000:1].tolist() #G
        json_array = json.dumps(sampled_data)

        freqs_json = json.dumps(freqs_list)
        amps_json = json.dumps(amps_list)

        js_code = f"updateWaveform({json_array}, {freqs_json}, {amps_json}, 'Low D on Saxophone')"
        self.browser.page().runJavaScript(js_code)

        # Find the closest frequency to the target frequency
        target = freqs_list[np.argmax(amps_list)]
        idx = np.abs(alto_frequencies - target).argmin()


        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Total numbers: {len(audio_data)}")
        print(f"Max value: {max}")
        print(f"Average value: {avg}")
        print(f"Number of positive values: {len(positive_values)}")
        print(f"Frequency: {target} Hz")
        print(f"Closest matching frequency: {alto_frequencies[idx]} Hz")
        print(f"Corresponding pitch: {alto_pitches[alto_frequencies[idx]]}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()
    sys.exit(app.exec())