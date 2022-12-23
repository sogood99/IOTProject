import socket
import struct
import time
import numpy as np
import pyaudio
import threading
from scipy.fft import fft, fftfreq
from utils import *


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

        self.t_a1, self.t_a2, self.t_a3 = None, None, None
        self.t_b1, self.t_b2, self.t_b3 = None, None, None

        self.listenThread = threading.Thread(target=self.startListen)

        self.sendThread = None

    def startListen(self):
        self.stream_in = self.p_in.open(
            format=pyaudio.paInt16, channels=1, rate=RATE, input=True)

        isA3 = True
        A3Ended = False
        while True:
            data = self.stream_in.read(CHUNK, exception_on_overflow=False)
            data = np.frombuffer(data, dtype=np.int16)
            freq = findNearest(fftfreq(len(data), d=1 / RATE), FREQ)
            data_fft = np.abs(fft(data)[freq])

            #print(data_fft)

            if data_fft.max() > 500:
                if isA3:
                    self.t_a3 = time.time()
                    print("Received A3 at {}".format(self.t_a3))
                    isA3 = False
                elif A3Ended:
                    self.t_b2 = time.time()
                    print("Received B2 at {}".format(self.t_b2))
                    break
            elif isA3:
                A3Ended = True

        self.stream_in.stop_stream()
        self.stream_in.close()
        self.p_in.terminate()

    def startSend(self, addr):
        wav = (AMPLITUDE * np.sin(2 * np.pi * np.arange(SAMPLES)
                                  * FREQ / RATE)).astype(np.int16)
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
        s, addr = self.s_recv.accept()

        self.t_a1 = time.time()

        self.listenThread.start()

        self.sendThread = threading.Thread(target=self.startSend, args=(addr[0],))
        self.sendThread.start()

        self.sendThread.join()
        self.listenThread.join()

        b_diff = s.recv(1024)
        b_diff = struct.unpack('f', b_diff)[0]
        print(b_diff)

        c = 337 * 100
        D = c / 2 * ((self.t_a3 - self.t_a1) - b_diff)

        self.s_recv.close()
        self.s_send.close()
        return D


# listen for connection on socket, when received connection, start timer
if __name__ == '__main__':
    d = []
    for i in range(10):
        receiver = Recv()
        d.append(receiver.start())
        time.sleep(0.5)
    print(d)
    print(sum(d) / len(d))
