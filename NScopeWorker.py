from PyQt5.QtCore import QThread, pyqtSignal
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
        self._fs = 10000
        self._n_samples = 500
        self.signal_fs.connect(self.slot_fs_update)

    def run(self):
        # run is executed in the new thread
        try:
            # Init nScope if we hasn't already
            if self._ns is None:
                from nscopeapi import nScope

                self._ns = nScope()

            self.signal_running.emit(True)

            # init channel 1
            ns = self._ns
            ns.setSampleRateInHz(self._fs)
            ns.setChannelOn(1, True)  # Turn on channel 1
            ns.setChannelsOn(True, False, False, False)
            counter = 0
            while not self.isInterruptionRequested():

                ns.requestData(self._n_samples)

                data = []
                while ns.requestHasData():
                    data.append(ns.readData(1))

                # release request resources
                ns.releaseRequest()

                self.output_arr.emit(data)

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
        self._fs = new_fs
