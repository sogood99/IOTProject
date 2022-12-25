import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import pyaudio
import time
from .recv import Decoder
from utils import *


class PyAudioWorker(QObject):
    finished = pyqtSignal(str, float)

    def __init__(self, widget) -> None:
        self.widget = widget

        self.p = None
        self.stream = None

        self.recieve = False
        self.firstRecv = True

        self.decoder = Decoder()
        self.decodedText = ""
        self.timeUsed = 0

        self.debug = widget.debug
        self.total_data = np.array([])

        self.lastReceiveTime = 0

        super().__init__()

    def closeStream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

        self.stream = None
        self.p = None

    def stopListen(self):
        self.recieve = False
        self.firstRecv = True

    def startListen(self):
        """
            Start collecting data
        """
        if self.recieve:
            return
        self.recieve = True

        # Finish setup, start receiving

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True,
                                  frames_per_buffer=CHUNK)

        self.total_data = np.array([])
        lastBool = False
        while self.recieve:
            if self.firstRecv:
                # remove first recv due to
                np.frombuffer(self.stream.read(CHUNK), dtype=np.int16)
                self.firstRecv = False
            else:
                data = np.frombuffer(self.stream.read(CHUNK), dtype=np.int16)
                currentBool = self.decoder.process(data)

                if self.debug:
                    self.total_data = np.append(self.total_data, data)
                    print(self.total_data)

                if lastBool == False and currentBool == True:
                    self.startTime = time.time()
                    self.lastReceiveTime = time.time()

                elif lastBool == True and currentBool == False:
                    print("Finished Decoding")

                    self.lastReceiveTime = time.time()
                    text = self.decoder.getOutput()
                    print("Decoded Text", text)
                    while text != None:
                        self.decodedText += text
                        text = self.decoder.getOutput()

                    # check if ETX char
                    if self.decodedText != "" and ord(self.decodedText[-1]) == 3:
                        self.timeUsed = time.time() - self.startTime
                        self.finished.emit(
                            self.decodedText[:-1], self.timeUsed)
                        self.recieve = False
                elif lastBool == False and currentBool == False and self.lastReceiveTime != 0:
                    timeDiff = time.time() - self.lastReceiveTime
                    if timeDiff > 15:
                        self.timeUsed = time.time() - self.startTime
                        self.finished.emit(
                            self.decodedText, self.timeUsed)
                        self.recieve = False

                lastBool = currentBool

        self.closeStream()


class RecvWidget(QWidget):
    def __init__(self, parent=None, debug=False):
        """
            Initialize many things for QWidget and set up GUI
        """
        super().__init__(parent)

        self.setWindowTitle("Reciever")

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
        self.recieveLabel.setText("Not Receiving")

        self.textBox = QTextEdit(self)
        self.textBox.setGeometry(500, 0, 400, 500)
        self.textBox.setReadOnly(True)
        self.textBox.show()

        self.debug = debug
        if self.debug:
            self.total_data = []

        self.worker = PyAudioWorker(self)
        self.thread = QThread(self)

    def closeEvent(self, a0) -> None:
        print("Closing")
        self.closeWorker()
        return super().closeEvent(a0)

    def closeWorker(self):
        self.worker.stopListen()
        self.thread.quit()
        self.thread.wait()

    def newWorker(self):
        self.worker = PyAudioWorker(self)
        self.thread = QThread(self)

    def start(self):
        self.recieveIndicator.setStyleSheet(
            "QLabel { background-color: green }")
        self.recieveLabel.setText("Recieving")

        self.closeWorker()
        self.newWorker()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.startListen)

        def pyaudioFinished(decodedText, timeUsed):
            if decodedText != "" or timeUsed != 0:
                self.textBox.setText(decodedText)
                msg = QMessageBox()
                msg.setText("Finished Recv Text: {}s".format(timeUsed))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            self.stop()

        self.worker.finished.connect(pyaudioFinished)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def reset(self):
        self.textBox.setText("")

    def stop(self):
        self.recieveIndicator.setStyleSheet(
            "QLabel { background-color: grey }")
        self.recieveLabel.setText("Not Receiving")
        if self.debug:
            self.total_data = self.worker.total_data
            canvas = FigureCanvasQTAgg(Figure(figsize=(8, 5)))
            ax = canvas.figure.subplots()
            canvas.flush_events()
            canvas.draw()
            ax.clear()
            ax.plot(self.total_data)
            ax.set_ylim(-32768, 32767)
            canvas.show()
            print(len(self.total_data))
            with open("test_recv.txt", "w") as f:
                np.savetxt(f, self.total_data)
        self.closeWorker()
        self.newWorker()


def startRecvGUI(debug=False):
    a = QApplication(sys.argv)
    w = RecvWidget(debug=debug)
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    DEBUG = False
    startRecvGUI(DEBUG)
