# run this code as the sender
# always run recv first


import socket
import numpy as np
import pyaudio
from utils import *
import time


class Sender:

    def __init__(self, addr, port=5000) -> None:
        pass

    def start(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(
            width=2), channels=1, rate=RATE, output=True)
        signal = AMPLITUDE * np.sin(np.pi * 2 * FREQ *
                                    np.arange(0, 0.2, 1.0 / RATE))
        port = 5000
        host_ip = "192.168.0.156"
        while (1):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                s.connect((host_ip, port))
            except socket.error:
                break

            stream.write(np.int16(signal).tobytes())
            time.sleep(2)
        stream.stop_stream()
        stream.close()

        p.terminate()
