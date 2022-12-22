import numpy as np
import matplotlib.pyplot as plt

LEN_SIZE = 8  # 8 bits
MAX_LEN = 31*8  # bits
SAMPLES = 1000
RATE = 44100
CHUNK = RATE//5  # RATE / number of updates per second
DURATION = SAMPLES/RATE
FREQ_ON = 1000
FREQ_OFF = 2000
ACCESS_ADDRESS = "10001110100010011011111011010110"  # 4 bytes of address
PREAMBLE = "01010101" if ACCESS_ADDRESS[0] == '0' else "10101010"
BLUETOOTH_PREFIX = PREAMBLE + ACCESS_ADDRESS
BLUETOOTH_PREFIX_LEN = len(BLUETOOTH_PREFIX)
HEADER_LEN = BLUETOOTH_PREFIX_LEN + LEN_SIZE
MIN_AMP = 500
RECV_PORT = 5000
SEND_PORT = 5001
FREQ = 1000
AMPLITUDE = 32767


def findNearest(array, value):
    return np.abs(array - value).argmin()


def bin2Int(bin):
    return int(bin, 2)


def str2Bin(s: str) -> str:
    # ASCII string to binary representation (in string)
    return ''.join(format(ord(char), '08b') for char in s)


def bin2ASCII(bin):
    # binary 01010 str to asci str

    s = ""
    for i in range(0, len(bin), 8):
        binOfChar = bin[i:i+8]
        ordOfChar = bin2Int(binOfChar)
        char = chr(ordOfChar)
        s += char
    return s
