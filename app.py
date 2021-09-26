import sys

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
)

from NScopeWorker import NScopeWorker
from PlotCanvas import PlotCanvas


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._title = "Pulse Oximeter"
        self._left = 10
        self._top = 10
        self._width = 640
        self._height = 400

        self._nscope_worker = NScopeWorker()
        self._nscope_worker.output.connect(self.slot_handle_output)
        self._nscope_worker.signal_error.connect(self.slot_handle_nscope_error)
        self._nscope_worker.signal_running.connect(self.slot_handle_nscope_running)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self._title)
        self.setGeometry(self._left, self._top, self._width, self._height)

        self._canvas = m = PlotCanvas(self, width=5, height=4)
        self._nscope_worker.output_arr.connect(self._canvas.slot_update_plot)
        m.move(0, 0)

        self._bt1 = bt1 = QPushButton("A button", self)
        bt1.setToolTip("Toolip")
        bt1.move(500, 0)
        bt1.resize(140, 100)
        bt1.clicked.connect(m.slot_update_plot)

        bt_on_off = QPushButton("Start", self)
        bt_on_off.setToolTip("Toggle the oscilloscope")
        bt_on_off.move(500, 100)
        bt_on_off.resize(140, 100)
        bt_on_off.clicked.connect(self.toggleOnOff)
        self._buttonOnOff = bt_on_off

        self.show()

    def slot_handle_output(self, x):
        self._bt1.setText(str(x))

    def slot_handle_nscope_running(self, isRunning: bool):
        if isRunning:
            self._buttonOnOff.setText("Stop")
        else:
            self._buttonOnOff.setText("Start")
        self._buttonOnOff.setDisabled(False)

    def slot_handle_nscope_error(self, err_msg: str):
        self._buttonOnOff.setText("Start")
        self.slot_handle_error(err_msg)

    def slot_handle_error(self, err_msg: str):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Error")
        msg_box.setText(err_msg)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.exec_()

    def toggleOnOff(self):
        if self._nscope_worker.isRunning():
            # Thread is currently running
            # self._timer.stop()
            self._nscope_worker.requestInterruption()
            self._buttonOnOff.setText("Stopping...")
            self._buttonOnOff.setDisabled(True)

        else:
            # Thread is not currently running
            # self._timer.start(1000)
            self._nscope_worker.start()
            self._buttonOnOff.setText("Starting...")
            self._buttonOnOff.setDisabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
