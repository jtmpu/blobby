#!/usr/bin/env python

import re
import os
import sys
import argparse

import wslib

def parse_cli_args():
    """
    Returns a dict with the run time options required
    to run blobby
    """ 
    parser = argparse.ArgumentParser(description="A CLI for websockets.")

    parser.add_argument("--echo", help="Output the parsed arguments.", default=False, action="store_true")
    parser.add_argument("-u", "--url", help="The URL for the Web-Socket endpoint", required=True)
    parser.add_argument("-t", "--timeout", help="Max amount of milliseconds to wait", default=1000, type=int)
    parser.add_argument("-d", "--data", help="The data to send to the websocket", nargs="*", default=[])
    parser.add_argument("-H", "--headers", help="Array with headers, specified in the form of -H \"Content-Type: blabla\" \"X-Custom-Header: qwe\"", nargs="*", default=[])
    args = parser.parse_args()

    # Check for "ws(s)?://" at the beginning, or add it for the lazy users
    if re.match(r'^http://', args.url):
        args.url = "ws://" + args.url[7:]
    elif re.match(r'^https://', args.url):
        args.url = "wss://" + args.url[8:]
    elif re.match(r'^ws(s)?://', args.url) is None:
        args.url = "ws://" + args.url 

    # TODO: Do this correctly
    args.headers = map(lambda x: x.split(":", 1), args.headers)
    for index, value in enumerate(args.headers):
        args.headers[index] = map(lambda x: x.strip(), value)
    args.headers = map(tuple, args.headers)

    return vars(args)

if __name__ == "__main__":
    args = parse_cli_args() 

    if args["echo"]:
        print(args)
        sys.exit()

    url = args["url"]
    data = args["data"]
    timeout = args["timeout"]
    headers = args["headers"]
    
    ws = wslib.create_ws(url, headers=headers, debug=False)
    ws.connect()
    responses = wslib.send_wait(ws, data, timeout)
    for response in responses:
        print(response)
