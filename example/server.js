var WebSocketServer = require("websocket").server;
var http = require("http");
var port = 19080;

var server = http.createServer(function(request, response) {
	// Process HTTP Request
});

server.listen(port, function() { });

wsServer = new WebSocketServer({
    httpServer: server
});

console.log("[+] Server started on port: " + port + "...");

wsServer.on("request", function(request) {
    var connection = request.accept(null, request.origin);
    console.log("[+] Connecton from origin: " + request.origin);
    console.log("[+] Connection accepted");

    // Set auth state
    connection.auth = "NOBODY";
    
    connection.on("message", function(message) {
        try {
            handle_message(connection, message);
        }
        catch(err) {
            send_msg(connection, JSON.stringify({"error":"JSON is only supported format"}));
        }
    });
    
    connection.on("close", handle_close);

});


function handle_message(connection, msg) {
    if(msg.type === "utf8") {
        // Handle only text 
        console.log("[+] Received message: " + msg.utf8Data);

        if(connection.auth === "NOBODY") {
            handle_auth(connection, msg);
            return;
        } 

        var json_request = JSON.parse(msg.utf8Data); 
        if ("request" in json_request) {
           switch(json_request.request) {
                case "set":
                    handle_set(connection, json_request);
                    break;
                case "get":
                    handle_get(connection, json_request);
                    break;
                default:
                    send_msg(connection, JSON.stringify({"requests":"set_description, get_description"}));
            } 
        }
        else {
            console.log("[+] Incorrect request sent.");
            send_msg(connection, JSON.stringify({"error":"Send a request"}));
        }
    
    } else {
        console.log("[+] Message is incorrect format: " + msg.type);
        send_msg(connection, JSON.stringify({"error":"JSON is only supported format"}));
    }
}

function handle_set(connection, json_msg) {
    if("property" in json_msg &&
       "value" in json_msg) {
        try {
            var result = eval("connection[\""+ json_msg.property + "\"] = json_msg.value"); 
            send_msg(connection, JSON.stringify({"result": result }));
        }
        catch(err) {
            send_msg(connection, JSON.stringify({"error":err}));
        }
    }
    else {
        send_msg(connection, JSON.stringify({"error":"Specify property and value"}));
    }
}

function handle_get(connection, json_msg) {
    if("property" in json_msg) {
        try {
            var value = eval("connection[json_msg.property]");
            console.log("GET: " + value);
            send_msg(connection, JSON.stringify({"result": value}));
        }
        catch(err) {
            send_msg(connection, JSON.stringify({"error":err}));
        }
    }
    else {
        send_msg(connection, JSON.stringify({"error":"Specify property"}));
    }
}

function handle_auth(connection, msg) {
    // User must be logged in before having access to anything
    var login_req = JSON.parse(msg.utf8Data);

    if("username" in login_req && "password" in login_req) {
        if(login_req.username === "admin" && 
           login_req.password === "admin") {
            send_msg(connection, JSON.stringify({"success":"successfully logged in."}));
            connection.auth = "ADMIN";
            console.log("[+] Successfully authenticated as admin");
            return;
        } 
        else if (login_req.username === "user" &&
                 login_req.password === "user") {
            send_msg(connection, JSON.stringify({"success":"successfully logged in."}));
            connection.auth = "USER";
            console.log("[+] Successfully authentiacted as user");
            return;
        }
        else {
            send_msg(connection, JSON.stringify({"error":"Authentication failed, incorrect username/password."}));
            return;
        }
    } else {
        send_msg(connection, JSON.stringify({"error":"Authentication failed, specify username and password."}));
    }
}

function handle_close(connection) {
    console.log("[+] Closing connection.");
}

function send_msg(connection, msg){
    console.log("[+] Sending msg: " + msg);
    connection.sendUTF(msg);
}
