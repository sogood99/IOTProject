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
        if len(data) == 0:
            return False

        f, t, Zxx = signal.stft(
            data, RATE, nperseg=SAMPLES, noverlap=0, boundary=None)
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

    # A = self.buffer_on or buffer_off,
    # returns the probability that i has on/off value
    def metric(self, A, i):
        # leftMetric = sigmoid(7*(A[i]-1/3))
        # rightMetric = sigmoid(7*(A[i+1]-1/3))
        # if leftMetric > 3/4:
        #     return 1
        # if leftMetric > 1/2 and rightMetric > 1/2:
        #     return 1
        return A[i]

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
        current = self.findNextNonZero(0)

        bitLength = len(self.buffer_off)

        while current + HEADER_LEN <= bitLength and current >= 0:
            print("Start", current)

            payloadLength = self.decodeHeader(current)
            print("Payload Length", payloadLength)

            if payloadLength == None:
                # false positive
                current = self.findNextNonZero(current+1)
            else:
                # everything fine
                payloadStart = current + HEADER_LEN
                if payloadStart + payloadLength > bitLength:
                    break
                decodedStr = self.decodeBTBits(payloadStart, payloadLength)
                self.output.append(decodedStr)

                current = self.findNextNonZero(
                    current + HEADER_LEN + payloadLength + 1)

            # process bits
        self.buffer_off = []
        self.buffer_on = []

    def decodeHeader(self, start):
        bits = ""
        assert len(self.buffer_on) >= start + HEADER_LEN

        for i in range(HEADER_LEN):
            if self.metric(self.buffer_on, start+i) > 1/2:
                bits += "1"
            else:
                bits += "0"

        return bin2Int(bits[BLUETOOTH_PREFIX_LEN: BLUETOOTH_PREFIX_LEN + LEN_SIZE][::-1]) * 8

    # decode bluetooth bits to ascii, if error output None

    def decodeBTBits(self, start, length):
        if length == 0:
            return ""
        decodedStr = ""
        decodedBits = ""
        for i in range(0, length, 8):
            asciiBit = ""
            asciiStart = start + i
            for j in range(8):
                if self.metric(self.buffer_on, asciiStart + j) > 1/2:
                    asciiBit += "1"
                else:
                    asciiBit += "0"
            decodedStr += bin2ASCII(asciiBit)
            decodedBits += asciiBit

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
    print(decoder.process(data))
    import matplotlib.pyplot as plt
    x = np.arange(len(decoder.buffer_off))
    plt.scatter(x, decoder.buffer_on, label="one")
    plt.scatter(x, decoder.buffer_off, label="zero")
    plt.show()
    print(decoder.processBuffer())
    print(decoder.getOutput())
    print(decoder.getOutput())
