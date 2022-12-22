import socket
import time
import numpy as np
import pyaudio
import threading
from scipy.fft import fft, fftfreq
from .utils import *


# beep beep receiver
class Recv:
    def __init__(self):
        self.s_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_recv.bind(('0.0.0.0', RECV_PORT))

        self.s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.p_in = pyaudio.PyAudio()
        self.p_out = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None

        self.t_a0, self.t_a2, self.t_a3 = None, None, None
        self.t_b1, self.t_b2, self.t_b3 = None, None, None

        self.listenThread = threading.Thread(target=self.startListen)
        self.listenThread.start()

        self.sendThread = None

    def startListen(self):
        self.stream_in = self.p_in.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True)

        isA3 = True
        while True:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            data = np.frombuffer(data, dtype=np.int16)
            freq = findNearest(fftfreq(len(data), d=1 / RATE), FREQ)
            data_fft = fft(data)[freq]

            if data_fft > 1500:
                if isA3:
                    self.t_a3 = time.time()
                    isA3 = False
                else:
                    self.t_b2 = time.time()
                    break

        self.stream_in.stop_stream()
        self.stream_in.close()
        self.p_in.terminate()

    def startSend(self, addr):
        wav = (AMPLITUDE * np.sin(2 * np.pi * np.arange(SAMPLES) * FREQ / RATE)).astype(np.int16)
        self.stream_out = self.p_out.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)
        self.s_send.connect((addr, SEND_PORT))

        self.t_b1 = time.time()
        self.stream_out.write(wav)

        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()

    def start(self):
        self.s_recv.listen(1)
        _, addr = self.s_recv.accept()

        self.t_a0 = time.time()

        self.sendThread = threading.Thread(target=self.startSend, args=(addr,))
        self.sendThread.start()

        self.sendThread.join()
        self.listenThread.join()


# listen for connection on socket, when received connection, start timer
if __name__ == '__main__':
    pass
