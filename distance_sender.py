# run this code as the sender
# always run distance_reciever first

from utils import *
import time
import pyaudio
import numpy as np

AMPLITUDE = 32767
DURATION = 0.1


def measure_distance(time_elapsed):
    # Calculate the distance by multiplying the time elapsed by the speed of sound
    distance = time_elapsed * 343
    return distance


if __name__ == '__main__':

    # create sine wave
    num_samples = DURATION * RATE
    sine_wave = (AMPLITUDE * np.sin(2 * np.pi *
                 np.arange(num_samples) * FREQ_ON / RATE)).astype(np.int16)

    # start timer
    start_time = time.time()

    # play audio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)
    stream.write(sine_wave)

    stream.stop_stream()
    stream.close()
    p.terminate()

    #
