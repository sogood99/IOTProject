import socket
import time
import numpy as np
import pyaudio
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

RATE = 48000
FREQ = 1000
AMPLITUDE = 32767
DURATION = 0.1
CHUNK = 20

def findNearest(array, value):
    return np.abs(array - value).argmin()

# listen for connection on socket, when received connection, start timer
if __name__ == '__main__':
    # take the server name and port name
    port = 5000
    
    # create a socket at server side using TCP / IP protocol
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket with server and port number
    s.bind((socket.gethostname(), port))

    # listen for audio, if amplitude is above threshold, stop timer
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                    input=True, output=True, frames_per_buffer=CHUNK,
                    )


    # allow maximum 1 connection to the socket
    s.listen(1)

    # wait till a client accept connection
    c, addr = s.accept()
    start_time = time.time()

    count = 0
    total_data = np.array([])
    while True:
        data = stream.read(CHUNK, exception_on_overflow = False)
        data_int = np.frombuffer(data, dtype=np.int16)
        # xf = fftfreq(CHUNK, 1 / RATE)
        # amp = np.abs(fft(data_int))
        total_data = np.append(total_data, data_int)
        # idx = findNearest(xf, FREQ)
        if abs(data_int).max() > 2000:
            count += np.where(abs(data_int) > 2000)[0][0]
            # count += CHUNK/2
            break
        else:
            count += CHUNK
    plt.plot(total_data)
    plt.show()

    # stop_time = time.time()
    stream.stop_stream()
    stream.close()
    p.terminate()

    print(count)
    #t_diff = count / RATE
    #distance = 340.29 * (t_diff)*100
    #print(t_diff)
    #print("Distance: ", distance, "cm")

    # calculate distance truth = 60 cm
    # distance = 340.29 * (stop_time - start_time)*100
    # print(stop_time - start_time)
    # print("Distance: ", distance, "cm")