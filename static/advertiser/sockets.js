let chatSocket = null;

Date.prototype.today = function () {
    return ((this.getDate() < 10)?"0":"") + this.getDate() +"."+(((this.getMonth()+1) < 10)?"0":"") + (this.getMonth()+1) +"."+ this.getFullYear();
}

Date.prototype.timeNow = function () {
     return ((this.getHours() < 10)?"0":"") + this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}

function connect() {
    chatSocket = new WebSocket("wss://" + window.location.host + "/ws/chat/test/");

    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket.");
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 2s...");
        setTimeout(function() {
            console.log("Reconnecting...");
            connect();
        }, 2000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log(data);

        switch (data.type) {
            case "log_message":
                var newDate = new Date();
                var payload = JSON.parse(data.message)
                document.getElementById('total').innerHTML = payload.total
                document.getElementById('visited').innerHTML = payload.visited
                document.getElementById('success').innerHTML = payload.success
                document.getElementById('skipped').innerHTML = payload.skipped
                var logs = document.getElementById('logs')
                logs.innerHTML += '<span class="log-time">' + newDate.today() + " " + newDate.timeNow() + '</span> ' + payload.message + "<br />";
                logs.scrollTop = logs.scrollHeight;
                break;
            default:
                console.error("Unknown message type!");
                break;
        }
    };

    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}
connect();