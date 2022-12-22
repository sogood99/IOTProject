# run this code as the sender
# always run distance_receiver first

from utils import *
import pyaudio
import numpy as np

AMPLITUDE = 32767
DURATION = 0.1


if __name__ == '__main__':

    # create sine wave
    num_samples = DURATION * RATE
    sine_wave = (AMPLITUDE * np.sin(2 * np.pi *
                 np.arange(num_samples) * FREQ_ON / RATE)).astype(np.int16)

    # connect to receiver server
    host = 'local host'
    port = 5000
    
    # create a socket at client side
    # using TCP / IP protocol
    s = socket.socket(socket.AF_INET,
                    socket.SOCK_STREAM)
    
    # connect it to server and port
    # number on local computer.
    s.connect(('127.0.0.1', port))

    # play audio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)
    stream.write(sine_wave)

    stream.stop_stream()
    stream.close()
    p.terminate()