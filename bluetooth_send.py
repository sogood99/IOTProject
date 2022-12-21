# Takes in string, encodes in bytes, adds Bluetooth protocol headers, use FSK to play
# Split if necessary
# Assume BT4
# Bit (String) in format "01"

import numpy as np
import pyaudio
from utils import *


# packet data into bluetooth packet structure
# assume data length <= 31


def process_string(s: str):
    bin_string = str2Bin(s)
    list_data = [bin_string[i:i+MAX_LEN]
                 for i in range(0, len(bin_string), MAX_LEN)]

    def packet_data(data: str):
        length = "{0:08b}".format(len(data)//8)[::-1]

        return BLUETOOTH_PREFIX + length + data

    list_packet = [packet_data(data) for data in list_data]

    return list_packet

# input string generate FSK signal


def FSK_signal(input_bin):
    signal = np.array([])

    on_signal = np.sin(np.pi * 2 * FREQ_ON * np.arange(0, DURATION, 1.0/RATE))
    off_signal = np.sin(np.pi * 2 * FREQ_OFF *
                        np.arange(0, DURATION, 1.0/RATE))
    for i in iter(str(input_bin)):
        if i == '0':
            signal = np.append(signal, off_signal)
        else:
            signal = np.append(signal, on_signal)

    signal *= 32767
    signal = np.int16(signal)
    return signal


if __name__ == "__main__":
    s = "This is the code inside the thing for the thingy magisdfsdfsdfsdfsdfsdg"

    bits = process_string(s)
    print(len(bits[0]))
    signal = [FSK_signal(bitstream) for bitstream in bits]

    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(
        width=2), channels=1, rate=RATE, output=True)
    for s in signal:
        stream.write(s)
    stream.stop_stream()
    stream.close()

    p.terminate()

    print(len(bits[0]))
    with open('test.txt', 'w') as f:
        t = np.concatenate(signal)
        np.savetxt(f, t)
