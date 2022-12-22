# run this code as the sender
# always run recv first

import pyaudio
import numpy as np
import socket
import time

RATE = 48000
FREQ = 1000
AMPLITUDE = 32767
DURATION = 0.1


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