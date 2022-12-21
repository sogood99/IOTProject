from scipy import signal
from scipy.special import expit as sigmoid
from utils import *
import matplotlib.pyplot as plt
from utils import *
import numpy as np

DEBUG = True


def findNearest(array, value):
    return np.abs(array - value).argmin()


class Decoder:
    def __init__(self, debug=False) -> None:
        self.debug = debug
        self.buffer_on = []
        self.buffer_off = []
        self.output = []

    # if there is bluetooth signal in data, return true
    # if true, wait for more data
    # if false, start processing data in buffer
    def process(self, data) -> bool:
        f, t, Zxx = signal.stft(
            data, RATE, nperseg=SAMPLES)
        amp = np.abs(Zxx)

        off_freq_index = findNearest(f, FREQ_OFF)
        on_freq_index = findNearest(f, FREQ_ON)

        off_max = amp[off_freq_index].max()
        on_max = amp[on_freq_index].max()

        notFinish = on_max >= 500 or off_max >= 500
        print(list(np.int16(amp[on_freq_index])))
        if notFinish:
            self.buffer_off = np.append(
                self.buffer_off, amp[off_freq_index] / off_max)
            self.buffer_on = np.append(
                self.buffer_on, amp[on_freq_index] / on_max)
        else:
            # start processing
            self.processBuffer()

        if self.debug:
            plt.pcolormesh(t, f, amp, vmin=0,
                           vmax=32767, shading='gouraud')
            plt.show()
        return notFinish

    def metric(self, A, i):
        return sigmoid(5*(A[i]-1/3)) * sigmoid(5*(A[i+1]-1/3))

    # find if there is bit value
    def findNextNonZero(self, start):
        for i in range(start, len(self.buffer_off)-1):
            metricOn = self.metric(self.buffer_on, i)
            metricOff = self.metric(self.buffer_off, i)
            if metricOn > 1/2 or metricOff > 1/2:
                return i

        return -1

    def processBuffer(self):
        assert len(self.buffer_off) == len(self.buffer_on)
        current = 0
        while current < len(self.buffer_off) and current >= 0:
            bits = ""

            satisfyOn, satisfyOff = False, False
            for i in range(current, len(self.buffer_on), 2):
                if i + 1 == len(self.buffer_on):
                    current = -1
                    break

                # check if exactly one of 1/0 is satisfied
                satisfyOn = self.metric(self.buffer_on, i) > 1/2
                satisfyOff = self.metric(self.buffer_off, i) > 1/2
                if satisfyOn == satisfyOff:  # both false => end, both true => end
                    # finished
                    print(self.buffer_on[i], self.buffer_on[i+1])
                    print(self.buffer_off[i], self.buffer_off[i+1])
                    print(self.metric(self.buffer_on, i))
                    print(self.metric(self.buffer_off, i))
                    current = self.findNextNonZero(i+1)
                    break
                else:
                    bits += "1" if satisfyOn else "0"
            current = self.findNextNonZero(i+1)

            print(current, len(self.buffer_off))
            print(bits)
            # process bits
            decodedStr = self.decodeBTBits(bits)
            self.output.append(decodedStr)
        self.buffer_off = []
        self.buffer_on = []

    # decode bluetooth bits to ascii, if error output None
    def decodeBTBits(self, bits):
        print("Decoding BT: {}".format(bits))
        if len(bits) <= BLUETOOTH_PREFIX_LEN + LEN_SIZE:
            print("ERROR: BT Packet too small")
            return None

        if bits[:BLUETOOTH_PREFIX_LEN] != BLUETOOTH_PREFIX:
            print("ERROR: BT Packet Prefix doesnt match")
            return None

        payloadLength = bin2Int(
            bits[BLUETOOTH_PREFIX_LEN: BLUETOOTH_PREFIX_LEN+LEN_SIZE][::-1])
        if len(bits) != BLUETOOTH_PREFIX_LEN + LEN_SIZE + payloadLength * 8:
            print(len(bits), BLUETOOTH_PREFIX_LEN + LEN_SIZE + payloadLength)
            print("ERROR: Payload size doesnt match")
            return None

        decodedStr = ""
        for i in range(BLUETOOTH_PREFIX_LEN+8, len(bits), 8):
            binAscii = bits[i:i+8]
            decodedStr += bin2ASCII(binAscii)

        print("Decoded: {}".format(decodedStr))
        return decodedStr

    def getOutput(self) -> str:
        if len(self.output) > 0:
            return self.output.pop(0)
        return None

    def __len__(self):
        return len(self.output)


if __name__ == "__main__":
    decoder = Decoder(DEBUG)

    with open('test_recv.txt', 'r') as f:
        data = np.loadtxt(f)
    print(len(data)//SAMPLES)
    # data = np.concatenate([[0] * (SAMPLES // 2), data, [0]*(1*(SAMPLES//2))])
    print(decoder.process(data))
    print(decoder.processBuffer())
