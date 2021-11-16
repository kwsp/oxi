import sys

from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from NScopeWorker import NScopeWorker
from PlotCanvas import PlotCanvas


class App(QWidget):
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

        self._counter = 0
        self._update_legend_prev = 0

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self._title)
        self.setGeometry(self._left, self._top, self._width, self._height)

        # main window Horizontal layout
        overallLayout = QHBoxLayout()
        overallLayout.addWidget(self.createOscilloScopeGroup())
        overallLayout.addWidget(self.createControlDataGroup())

        self.setLayout(overallLayout)
        self.show()

    def createOscilloScopeGroup(self):
        # left side: oscilloscope
        self._canvas = PlotCanvas(self, width=5, height=4)
        self._nscope_worker.output_arr.connect(self.slot_update_plot)
        return self._canvas

    def slot_update_plot(self, arr):
        if self._counter == self._update_legend_prev:
            legend = "940 nm"
            self._update_legend_prev -= 1
        else:
            legend = "650 nm"
            self._update_legend_prev = self._counter + 1

        self._canvas.slot_update_plot(arr, legend)

    def createControlDataGroup(self):
        # right side: controls and buttons
        # Button to toggle nScope
        self._buttonOnOff = buttonOnOff = QPushButton("Start" )
        buttonOnOff.setToolTip("Toggle the oscilloscope")
        buttonOnOff.clicked.connect(self.slot_toggleOnOff)

        self._oxi_label = QLabel("")
        self._oxi_label.setToolTip("Blood oxygenation estimate")

        # TODO: change button to label later just to display data
        self._bt1 = bt1 = QPushButton("" )
        bt1.setToolTip("No. of cycles collected")
        bt1.setDisabled(True)

        # y resolution slider
        y_slider = QSlider(self)
        y_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        y_slider.setTickInterval(5)
        y_slider.setMaximum(5) # max range: 5V
        y_slider.setMinimum(1) # min range: 1V
        y_slider.setSingleStep(1)
        y_slider.setValue(5)
        y_slider.valueChanged.connect(self.slot_handle_y_slider_changed)

        x_slider = QSlider(self)
        x_slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
        x_slider.setTickInterval(100)
        x_slider.setMaximum(5000) # max range: 5V
        x_slider.setMinimum(1000) # min range: 1V
        x_slider.setSingleStep(100)
        x_slider.setValue(500)
        x_slider.valueChanged.connect(self.slot_handle_x_slider_changed)

        self._sliderGroup = sliderGroup = QGroupBox("Resolution")
        box = QHBoxLayout()
        box.addWidget(y_slider)
        box.addWidget(x_slider)
        sliderGroup.setLayout(box)

        rightVBox = QVBoxLayout()
        rightVBox.addWidget(buttonOnOff)
        rightVBox.addWidget(self._oxi_label)
        rightVBox.addWidget(bt1)
        rightVBox.addWidget(sliderGroup)

        rightGroupBox = QGroupBox()
        rightGroupBox.setLayout(rightVBox)
        return rightGroupBox


    def slot_handle_output(self, x):
        self._counter = x
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
        QMessageBox.clickedButton
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec_()

    def slot_handle_y_slider_changed(self, val):
        self._canvas.slot_update_ylim((0, val))

    def slot_handle_x_slider_changed(self, val):
        self._canvas.slot_update_xlim((0, val))

    def slot_toggleOnOff(self):
        if self._nscope_worker.isRunning():
            # Thread is currently running
            self._nscope_worker.requestInterruption()
            self._buttonOnOff.setText("Stopping...")
            self._buttonOnOff.setDisabled(True)

        else:
            # Thread is not currently running
            self._nscope_worker.start()
            self._buttonOnOff.setText("Starting...")
            self._buttonOnOff.setDisabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())
