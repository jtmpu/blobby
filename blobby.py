#!/usr/bin/env python

import re
import os
import sys
import argparse

import log
import wslib
import wsflasklib

def parse_cli_args():
    """
    Returns a dict with the run time options required
    to run blobby
    """ 
    parser = argparse.ArgumentParser(description="A CLI for websockets.")
    parser.add_argument("--echo", help="Output the parsed arguments.", default=False, action="store_true")

    subparsers = parser.add_subparsers(help="Sub command help")

    client_parser = subparsers.add_parser("client", help="Run blobby as a CLI client")
    client_parser.add_argument("--module", default="client", help="Name of the current module")
    client_parser.add_argument("-u", "--url", help="The URL for the Web-Socket endpoint", required=True)
    client_parser.add_argument("-t", "--timeout", help="Max amount of milliseconds to wait", default=1000, type=int)
    client_parser.add_argument("-p", "--pattern", help="If specified, uses this regex pattern to determine when the correct message has been received. Uses re.search(<pattern,...)", default="")
    client_parser.add_argument("-d", "--data", help="The data to send to the websocket", nargs="*", default=[])
    client_parser.add_argument("-H", "--headers", help="Array with headers, specified in the form of -H \"Content-Type: blabla\" \"X-Custom-Header: qwe\"", nargs="*", default=[])
    client_parser.add_argument("-l", "--loglevel", help="What log messages to receive", choices=log.SEVERITY_TO_STR, default=log.SEVERITY_TO_STR[2])

    service_parser = subparsers.add_parser("service", help="Run blobby as an HTTP service")
    service_parser.add_argument("--module", default="service", help="Name of the current module")
    service_parser.add_argument("-p", "--port", help="The port for the HTTP service. (Port 5000 default)", default=5000, type=int)
    service_parser.add_argument("-fd", "--flask-debug", help="Run flask in debug mode", default=False, action="store_true")
    service_parser.add_argument("-l", "--loglevel", help="What log messages to receive", choices=log.SEVERITY_TO_STR, default=log.SEVERITY_TO_STR[2])
    args = parser.parse_args()

    return vars(args)

def client_validate_fix_inputs(args):
    # Check for "ws(s)?://" at the beginning, or add it for the lazy users
    args["url"] = wslib.validate_fix_url(args["url"])

    # TODO: Do this correctly
    headers = args["headers"]
    headers = map(lambda x: x.split(":", 1), headers)
    
    incorrect_headers = filter(lambda x: len(x) != 2, headers)
    if len(incorrect_headers) > 0:
        for ih in incorrect_headers:
            log.get_logger().log("Incorrect header: {}".format(":".join(ih)), log.ERROR)
        sys.exit()
    
    
    for index, value in enumerate(headers):
        headers[index] = map(lambda x: x.strip(), value)
    headers = map(tuple, headers)
    args["headers"] = headers

    return args

def service_validate_fix_inputs(args):
    return args

if __name__ == "__main__":
    args = parse_cli_args() 
    
    module = args["module"]

    if module == "client":
        args = client_validate_fix_inputs(args)
    elif module == "service":
        args = service_validate_fix_inputs(args)

    if args["echo"]:
        print(args)

    elif module == "client":
        url = args["url"]
        data = args["data"]
        sev = args["loglevel"]
        timeout = args["timeout"]
        headers = args["headers"]
        pattern = args["pattern"]
        
        log.get_logger().set_output_severity(sev)
        
        ws = wslib.create_ws(url, headers=headers)
        ws.connect()
        responses = wslib.send_wait(ws, data, timeout, regex_pattern=pattern)
        for response in responses:
            print(response)

    elif module == "service":
        port = args["port"]
        sev = args["loglevel"]
        flask_debug = args["flask_debug"]
        log.get_logger().set_output_severity(sev)
        wsflasklib.run_service(port, flask_debug)
