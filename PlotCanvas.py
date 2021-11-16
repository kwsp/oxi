from typing import Tuple, Optional

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
        fig.tight_layout()
        self._axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        FigureCanvas.updateGeometry(self)

        self._data = []
        self._legend = None
        self._ylim: Tuple[float, float] = (-5, 5)
        self._xlim: Tuple[float, float] = (0, 500)
        self._plot()

    def _plot(self):
        self._axes.cla()  # type: ignore
        if self._legend:
            self._axes.plot(self._data, label=self._legend)  # type: ignore
            self._axes.legend() # type: ignore
        else:
            self._axes.plot(self._data)  # type: ignore
        self._axes.set_ylim(self._ylim)  # type: ignore
        self._axes.set_xlim(self._xlim)  # type: ignore
        self._axes.set_ylabel("Voltage (V)") # type: ignore
        self._axes.set_title("Oscilloscope")  # type: ignore
        self.draw()

    def slot_update_plot(self, arr, legend: Optional[str] = None):
        self._data = arr
        self._legend = legend
        self._plot()

    def slot_update_ylim(self, ylim: Tuple[float, float]):
        self._ylim = ylim

    def slot_update_xlim(self, xlim: Tuple[float, float]):
        self._xlim = xlim
