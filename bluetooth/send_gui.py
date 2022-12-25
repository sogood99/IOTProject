import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from .send import *
from utils import *


class PyaudioWorker(QObject):
    # Worker inside QThread that sends sound signal, and measures time used to send
    sender = Sender()
    finished = pyqtSignal(float)
    text = ""

    def send(self):
        startTime = time.time()
        self.sender.process(self.text)
        self.finished.emit(time.time()-startTime)


class SendWidget(QWidget):
    def __init__(self, parent=None, debug=False):
        """
            Initialize many things for QWidget and set up GUI
        """
        super().__init__(parent)

        self.setWindowTitle("Sender")

        self.setFixedSize(900, 600)
        self.view = QWidget(self)
        self.view.setGeometry(0, 0, 400, 500)
        self.view.show()

        # Initialize other gui elements
        self.textBox = QTextEdit(self)
        self.textBox.setGeometry(300, 0, 300, 400)
        self.textBox.show()

        self.playButton = QPushButton("Send", self)
        self.playButton.setGeometry(300, 500, 300, 100)
        self.playButton.clicked.connect(self.send)
        self.playButton.show()

        self.worker = PyaudioWorker()
        self.thread = QThread(self)

    def send(self):
        # send textbox text to PyAudioWorker
        text = self.textBox.toPlainText()

        self.closeWorker()
        self.newWorker()

        self.worker.text = text
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.send)

        def pyaudioFinished(timeUsed):
            msg = QMessageBox()
            msg.setText("Finished Send Text: {}s".format(timeUsed))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        self.worker.finished.connect(pyaudioFinished)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def closeEvent(self, a0) -> None:
        print("Closing")
        self.closeWorker()
        return super().closeEvent(a0)

    def closeWorker(self):
        self.thread.quit()
        self.thread.wait()

    def newWorker(self):
        self.worker = PyaudioWorker()
        self.thread = QThread(self)


def startSendGUI(debug=False):
    a = QApplication(sys.argv)
    w = SendWidget(debug=debug)
    w.show()
    sys.exit(a.exec())


if __name__ == "__main__":
    DEBUG = False
    startSendGUI(DEBUG)
