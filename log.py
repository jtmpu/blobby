#!/usr/bin/env python

import sys
import time

DEBUG=0
INFO=1
WARNING=2
ERROR=3

SEVERITY_TO_STR = [ "debug", "info", "warning", "error" ]

logger = None
def get_logger():
    global logger
    if logger is None:
        logger = Logger() 
    return logger

class Logger():

    def __init__(self):
        self.severity_level = WARNING

    def set_output_severity(self, severity):
        self.severity_level = SEVERITY_TO_STR.index(severity)
    
    def log(self, msg, severity=INFO):
        if severity >= self.severity_level:
            self._print_log(sys.stdout, severity, msg)

    def _print_log(self, fd, severity, msg):
        str_sev = SEVERITY_TO_STR[severity].upper()
        str_time = time.ctime() + " " + time.tzname[0]
        out = "[{}] [{}]: {}".format(str_sev, str_time, msg)
        fd.write(out + "\n")
