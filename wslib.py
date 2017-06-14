#!/usr/bin/env python

import re
import time
import threading
from ws4py.client.threadedclient import WebSocketClient

import log

def send_wait(ws, data_arr, timeout=1000, regex_pattern=""):
    if regex_pattern is not None and regex_pattern != "":
        log.get_logger().log("Using regex: {}".format(regex_pattern), log.DEBUG)
        ws.set_regex_match(regex_pattern)

    for data in data_arr:
        log.get_logger().log("Sending: {}".format(data), log.DEBUG) 
        ws.send(data)

    elapsed = 0.0 
    while elapsed < timeout:
        start = int(round(time.time() * 1000))
        ws.s_lock.acquire()
        if ws.s_done:
            break
        ws.s_lock.release()
        elapsed += int(round(time.time() * 1000)) - start
        
    return ws.s_data

def create_ws(url, headers=[]):
    ws = WSClient(url, headers)
    log.get_logger().log("Created WS ({}, {}).".format(url, headers), log.DEBUG)
    ws.s_done = False
    ws.s_match_regex = False
    ws.s_data = []

    return ws

class WSClient(WebSocketClient):
    def __init__(self, url, headers):
        WebSocketClient.__init__(self, url, headers=headers)
        self.s_lock = threading.Lock()
        self.s_done = False
        self.s_match_regex = False
        self.s_data = []

    def opened(self):
        log.get_logger().log("WebSocket opened.", log.INFO)
        return

    def closed(self, code, reason):
        log.get_logger().log("WebSocket closed: ({}, {})".format(code, reason), log.INFO)
        self.set_s_done(True)
        return

    def received_message(self, m):
        log.get_logger().log("WebSocket receved: {}".format(m), log.INFO)
        self.s_data.append(str(m))

        if self.s_match_regex:
            message = str(m)
            log.get_logger().log("Matching '{}' with pattern '{}'.".format(message, self.s_pattern), log.DEBUG)
            if re.search(self.s_pattern, message):
                log.get_logger().log("Found match: {}".format(message), log.DEBUG)
                self.set_s_done(True) 
        return

    def set_regex_match(self, pattern):
        self.s_match_regex = True
        self.s_pattern = pattern
    
    def unset_regex_match(self):
        self.s_match_regex = False
        self.s_pattern = None

    def set_s_done(self, value):
        self.s_lock.acquire()
        self.s_done = value
        self.s_lock.release()


def validate_fix_url(url):
    if re.match(r'^http://', url):
        url = "ws://" + url[7:]
    elif re.match(r'^https://', url):
        url = "wss://" + url[8:]
    elif re.match(r'^ws(s)?://', url) is None:
        url = "ws://" + url 
    return url
