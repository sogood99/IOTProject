import socket
import pyaudio
import time
import numpy as np
from scipy.fft import fft, fftfreq
from scipy import signal
from utils import *
# from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# from sklearn.cluster import KMeans


class Recv:
    def __init__(self, port=5000) -> None:
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))
        s.listen(1)
        dist = []

        while len(dist) < 20:
            client, addr = s.accept()

            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(
                width=2), channels=1, rate=RATE, input=True, output=True)
            # idx = findNearest(fftfreq(CHUNK//10), FREQ)
            startTime = 0
            endTime = 0
            OFFSET = 1715 - 150
            while True:
                data = np.frombuffer(stream.read(CHUNK, False), dtype=np.int16)

                f, t, Zxx = signal.stft(
                    data, RATE, nperseg=NPERSEG, noverlap=0, boundary=None)
                idx = findNearest(f, FREQ)
                amp = np.abs(Zxx)

                if amp[idx].max() > 200:
                    endTime += np.where(amp[idx] > 100)[0][0] * NPERSEG
                    print(endTime)
                    # endTime = time.time()
                    t_diff = (endTime - startTime) / RATE
                    # t_diff = endTime - startTime
                    print("dist ", 343 * t_diff * 100)
                    x = 343 * t_diff * 100
                    # y = -156.91087048 + 0.72303024*x
                    dist.append(x)
                    break
                elif endTime - startTime > 99999:
                    break
                else:
                    endTime += len(data)

            stream.stop_stream()
            stream.close()
            time.sleep(1)
        # plt.hist(dist, bins=10)
        # plt.show()
        # print(np.mean(dist))
        return np.mean(dist)
