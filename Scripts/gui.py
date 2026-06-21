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
        audio_file = "S:\VSC\Sax-Score\Recordings\D Sax.wav"
        sample_rate, audio_data = wavfile.read(audio_file)

        if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]
        
        # 1. Get min and max instantly
        min = np.min(audio_data)
        max = np.max(audio_data)

        # 2. Filter out only the positive numbers
        positive_values = audio_data[audio_data > 4000]

        # 3. Calculate the average safely using float64 to prevent overflow
        avg = np.mean(positive_values, dtype=np.float64)

        frequencies = np.fft.rfftfreq(len(audio_data), d=1/sample_rate)
        amplitudes = np.abs(np.fft.rfft(audio_data))

        sampled_data = audio_data[100000:100500].tolist() #D
        #sampled_data = audio_data[30000:31000:1].tolist() #G
        json_array = json.dumps(sampled_data)
        js_code = f"updateWaveform({json_array}, 'Low D on Saxophone')"
        self.browser.page().runJavaScript(js_code)

        print(f"Sample Rate: {sample_rate} Hz")
        print(f"Total numbers: {len(audio_data)}")
        print(f"Min value: {min}")
        print(f"Max value: {max}")
        print(f"Average value: {avg}")
        print(f"Number of positive values: {len(positive_values)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()
    sys.exit(app.exec())