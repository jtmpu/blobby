#!/usr/bin/env python

import time
import threading

from ws4py.client.threadedclient import WebSocketClient

def send_wait(ws, data_arr, timeout):
    for data in data_arr:
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

def create_ws(url, headers=[], debug=False):
    ws = WSClient(url, debug)
    ws.s_done = False
    ws.s_data = []

    return ws

class WSClient(WebSocketClient):
    def __init__(self, url, debug):
        WebSocketClient.__init__(self, url)
        self.debug = debug
        self.s_lock = threading.Lock()
        self.s_done = False
        self.s_data = []

    def opened(self):
        if self.debug:
            print("[+] WebSocket opened.")
        return

    def closed(self, code, reason):
        if self.debug:
            print("[+] WebSocket closed")
        self.set_s_done(True)
        return

    def received_message(self, m):
        if self.debug:
            print("[+] WebSocket receved: {}".format(m))
        self.s_data.append(str(m))
        return

    def set_s_done(self, value):
        self.s_lock.acquire()
        self.s_done = value
        self.s_lock.release()
