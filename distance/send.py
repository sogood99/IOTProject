# run this code as the sender
# always run recv first

import pyaudio
import socket
from scipy.fft import fft, fftfreq
import time
import threading
import struct
from utils import *


# Beep beep sender
class Sender:
    def __init__(self, addr):
        self.s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr

        self.s_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_recv.bind(('0.0.0.0', SEND_PORT))

        self.p_in = pyaudio.PyAudio()
        self.p_out = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None

        self.t_a1, self.t_a2, self.t_a3 = None, None, None
        self.t_b1, self.t_b2, self.t_b3 = None, None, None

        self.listenThread = threading.Thread(target=self.startListen)

        self.sendThread = None

    def startListen(self):
        self.stream_in = self.p_in.open(
            format=pyaudio.paInt16, channels=1, rate=RATE, input=True)

        isA2 = True
        A2Ended = False
        while True:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            data = np.frombuffer(data, dtype=np.int16)
            freq = findNearest(fftfreq(len(data), d=1 / RATE), FREQ)
            data_fft = fft(data)[freq]

            if data_fft.max() > 500:
                if isA2:
                    self.t_a2 = time.time()
                    isA2 = False
                elif A2Ended:
                    self.t_b3 = time.time()
                    break
            elif isA2:
                A2Ended = True

        self.stream_in.stop_stream()
        self.stream_in.close()
        self.p_in.terminate()

    def start(self):
        self.s_send.connect((self.addr, RECV_PORT))
        self.t_a1 = time.time()

        wav = (AMPLITUDE * np.sin(2 * np.pi * np.arange(SAMPLES)
                                  * FREQ / RATE)).astype(np.int16)
        self.stream_out = self.p_out.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True,
                                          frames_per_buffer=CHUNK)

        self.listenThread.start()
        self.stream_out.write(wav)

        self.stream_out.stop_stream()
        self.stream_out.close()
        self.p_out.terminate()

        self.s_recv.listen(1)
        self.s_recv.accept()
        self.t_b1 = time.time()

        self.listenThread.join()

        print(self.t_b3 - self.t_b1)
        self.s_send.sendall(struct.pack('f', self.t_b3 - self.t_b1))

        self.s_send.close()
        self.s_recv.close()


if __name__ == '__main__':
    for i in range(10):
        sender = Sender("192.168.0.156")
        sender.start()
        time.sleep(1)
