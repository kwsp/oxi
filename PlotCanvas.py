from typing import Tuple

from PyQt6.QtWidgets import (
    QSizePolicy,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotCanvas(FigureCanvas):
    """
    Custom QT5 widget for a matplotlib plot
    """

    def __init__(self, parent, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self._axes = fig.add_subplot(111)
        # self._line, = self._axes.plot([]) # type: ignore

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._data = []
        self._ylim: Tuple[float, float] = (-5, 5)
        self.plot()

    def plot(self):
        self._axes.cla()  # type: ignore
        self._axes.plot(self._data)  # type: ignore
        self._axes.set_ylim(self._ylim)  # type: ignore
        self._axes.set_title("Oscilloscope")  # type: ignore
        self.draw()

    def slot_update_plot(self, arr):
        self._data = arr
        self.plot()

    def slot_update_ylim(self, ylim: Tuple[float, float]):
        self.ylim = ylim
