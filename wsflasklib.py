#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
from flask import Flask
from flask import Response
from flask import request
from flask import make_response

import log
import wslib

app = Flask(__name__)

ENDPOINTS = {"send_wait" : "/ws/send_wait"}
SIMPLE_PAGE_TEMPLATE="""
<html>
<body>
{}
</body>
</html>
"""

@app.route("/")
def default_page():
    response = "<h1>Blobby HTTP Service</h1><h2>API Endpoints</h2>"
    for key, value in ENDPOINTS.iteritems():
        response += "<a href='{}'>{}</a>\n".format(value, key)

    response += "</body></html>"
    return SIMPLE_PAGE_TEMPLATE.format(response)

def show_api_info(endpoint):
    log.get_logger().log("Showing API info for: {}".format(endpoint))
    response = "<h1>Send_Wait</h1>"
    response +="<p>Send data via a websocket</p>"
    response +="<h2>Specification</h2>"
    response +="""<code>
POST /ws/send_wait HTTP/1.1<br/>
Host: 127.0.0.1:5000<br/>
Content-Type: application/json<br/>
Content-Length: 7<br/>
O-Url: http://ws.domain.tld:21938/wsendpoint<br/>
O-Timeout: 1000<br/>
O-Header-RegexPattern: [^q]+<br/>
O-Header-Cookie: PHPSESSID=hgcu3c99epbbqo98ojru4pv8k5<br/>
<br/>
["qwe", {"some_type":"value"}]<br/>
</code>
<br>
<code>
POST /ws/send_wait HTTP/1.1<br>
Host: 127.0.0.1:5000<br>
Content-Type: application/blobby<br>
O-Url: http://127.0.0.1:19080<br>
O-Timeout: 1000<br>
O-Delimiter: |DELIM|<br>
O-Return-JSON: True<br>
O-Header-Cookie: PHPSESSID=hgcu3c99epbbqo98ojru4pv8k5<br>
<br>
{"username":"admin","password":"admin"}|DELIM|<br>
{"request":"set","property":"test","value":"qwe"}<br>

</code>"""
    response += "<p>All options are sent as headers with the 'O-' prefix</p>"
    response += "<p>Specify websocket endpoint in the URL param (will transform http(s) to ws(s), or add ws)</p>"
    response += "<p>Specify messages to send as elements in a JSON array</p>"
    response += "<p>Timeout is the maximum amount of time to wait.</p>"
    response += "<p>Specify a regex to match the message to wait for</p>"
    response += "<p>Prefix any headers that should be sent with the 'O-Header-' prefix.</p>"
    response += "<p>When using application/blobby, specify the char-sequence which splits the messages with the O-Delimiter header</p>"
    response += "<p>If O-Return-JSON is set to true, the server attempts to parse the responses from the web application as JSON to return a better format of the data.</p>"
    return SIMPLE_PAGE_TEMPLATE.format(response)

@app.route(ENDPOINTS["send_wait"], methods=["GET", "POST"])
def http_send_wait():
    if request.method == "GET":
        return show_api_info(ENDPOINTS["send_wait"])
    else:
        return run_send_wait()

def run_send_wait():
    errors = {}

    url = ""
    timeout = 1000
    regex_pattern = ""
    delimiter = "|"
    return_json = False
    headers = []
    for key, value in request.headers.iteritems():
        key = key.lower()
        if re.match("^o-", key):
            new_key = key[2:]
            if re.match("^header-", new_key):
                header_key = new_key[7:]
                headers.append((header_key, value))
            elif re.match("^url", new_key):
                url = wslib.validate_fix_url(value)
            elif re.match("^timeout", new_key):
                try:
                    timeout = int(value)
                except:
                    errors["timeout"] = "Failed to parse timeout as int." 
            elif re.match("^regexpattern", new_key):
                try:
                    re.compile(value)
                    regex_pattern = value
                except Exception as e:
                    errors["regexpattern"] = "Failed to parse regexpattern: {}".format(e)
            elif re.match("^delim", new_key):
                delimiter = value
            elif re.match("^return-json", new_key):
                return_json = value.lower() == "true"

    if len(url) == 0:
        errors["url"] = "Need a url for the websocket endpoint"

    if len(errors) > 0:
        return str(errors), 500, { "Content-Type" : "application/json" }

    json_data = []
    if request.content_type == "application/blobby":
        log.get_logger().log("Content-Type is text/blobby, using a known delimiter to find the message-strings.")
        data = request.data
        json_data = filter(lambda x: len(x) > 0, data.split(delimiter))
    elif request.content_type == "application/json":
        log.get_logger().log("Content-Type is application/json, WebSocket messages have been sent as JSON structures")
        data = request.get_json(force=True)
        if isinstance(data, list):
           json_data =  map(lambda x: json.dumps(x), data)
        else:
            return str({"error":"Specify each JSON message to send as an element in an array."}), 408
    else:
        return str({"error":"Incompatible content-type. Use text/plain or application/json"}), 408

    log.get_logger().log("Performing WebSocket request with: {} - {} - {}".format(url, headers, json_data), log.INFO) 

    # TODO: Error check the input json data
    ws = wslib.create_ws(url, headers)
    ws.connect()
    ws_data = wslib.send_wait(ws, json_data, timeout, regex_pattern)

    resp_data = json.dumps(ws_data)
    if return_json:
        json_arr = []
        for data in ws_data:
            elem = ""
            try:
                # Attempt to return a proper JSON array with elements in it 
                elem = json.loads(data)
            except:
                # Just encode it as string, something something lol
                elem = data
            json_arr.append(elem)
        resp_data = json.dumps(json_arr)
            
    
    return resp_data, 200, { "Content-Type": "application/json" }

def run_service(port, flask_debug):
    log.get_logger().log("Starting flask service", log.INFO)
    app.run(debug=flask_debug)
    return 
