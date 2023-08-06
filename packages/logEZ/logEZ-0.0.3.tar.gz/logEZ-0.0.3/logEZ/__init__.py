import logging

rootLogger = logging.getLogger()

class MyLogger:
    def __init__(
        self,
        log_file_name="logEZ.log",
        logging_level="INFO",
        disable_console_logs=False,
        disable_file_logs=False
    ) -> None:

        if disable_console_logs and disable_file_logs:
            raise Exception("Both console and file logs are disabled")

        self.logging_levels = {
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Uses structure: 17-11-21 11:26:34 - root : DEBUG : MyLogger initialized...
        logFormatter = logging.Formatter(
            "%(asctime)s - %(name)s : %(levelname)s : %(message)s", "%d-%m-%y %H:%M:%S"
        )

        rootLogger.setLevel(self.logging_levels[logging_level])

        if not disable_file_logs:
            # Save logs to log file
            fileHandler = logging.FileHandler(log_file_name)
            fileHandler.setFormatter(logFormatter)
            rootLogger.addHandler(fileHandler)

        if not disable_console_logs:
            # Show logs on console
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logFormatter)
            rootLogger.addHandler(consoleHandler)

        self.myDebug("logEZ initialized...")

    def setLoggingLevel(self, level):
        rootLogger.setLevel(self.logging_levels[level])

    def myDebug(self, inString):
        rootLogger.debug(inString)

    def myInfo(self, inString):
        rootLogger.info(inString)

    def myWarn(self, inString):
        rootLogger.warning(inString)

    def myError(self, inString, exc_info=False):
        rootLogger.error(inString, exc_info=exc_info)

    def myCrit(self, inString, exc_info=False):
        rootLogger.critical(inString, exc_info=exc_info)

    def myExcept(self, inString):
        rootLogger.exception(inString)
