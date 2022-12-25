import socket
import pyaudio
import time
import numpy as np
from scipy.fft import fft, fftfreq
from scipy import signal
from utils import *
# from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


class Recv:
    def __init__(self, port=5000) -> None:
        # receive tcp connection from port
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen(1)
        dist = []

        # transmit 20 packets and take mean
        while len(dist) < 20:
            self.startRecv = time.time()
            client, addr = s.accept()

            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(
                width=2), channels=1, rate=RATE, input=True, output=True)
            startTime = 0
            endTime = 0
            while True:
                data = np.frombuffer(stream.read(CHUNK, False), dtype=np.int16)

                f, t, Zxx = signal.stft(
                    data, RATE, nperseg=NPERSEG, noverlap=0, boundary=None)
                idx = findNearest(f, FREQ)
                amp = np.abs(Zxx)

                if amp[idx].max() > 200:
                    # heard from sender, calculate endTime and exit loop
                    endTime += np.where(amp[idx] > 100)[0][0] * NPERSEG
                    t_diff = (endTime - startTime) / RATE
                    x = 343 * t_diff * 100
                    dist.append(x)
                    break
                elif endTime - startTime > 99999:
                    # did not hear from sender timeout, retry
                    break
                else:
                    endTime += len(data)

            stream.stop_stream()
            stream.close()
            time.sleep(1)
        self.endRecv = time.time()
        data = COEFF * np.median(dist) - OFFSET
        print("Used {}s".format(self.endRecv - self.startRecv))
        return data
