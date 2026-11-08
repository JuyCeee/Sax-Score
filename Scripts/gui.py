# Tuned to some Razer mic set at 50% Sensitivity, recorded with the Microsoft Recorder app

import json
import sys
import os
import random
from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLabel, QPushButton, QMainWindow, QHBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView 
from PySide6.QtCore import QUrl
import sounddevice as sd
from scipy.io import wavfile
from scipy.signal import find_peaks
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sax Score")
        self.setGeometry(100, 100, 970, 600)

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
        audio_file = os.path.join(project_root, "Recordings", "Alle meine Entchen 190bpm.wav") # Change this to the path of your audio file
        sample_rate, audio_data = wavfile.read(audio_file)

        alto_pitches = {
            138.59: "A#3",   # Low A#
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
            277.18: "A#4",   # Middle A#
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
            554.37: "A#5",   # High A#
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
        
        # Get min and max
        min_val = np.min(audio_data)
        max_val = np.max(audio_data)

        # Filter out only the positive numbers
        positive_values = audio_data[audio_data > 4000]

        # Calculate the average safely using float64 to prevent overflow
        avg = np.mean(positive_values, dtype=np.float64)

        frequencies_t = np.fft.rfftfreq(len(audio_data), d=1/sample_rate)
        amplitudes_t = np.abs(np.fft.rfft(audio_data))

        mask = (frequencies_t >= 120) & (frequencies_t <= 10000)
        vis_freqs_t = frequencies_t[mask]
        vis_amps_t = amplitudes_t[mask]

        step_t = 500

        sampled_data_t = audio_data[::step_t].tolist()

        freqs_list_t = vis_freqs_t[::step_t].tolist()
        amps_list_t = vis_amps_t[::step_t].tolist()

        samples_per_segment = int(4096 * sample_rate / 48000) # Tweak this number if analasys is too inaccurate

        volume_threshold = 500

        pitches_detected = []

        # peak_indeces_amps, _ = find_peaks(audio_data, height=volume_threshold, distance=1)
        # peak_amps = audio_data[peak_indeces_amps]
        # peak_indices_volume, properties = find_peaks(peak_amps, height=volume_threshold, distance=1, prominence=3000)
        # peak_volume = peak_indeces_amps[peak_indices_volume]
        # # peak_volume_widths = properties['widths']
        # peak_volume_l_threshold = properties['prominences']

        # peak_volume_list = peak_volume.tolist()
        # # peak_volume_widths_list = peak_volume_widths.tolist()
        # peak_volume_l_threshold_list = peak_volume_l_threshold.tolist()

        # # print("Peak amps:", peak_amps)
        # print("Peak volume:", peak_volume_list)
        # print("Peak volume widths:", peak_volume_l_threshold_list)
        # print("Length of peak volume list:", len(peak_volume_list))
        # # peak_indices_volume_adjusted = [x // samples_per_segment for x in peak_indices_volume]
        # # print("Peak indices for volume (adjusted):", peak_indices_volume_adjusted)

        rectified_audio = np.abs(audio_data.astype(np.float64))

        window_size = 1500
        window = np.ones(window_size) / window_size
        envelope = np.convolve(rectified_audio, window, mode='same')

        dynamic_prominence_array = envelope * 0.03

        # minimum_prominence = np.max(envelope) * 0.02
        dynamic_prominence_array = np.clip(dynamic_prominence_array, 200, None)

        peak_volume, _ = find_peaks(envelope, height=volume_threshold, distance=5604, prominence=dynamic_prominence_array)
        peak_volume_list = peak_volume.tolist()

        

        # Downsample the new arrays for the web graph
        sampled_envelope = envelope[::step_t].tolist()
        scaled_peak_indices = [int(p / step_t) for p in peak_volume_list]

        json_array = json.dumps(sampled_data_t)
        env_json = json.dumps(sampled_envelope)
        peaks_json = json.dumps(scaled_peak_indices)
        freqs_json = json.dumps(freqs_list_t)
        amps_json = json.dumps(amps_list_t)

        # Push all 5 arrays to the JS frontend
        js_code = f"updateWaveform({json_array}, {env_json}, {peaks_json}, {freqs_json}, {amps_json})"
        self.browser.page().runJavaScript(js_code)



        print("Peak volume:", peak_volume_list)
        print("Peak volume count:", len(peak_volume_list))

        for i in range(0, len(audio_data), samples_per_segment):
            audio_sliced = audio_data[i:i+samples_per_segment]
            if len(audio_sliced) < 512:
                continue

            volume = np.sqrt(np.mean(audio_sliced.astype(np.float64)**2))
            if volume < volume_threshold:
                pitches_detected.append(0)
                continue

            # print(volume)

            windowed_audio = audio_sliced * np.hanning(len(audio_sliced))

            frequencies = np.fft.rfftfreq(16384, d=1/sample_rate)
            amplitudes = np.abs(np.fft.rfft(windowed_audio, n=16384))

            mask = (frequencies >= 50) & (frequencies <= 10000)
            vis_freqs = frequencies[mask]
            vis_amps = amplitudes[mask]

            step = 1
            freqs_list = vis_freqs[::step].tolist()
            amps_list = vis_amps[::step].tolist()

            sampled_data = audio_sliced.tolist() #D
            # sampled_data = audio_data[30000:31000:1].tolist() #G
            # sampled_data = audio_data[150000:151000:1].tolist() #hG
            pitch = self.analyze_segment(sampled_data, freqs_list, amps_list, sample_rate, alto_frequencies, alto_pitches, audio_data, avg, positive_values, max_val)
            pitches_detected.append(pitch)

        for i in range(1, len(pitches_detected) - 1):
            if pitches_detected[i] != pitches_detected[i-1] and pitches_detected[i] != pitches_detected[i+1]:
                pitches_detected[i] = pitches_detected[i+1]

        # print("Detected pitches:", pitches_detected)
        # print("Length of detected pitches:", len(pitches_detected))
        structured_pitches, structured_lengths = self.structure_data(pitches_detected, samples_per_segment, peak_volume_list)
        # print("Structured pitches:", structured_pitches)
        # print("Structured lengths:", structured_lengths)

        lengths_and_pitches = [f"{pitch}: {length}" for pitch, length in zip(structured_pitches, structured_lengths)]
        print(lengths_and_pitches)

        # print(len(structured_pitches))


    # For optimization: look at input/output, what could be moved where, whats only needed for prints, etc.
    def analyze_segment(self, sampled_data, freqs_list, amps_list, sample_rate, alto_frequencies, alto_pitches, audio_data, avg, positive_values, max_val):
        # json_array = json.dumps(sampled_data)

        min_volume = np.max(amps_list) * 0.15

        # freqs_json = json.dumps(freqs_list)
        # amps_json = json.dumps(amps_list)

        # js_code = f"updateWaveform({json_array}, {freqs_json}, {amps_json})"
        # self.browser.page().runJavaScript(js_code)

        # Find the closest frequency to the target frequency
        freqs_list_arr = np.array(freqs_list)
        amps_list_arr = np.array(amps_list)
        #distance might be too big, still giving multiple values for same peek, doesnt matter for now js keep in mind
        peak_indices, _ = find_peaks(amps_list, height=min_volume, distance=20) 
        isolated_peak_freqs = freqs_list_arr[peak_indices]
        isolated_peak_amps = amps_list_arr[peak_indices]

        # target = freqs_list[np.argmax(amps_list)]
        if len(peak_indices) > 0:
            target = isolated_peak_freqs[0]
            # print(isolated_peak_freqs)
            #print(peak_indices)
        else:
            # print(0)
            return(0)
        #print(isolated_peak_freqs)
        idx = np.abs(alto_frequencies - target).argmin()


        # print(f"Sample Rate: {sample_rate} Hz")
        # print(f"Total numbers: {len(audio_data)}")
        # print(f"Max value: {max_val}")
        # print(f"Average value: {avg}")
        # print(f"Number of positive values: {len(positive_values)}")
        # print(f"Frequency: {target} Hz")
        # print(f"Closest matching frequency: {alto_frequencies[idx]} Hz")
        # print(f"Corresponding pitch: {alto_pitches[alto_frequencies[idx]]}")
        return(alto_pitches[alto_frequencies[idx]])

    def structure_data(self, data, samples_per_segment, segmentation):

        active_pitch = None
        pitches = []
        lengths = []

        peak_segments = [int(p / samples_per_segment) for p in segmentation]
        peak_segments.append(float('inf'))
        j = 0

        for i, pitch in enumerate(data):
            peak_crossed = False
            while i >= peak_segments[j]:
                peak_crossed = True
                j += 1

            if pitch == 0:
                peak_crossed = False

            if active_pitch == pitch:
                if peak_crossed and active_pitch != 0 and lengths[-1] >= 2:
                    pitches.append(active_pitch)
                    lengths.append(1)
                else:
                    if len(lengths) > 0:
                        lengths[-1] += 1
            else:
                active_pitch = pitch
                pitches.append(active_pitch)
                lengths.append(1)

        if len(pitches) > 0 and pitches[0] == 0: 
            pitches.pop(0)
            lengths.pop(0)
        if len(pitches) > 0 and pitches[-1] == 0:
            pitches.pop()
            lengths.pop()

        return pitches, lengths


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()
    sys.exit(app.exec())