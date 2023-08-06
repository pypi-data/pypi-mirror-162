"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import sys
import logging

try:
    from PySide2 import QtCore
    HAVE_PYSIDE2 = True
except ImportError:
    HAVE_PYSIDE2 = False

from opencmiss.zinc.logger import Logger

ENABLE_STD_STREAM_CAPTURE = False


if HAVE_PYSIDE2:
    class CustomStreamImpl(QtCore.QObject):
        # Signal is a class variable; PySide creates per-instance SignalInstance object of same name
        messageWritten = QtCore.Signal(str, str)

        # Note: if implementing __init__ you must call super __init__ for Signals to work.
        # def __init__(self):
        #     super(CustomStreamImpl, self).__init__()

        def flush(self):
            pass

        def fileno(self):
            return -1

        def write(self, msg, level="INFORMATION"):
            if not self.signalsBlocked():
                self.messageWritten.emit(msg, level)
else:
    class CustomStreamImpl(object):

        def flush(self):
            pass

        def fileno(self):
            return -1

        def write(self, msg, level="INFORMATION"):
            sys.stdout.write(f'{level} - {msg}')


class CustomStream(object):
    _stdout = None
    _stderr = None

    @staticmethod
    def stdout():
        if CustomStream._stdout is None:
            CustomStream._stdout = CustomStreamImpl()
            if ENABLE_STD_STREAM_CAPTURE:
                sys.stdout = CustomStream._stdout
        return CustomStream._stdout

    @staticmethod
    def stderr():
        if CustomStream._stderr is None:
            CustomStream._stderr = CustomStreamImpl()
            if ENABLE_STD_STREAM_CAPTURE:
                sys.stderr = CustomStream._stderr
        return CustomStream._stderr


class LogsToWidgetHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        levelString = record.levelname
        record = self.format(record)
        if record:
            CustomStream.stdout().write('%s\n' % record, levelString)


def setup_custom_logger(name, callback):

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = LogsToWidgetHandler()
    handler.setFormatter(formatter)

    argonLogger = logging.getLogger(name)
    argonLogger.setLevel(logging.DEBUG)
    argonLogger.addHandler(handler)
    return argonLogger


class ArgonLogger(object):
    _logger = None
    _zincLogger = None
    _loggerNotifier = None
    _callback = None

    @staticmethod
    def setCallback(callback):
        """
        Set Argon Logger callback.
        
        :param callback: Callback function.
        """
        ArgonLogger._callback = callback

    @staticmethod
    def getLogger():
        """
        Return the Argon Logger.
        
        :return: ArgonLogger
        """
        if not ArgonLogger._logger:
            ArgonLogger._logger = setup_custom_logger("Argon", ArgonLogger._callback)
        return ArgonLogger._logger

    @staticmethod
    def closeLogger():
        """
        Deletes subobjects of Argon logger to help free memory held by Argon objects earlier.
        """
        if ArgonLogger._logger:
            del ArgonLogger._logger
            ArgonLogger._logger = None
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    @staticmethod
    def writeErrorMessage(string):
        """
        Write Argon Logger Error message.
        
        :param string: string
        """
        ArgonLogger.getLogger().error(string)

    @staticmethod
    def writeWarningMessage(string):
        """
        Write Argon Logger Warning message.
        
        :param string: string
        """
        ArgonLogger.getLogger().warning(string)

    @staticmethod
    def writeInformationMessage(string):
        """
        Write Argon Logger Information message.
        
        :param string: string
        """
        ArgonLogger.getLogger().info(string)

    @staticmethod
    def loggerCallback(event):
        """
        Argon Logger Callback, wirte different type of message based on the input event flags.
        
        :param event: event
        """
        if event.getChangeFlags() == Logger.CHANGE_FLAG_NEW_MESSAGE:
            text = event.getMessageText()
            if event.getMessageType() == Logger.MESSAGE_TYPE_ERROR:
                ArgonLogger.writeErrorMessage(text)
            elif event.getMessageType() == Logger.MESSAGE_TYPE_WARNING:
                ArgonLogger.writeWarningMessage(text)
            elif event.getMessageType() == Logger.MESSAGE_TYPE_INFORMATION:
                ArgonLogger.writeInformationMessage(text)

    @staticmethod
    def setZincContext(zincContext):        
        """
        Set the underlying Zinc context for the Argon Logger.

        :param zincContext: opencmiss.zinc.context.Context
        """
        if ArgonLogger._loggerNotifier:
            ArgonLogger._loggerNotifier.clearCallback()
        ArgonLogger._zincLogger = zincContext.getLogger()
        ArgonLogger._loggerNotifier = ArgonLogger._zincLogger.createLoggernotifier()
        ArgonLogger._loggerNotifier.setCallback(ArgonLogger.loggerCallback)
