# run this code as the sender
# always run recv first

import pyaudio
import numpy as np
import socket
from utils import *


# Beep beep sender
class Sender:
    def __init__(self,addr):
        self.s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = addr

        self.s_recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_recv.bind(('0.0.0.0', RECV_PORT))

        self.p_in = pyaudio.PyAudio()
        self.p_out = pyaudio.PyAudio()
        self.stream_in = None
        self.stream_out = None

        self.t_a1, self.t_a2, self.t_a3 = None, None, None
        self.t_b1, self.t_b2, self.t_b3 = None, None, None

        self.listenThread = threading.Thread(target=self.startListen)
        self.listenThread.start()

        self.sendThread = None


if __name__ == '__main__':
    # create sine wave
    num_samples = DURATION * RATE
    sine_wave = (AMPLITUDE * np.sin(2 * np.pi *
                                    np.arange(num_samples) * FREQ / RATE)).astype(np.int16)

    # connect to receiver server
    port = 5000

    # play audio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)

    # connect it to server and port
    # number on local computer.

    # create a socket at client side using TCP / IP protocol
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), port))

    stream.write(sine_wave)

    stream.stop_stream()
    stream.close()
    p.terminate()
