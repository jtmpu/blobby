# Blobby
A command line and HTTP interface for interacting with a websocket.

```
usage: blobby.py [-h] [--echo] {client,service} ...

A CLI for websockets.

positional arguments:
  {client,service}  Sub command help
    client          Run blobby as a CLI client
    service         Run blobby as an HTTP service

optional arguments:
  -h, --help        show this help message and exit
  --echo            Output the parsed arguments.
```

## HTTP Interface

Options:

```
usage: blobby.py service [-h] [--module MODULE] [-p PORT] [-fd]
                         [-l {debug,info,warning,error}]

optional arguments:
  -h, --help            show this help message and exit
  --module MODULE       Name of the current module
  -p PORT, --port PORT  The port for the HTTP service. (Port 5000 default)
  -fd, --flask-debug    Run flask in debug mode
  -l {debug,info,warning,error}, --loglevel {debug,info,warning,error}
                        What log messages to receive
```

Example request:

```
POST /ws/send_wait HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/blobby
Content-Length: 99
O-Url: http://127.0.0.1:19080
O-Timeout: 1000
O-Delimiter: |DELIM|
O-Return-JSON: True
O-RegexPattern: "(result|error)":
O-Header-Cookie: PHPSESSID=qwekjas92013i0

{"username":"admin","password":"admin"}|DELIM|
{"request":"set","property":"test","value":"qwe"}
```


## Command Line Interface

Options:

```
usage: blobby.py client [-h] [--module MODULE] -u URL [-t TIMEOUT]
                        [-p PATTERN] [-d [DATA [DATA ...]]]
                        [-H [HEADERS [HEADERS ...]]]
                        [-l {debug,info,warning,error}]

optional arguments:
  -h, --help            show this help message and exit
  --module MODULE       Name of the current module
  -u URL, --url URL     The URL for the Web-Socket endpoint
  -t TIMEOUT, --timeout TIMEOUT
                        Max amount of milliseconds to wait
  -p PATTERN, --pattern PATTERN
                        If specified, uses this regex pattern to determine
                        when the correct message has been received. Uses
                        re.search(<pattern,...)
  -d [DATA [DATA ...]], --data [DATA [DATA ...]]
                        The data to send to the websocket
  -H [HEADERS [HEADERS ...]], --headers [HEADERS [HEADERS ...]]
                        Array with headers, specified in the form of -H
                        "Content-Type: blabla" "X-Custom-Header: qwe"
  -l {debug,info,warning,error}, --loglevel {debug,info,warning,error}
                        What log messages to receive
```

Example:

```
./blobby.py  client --url ws://127.0.0.1:19080 -H "Cookie: PHPSESSID=qwekasjdkj" "X-Forwarded-For: 127.0.0.1" --timeout 5000 --pattern '"(result|error)":' -d '{"username":"admin","password":"admin"}' '{"request":"get","property":"auth"}' 
```
