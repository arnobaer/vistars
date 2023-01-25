#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Simple CERN vistars viewer.
#

import argparse
import logging
import os
import signal
import ssl
import sys
import time
from urllib.request import urlopen

from PyQt5 import QtCore, QtGui, QtWidgets

__version__ = "1.0.1"

DEFAULT_URL = 'https://vistar-capture.s3.cern.ch/lhc1.png'
DEFAULT_INTERVAL = 25 # sec
DEFAULT_TIMEOUT = 5 # sec

# Workaround for CERTIFICATE_VERIFY_FAILED error on Python3
ssl._create_default_https_context = ssl._create_unverified_context

class ScreenWidget(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(ScreenWidget, self).__init__(parent)
        pixmap = QtGui.QPixmap(1, 1)
        pixmap.fill(QtCore.Qt.black)
        self.setPixmapBuffer(pixmap)
        self.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.black)
        palette.setColor(self.foregroundRole(), QtCore.Qt.white)
        self.setPalette(palette)
        font = self.font()
        font.setPixelSize(160)
        self.setFont(font)

    def setOffline(self, message=None):
        self.setText(message or self.tr("OFFLINE..."))

    def isOnline(self):
        return not self.text()

    def pixmapBuffer(self):
        return self._pixmapBuffer

    def setPixmapBuffer(self, pixmap):
        self._pixmapBuffer = pixmap

    def paintPixmapBuffer(self):
        pixmap = self.pixmapBuffer()
        self.setPixmap(pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio))

    def resizeEvent(self, event):
        """Repaint pixmap on resize."""
        if self.isOnline():
            self.paintPixmapBuffer()
        super(ScreenWidget, self).resizeEvent(event)

class MainWindow(QtWidgets.QWidget):

    def __init__(self, url, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setUrl(url)
        self.setInterval(DEFAULT_INTERVAL)
        self.setTimeout(DEFAULT_TIMEOUT)
        self._mouseMoveTimeout = 2000 # ms
        self._mouseMoveTimer = QtCore.QTimer()
        self.setWindowTitle(self.tr("Vistars"))
        self.resize(800, 600)
        self.setMinimumSize(640, 480)
        # Black background
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(palette)
        # Create screen widget
        self.screenWidget = ScreenWidget(self)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.screenWidget)
        self.setLayout(vbox)
        # Connections
        self._mouseMoveTimer.timeout.connect(self.hideCursor)
        # Enable mouse tracking
        self.setMouseTracking(True)
        self.screenWidget.setMouseTracking(True)

    def refresh(self):
        """Load vistars screen from remote server."""
        logging.info("loading image...")
        success = False
        def watchdog():
            # nasty urllib2 SSL bug...
            if not success:
                logging.error("timeout, urllib2 probably hung up...")
                self.screenWidget.setOffline()
        timer = QtCore.QTimer()
        timer.timeout.connect(watchdog)
        timer.start(self.timeout() * 1000) # ms
        try:
            connection = urlopen(self.url(), timeout=self.timeout()) # sec
            data = connection.read()
            timer.stop()
        except Exception as e:
            timer.stop()
            logging.warning("failed to load remote pixmap: %s", format(e))
            self.screenWidget.setOffline()
        else:
            success = True
            image = QtGui.QImage.fromData(data)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.screenWidget.setPixmapBuffer(pixmap)
            self.screenWidget.paintPixmapBuffer()
            logging.info("updated pixmap (%sx%s).", pixmap.size().width(), pixmap.size().height())

    def url(self):
        return self._url

    def setUrl(self, url):
        self._url = url

    def interval(self):
        return self._interval

    def setInterval(self, interval):
        self._interval = interval

    def timeout(self):
        return self._timeout

    def setTimeout(self, timeout):
        self._timeout = timeout

    def hideCursor(self):
        """Hide cursor if fullscreen."""
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BlankCursor)

    def mouseMoveEvent(self, event):
        """Start timer to hide mouse if not moved."""
        self._mouseMoveTimer.stop()
        while QtWidgets.QApplication.overrideCursor():
            QtWidgets.QApplication.restoreOverrideCursor()
        self._mouseMoveTimer.start(self._mouseMoveTimeout)

    def mouseDoubleClickEvent(self, event):
        """Toggle fullscreen on double click."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'url',
        nargs="?",
        default=DEFAULT_URL,
        help="remote image URL (default {0})".format(DEFAULT_URL),
    )
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=DEFAULT_INTERVAL,
        help="referesh interval in seconds (default {0})".format(DEFAULT_INTERVAL),
    )
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=DEFAULT_TIMEOUT,
        help="connection timeout in seconds (default {0})".format(DEFAULT_TIMEOUT)
    )
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse()

    # Setup logging
    logging.getLogger().setLevel(logging.INFO)

    # Create application
    app = QtWidgets.QApplication(sys.argv)

    # Create window
    win = MainWindow(args.url)
    win.setTimeout(args.timeout)
    win.raise_()
    win.showFullScreen()

    # Initial load
    QtCore.QTimer.singleShot(250, win.refresh)

    # Setup update timer
    timer = QtCore.QTimer()
    timer.timeout.connect(win.refresh)
    timer.start(args.interval * 1000) # ms

    # Terminate application on SIG_INT signal.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Run workloop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
