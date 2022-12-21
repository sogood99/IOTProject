import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import pyaudio
import numpy as np
import time
from threading import Thread

DEBUG = True

RATE = 44100
CHUNK = RATE//2  # RATE / number of updates per second


def soundplot(stream):
    t1 = time.time()
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    print(data)


class CustomWidget(QWidget):
    def __init__(self, parent=None, debug=False):
        """
            Initialize many things for QWidget and set up GUI
        """
        super().__init__(parent)

        self.setFixedSize(900, 600)
        self.view = QWidget(self)
        self.view.setGeometry(0, 0, 400, 500)
        self.view.show()

        # Initialize other gui elements
        self.playButton = QPushButton("Start", self)
        self.playButton.setGeometry(000, 500, 300, 100)
        self.playButton.clicked.connect(self.start)
        self.playButton.show()

        self.playButton = QPushButton("Reset", self)
        self.playButton.setGeometry(300, 500, 300, 100)
        self.playButton.clicked.connect(self.reset)
        self.playButton.show()

        self.endButton = QPushButton("End", self)
        self.endButton.setGeometry(600, 500, 300, 100)
        self.endButton.clicked.connect(self.stop)
        self.endButton.show()

        self.recieveIndicator = QLabel(self)
        self.recieveIndicator.setGeometry(0, 425, 50, 50)
        self.recieveIndicator.setStyleSheet(
            "QLabel { background-color: grey }")

        self.recieveLabel = QLabel(self)
        self.recieveLabel.setGeometry(100, 425, 100, 50)
        self.recieveLabel.setText("Not Recieving")

        self.textBox = QTextEdit(self)
        self.textBox.setGeometry(500, 0, 400, 500)
        self.textBox.setReadOnly(True)
        self.textBox.show()

        self.recieve = False
        self.debug = debug
        if self.debug:
            self.total_data = []

        self.p = pyaudio.PyAudio()
        self.stream = None

    def close(self) -> bool:
        self.closeStream()
        return super().close()

    def start(self):
        self.recieveIndicator.setStyleSheet(
            "QLabel { background-color: green }")
        self.recieveLabel.setText("Recieving")
        newThread = Thread(target=self.startListen)
        newThread.start()

    def reset(self):
        self.textBox.setText("")

    def stop(self):
        self.recieveIndicator.setStyleSheet(
            "QLabel { background-color: grey }")
        self.recieveLabel.setText("Not Recieving")
        self.recieve = False
        if self.debug:
            plt.plot(self.total_data)
            plt.ylim(-32768, 32767)
            plt.show()
            np.savetxt(open("test_recv.txt", "w"), self.total_data)

    def closeStream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

        self.stream = None
        self.p = None

    def startListen(self):
        """
            Start collecting data
        """
        if self.recieve:
            return
        self.recieve = True

        # Finish setup, start recieving

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                                  frames_per_buffer=CHUNK)

        self.total_data = np.array([])
        while self.recieve:
            data = np.frombuffer(self.stream.read(CHUNK), dtype=np.int16)
            self.total_data = np.append(self.total_data, data)

        self.closeStream()

        msg = QMessageBox()
        msg.setText("Finished Recv")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def showCanvas(self, i, ax):
        # Output the resutls to FigureCanvas from matplotlib
        ax.clear()
        ax.set_title("Iteration={}".format(i), fontsize=16)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    w = CustomWidget(debug=DEBUG)
    w.show()
    a.exec()
