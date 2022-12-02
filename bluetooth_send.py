# Takes in string, encodes in bytes, adds Bluetooth protocol headers, use FSK to play
# Split if necessary
# Assume BT4
# Bit (String) in format "01"

import tkinter as tk
import numpy as np
from scipy.io import wavfile

MAX_LEN = 31*8 # bits

# input string generate FSK signal
def FSK_singal(input_bin):
    sr = 48000
    duration = 0.01
    freq1 = 1000
    freq2 = 2000
    signal = np.array([])

    on_signal = np.sin(np.pi * 2 * freq1 * np.arange(0, duration, 1.0/sr))
    off_signal = np.sin(np.pi * 2 * freq2 * np.arange(0, duration, 1.0/sr))
    for i in iter(str(input_bin)):
        if i == '0':
            signal = np.append(signal, off_signal)
        else:
            signal = np.append(signal, on_signal)
    
    signal *= 32767
    signal = np.int16(signal)
    wavfile.write("file.wav", sr, signal)

# return binary string
def string_to_bin(s:str) -> str:
    return ''.join(format(ord(char), '032b') for char in s)

# packet data into bluetooth packet structure
# assume data length <= 31
def packet_data(data: str):
    access_address = "10001110100010011011111011010110" # 4 bytes of address
    preamble = "01010101" if access_address[0] == '0' else "10101010"

    # PDU_type = "0000"
    # reserve = "00"
    # tx_address = "0"
    # rx_address = "0"

    # header = PDU_type + reserve + tx_address + rx_address + length

    length =  "{0:08b}".format(len(data)//8)[::-1]

    return preamble + access_address + length + data

def process_string(s:str):
    bin_string = string_to_bin(s)
    list_data = [ bin_string[i:i+MAX_LEN] for i in range(0, len(bin_string), MAX_LEN) ]

    list_packet = [packet_data(data) for data in list_data]

    return list_packet

def audio_reader():
    # change this to change input file name
    file_name = "file.wav"


if __name__ == "__main__":
    s = "你好abcddfadfsdfhdhagdnagadj"
    
    # main window for GUI
    root = tk.Tk()
    root.geometry("400x300")
    root.title("BT sender")

    def send():
        data = textbox.get("1.0", "end-1c")
        FSK_singal(process_string(data))

    label = tk.Label(root, text = "Data:")
    label.pack(padx=20, pady=20)

    textbox = tk.Text(root, height=5, width=20)
    textbox.pack(padx=20, pady=20)

    button = tk.Button(root, text="Send", command=send)
    button.pack(padx=20, pady=20)
    root.mainloop()