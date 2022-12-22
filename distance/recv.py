import socket
import pyaudio
import time
import numpy as np

RATE = 44100
FREQ = 2000
AMPLITUDE = 32767
DURATION = 0.1
CHUNK = 1024


# listen for connection on socket, when received connection, start timer
if __name__ == '__main__':
    # take the server name and port name
    port = 5000
    
    # create a socket at server side using TCP / IP protocol
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind the socket with server and port number
    s.bind((socket.gethostname(), port))

    # allow maximum 1 connection to the socket
    s.listen(1)

    # wait till a client accept connection
    c, addr = s.accept()
    start_time = time.time()
    print("Connection from: " + str(addr))

    # TODO invalid output device
    # listen for audio, if amplitude is above threshold, stop timer
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                    input=True, output=True, frames_per_buffer=CHUNK,
                    )

    while True:
        data = stream.read(CHUNK)
        data_int = np.frombuffer(data, dtype=np.int16)
        if data_int.max() > 500:
            break

    stop_time = time.time()
    stream.stop_stream()
    stream.close()
    p.terminate()

    # calculate distance
    distance = (stop_time - start_time) * 34300 / 2

    print("Distance: ", distance, "cm")