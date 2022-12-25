# Takes in string, encodes in bytes, adds Bluetooth protocol headers, use FSK to play
# Split if necessary
# Assume BT4
# Bit (String) in format "01"

import numpy as np
import pyaudio
import time
from utils import *


# packet data into bluetooth packet structure
# assume data length <= 31

class Sender:
    # input string, split string into 0<= len <= 31 chunks, process into binary,
    # and add bluetooth header
    def processString(self, s):
        bin_string = str2Bin(s)
        list_data = [bin_string[i:i+MAX_LEN]
                     for i in range(0, len(bin_string), MAX_LEN)]
        if len(list_data) == 0:
            list_data = [""]

        # add 0 to end
        if len(list_data[-1]) + 8 <= MAX_LEN:
            list_data[-1] += ETX
        else:
            list_data.append(ETX)
        print(list_data)

        def packet_data(data: str):
            length = "{0:08b}".format(len(data)//8)[::-1]

            return BLUETOOTH_PREFIX + length + data

        list_packet = [packet_data(data) for data in list_data]

        return list_packet

    # input string generate FSK signal

    def FSK_signal(self, input_bin):
        signal = np.array([])

        on_signal = np.sin(np.pi * 2 * FREQ_ON *
                           np.arange(0, DURATION, 1.0/RATE))
        off_signal = np.sin(np.pi * 2 * FREQ_OFF *
                            np.arange(0, DURATION, 1.0/RATE))
        for i in iter(str(input_bin)):
            if i == '0':
                signal = np.append(signal, off_signal)
            else:
                signal = np.append(signal, on_signal)

        signal *= AMPLITUDE
        signal = np.int16(signal)
        return signal

    # send packet to audio
    def process(self, s):
        bits = self.processString(s)
        signal = [self.FSK_signal(bitstream) for bitstream in bits]

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(
            width=2), channels=1, rate=RATE, output=True)
        for sig in signal:
            stream.write(np.int16(sig).tobytes())
            time.sleep(1.5)
        stream.stop_stream()
        stream.close()

        p.terminate()


if __name__ == "__main__":
    s = "test code"

    sender = Sender()
    sender.process(s)
