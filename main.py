"""
Send sine wave at 1000Hz
"""
from contextlib import contextmanager
import sys

from nscopeapi import nScope
import numpy as np
import matplotlib.pyplot as plt


class App:
    def __init__(self):
        self.ns = nScope()

        # initialise channel 1
        desired_fs = 10000
        self.ns.setSampleRateInHz(desired_fs)
        self.fs = self.ns.getSampleRateInHz()
        assert (
            self.fs == desired_fs
        ), f"Want to sample at {desired_fs}Hz, can only do {self.fs}"
        print(f"Sampling freq: {self.fs}Hz")
        self.ns.setChannelOn(1, True)  # Turn on channel 1

    def main(self):

        # init plots
        fig, ax = plt.subplots()
        fig.canvas.mpl_connect("key_press_event", self.handleKeyPress)

        ax.set_ylim([0, 5])
        ax.set_ylabel("Voltage (V)")
        ax.set_xlabel("Time (s)")
        ax.set_title("Oscilloscope")
        plt.ion()
        plt.show()

        with self.sendPulse(1, 100, 5):
            res = self.readCh1()
            line, = ax.plot(res)
            # TODO: this isn't really async
            fig.canvas.flush_events()

        # main loop
        while True:
            # send sine wave on AX1
            with self.sendPulse(1, 100, 5):
                res = self.readCh1()
                line.set_ydata(res)
                line.figure.canvas.draw_idle()
                line.figure.canvas.flush_events()

    def readCh1(self, nSamples: int = 5000):
        "Read"
        res = self.ns.readCh1(nSamples, self.fs)
        return np.array(res)

    @contextmanager
    def sendPulse(self, ax: int, freq: float, amplitude: float):
        "Send pulse and turn AX off when context ends"
        ns = self.ns
        try:
            ns.setAXOn(ax, True)
            ns.setAXFrequencyInHz(ax, freq)
            ns.setAXAmplitude(ax, amplitude)
            yield
        finally:
            ns.setAXOn(ax, False)

    def handleKeyPress(self, event):
        "Key press handler for MPL"
        if event.key in ("q", "esc"):
            self.exit()

    def exit(self):
        print("Bye bye")
        sys.exit(0)


if __name__ == "__main__":
    app = App()
    try:
        app.main()
    except KeyboardInterrupt:
        app.exit()
