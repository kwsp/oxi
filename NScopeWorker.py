from contextlib import contextmanager

from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np


class NScopeWorker(QThread):
    """
    QThread object that handles talking to the nScope on a separate thread
    """

    output = pyqtSignal(int)
    output_arr = pyqtSignal(list)
    signal_fs = pyqtSignal(float)
    signal_error = pyqtSignal(str)  # any error during run
    signal_running = pyqtSignal(bool)  # when nScope running state changes

    def __init__(self, parent=None):
        # init is executed in the calling thread
        QThread.__init__(self, parent)

        self._ns = None
        self._fs = 1000
        self._n_samples = 500
        self.signal_fs.connect(self.slot_fs_update)

    def _init_nscope(self):
        if self._ns is None:
            from nscopeapi import nScope

            self._ns = nScope()

    def run(self):
        # run is executed in the new thread
        try:
            # Init nScope if we hasn't already
            self._init_nscope()
            assert self._ns is not None

            self.signal_running.emit(True)

            # init channel 1
            ns = self._ns
            ns.setSampleRateInHz(self._fs)
            ns.setChannelsOn(True, False, False, False)  # Turn on channel 1
            counter = 0
            while not self.isInterruptionRequested():

                # AX1 is the red LED, 650nm
                # with self.sendSineWave(1, 1000, 1.5):  # send pulse
                # read signal
                self._n_samples = 5000
                data = self.readCh(1)  # array of self._n_samples (500) points
                # calculate the peak and trough of the sine wave
                self.output_arr.emit(data)

                # # AX2 is the red LED, 940nm
                # with self.sendSineWave(2, 1000, 1.5):  # send pulse
                    # # read signal
                    # data = self.readCh(1)
                    # self.output_arr.emit(data)

                # # AX1 is the red LED, 650nm
                # with self.sendPulseWave(1):
                    # # read signal
                    # data = self.readCh(1)  # array of self._n_samples (500) points
                    # # calculate the peak and trough of the sine wave
                    # self.output_arr.emit(data)

                # # AX2 is the red LED, 940nm
                # with self.sendPulseWave(1):
                    # # read signal
                    # data = self.readCh(1)
                    # self.output_arr.emit(data)

                counter += 1
                self.output.emit(counter)

        except Exception as e:
            self.signal_error.emit(str(e))

        # clean up
        if self._ns:
            # turn off all channels
            self._ns.setChannelsOn(False, False, False, False)

        self.signal_running.emit(False)

    def slot_fs_update(self, new_fs: float):
        "TODO: unused"
        self._fs = new_fs

    def readCh(self, ch: int):
        ns = self._ns
        assert ns is not None
        ns.requestData(self._n_samples)
        data = []
        while ns.requestHasData():
            data.append(ns.readData(ch))

        # release request resources
        ns.releaseRequest()
        return data

    @contextmanager
    def sendSineWave(self, ax: int, freq: float, amplitude: float):
        "Send sine wave and turn AX off when context ends"
        ns = self._ns
        assert ns is not None
        try:
            ns.setAXOn(ax, True)
            ns.setAXFrequencyInHz(ax, freq)
            ns.setAXAmplitude(ax, amplitude)
            yield
        finally:
            ns.setAXOn(ax, False)


    @contextmanager
    def sendPulseWave(self, px: int, duty: float = 100., periodMs: float = 250.):
        "Send pulse and turn AX off when context ends"
        ns = self._ns
        assert ns is not None
        try:
            ns.setPXDutyPercentage(px, duty)
            ns.setPXPeriodInMs(px, periodMs)
            ns.setPXOn(px, True)
            yield
        finally:
            ns.setPXOn(px, False)
