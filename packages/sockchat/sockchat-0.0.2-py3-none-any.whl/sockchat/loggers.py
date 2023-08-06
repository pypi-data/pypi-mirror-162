class Logger:
    def log(self, message):
        raise NotImplementedError()


class SyslogLogger(Logger):
    def __init__(self):
        import syslog
        self.syslog = syslog

    def log(self, message):
        self.syslog.syslog(message)


class VoidLogger(Logger):
    def __init__(self):
        pass

    def log(self, message):
        pass


def get_logger() -> Logger:
    try:
        return SyslogLogger()
    except ModuleNotFoundError:
        # Для систем не поддерживающих syslog
        return VoidLogger()
