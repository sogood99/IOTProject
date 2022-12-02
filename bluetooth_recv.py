import tkinter as tk
from scipy.fft import fft,fftfreq
import numpy as np

LOWER_BOUND = 2


def decode(filename):
    data, sample_rate = sf.read(filename)

    interval_size = int(0.001*sample_rate)

    # graph
    N = len(data)

    xf = fftfreq(interval_size, 1 / sample_rate)
    idx = np.where(xf == 20000.)[0][0]

    count = 0

    output_bits = ""

    for i in range(int(N/interval_size)):
        yf = fft(data[i*interval_size:(i+1)*interval_size])
        amplitude = np.abs(yf[idx])
        if amplitude > LOWER_BOUND:
            # finish 1 bit
            if count == 1:
                output_bits += "0"
            elif count == 2:
                output_bits += "1"

            count = 0
        else:
            count += 1

    return output_bits

if __name__ == "__main__":
    
    # main window for GUI
    root = tk.Tk()
    root.geometry("400x300")
    root.title("BT reciever")

    label = tk.Label(root, text = "Data:")
    label.pack(padx=20, pady=20)

    textbox = tk.Text(root, height=5, width=20)
    textbox.pack(padx=20, pady=20)

    root.mainloop()