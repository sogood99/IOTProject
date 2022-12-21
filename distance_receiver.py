import pyaudio

AMPLITUDE = 32767
DURATION = 0.1


def play_audio():
    # create sine wave
    num_samples = DURATION * RATE
    sine_wave = (AMPLITUDE * np.sin(2 * np.pi *
                 np.arange(num_samples) * FREQ_ON / RATE)).astype(np.int16)

    # play audio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True)
    stream.write(sine_wave)

    stream.stop_stream()
    stream.close()
    p.terminate()


# listen for audio, when a large amplitude is detected, play sine wave and stop listening
if __name__ == '__main__':
    pass
# TODO: implement this