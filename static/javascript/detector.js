document.body.onload = loadFrames;

function loadFrames() {
    // addElement ();

    var client = new sendRequest();
    client.get('http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/rest/api/detector', function(response) {
        var detData = JSON.parse(response).detectors;
        for (i in detData){
            de = JSON.parse(i);
            addElement (de.id, de.name);
        }
    });
}

function addElement (inputId, inputName) {
    var div1 = document.createElement("div");
    div1.className = "detector-list"
    var ul1 = document.createElement("ul");
    ul1.className = "list-group"
    div1.appendChild(ul1)

    addLi(ul1, inputId, inputName);

    var currentDiv = document.getElementById("detectors");
    currentDiv.appendChild(div1)
}

function addLi(parent_ul, inputId, inputName) {
    var li = document.createElement("li");
    li.className = "list-group-item"
    li.appendChild(document.createTextNode("ID:" + inputId + "-" + "Name:" + inputName));
    parent_ul.appendChild(li)
}


// function post(path, params, method) {
//     method = "post";
//
//     var form = document.createElement("form");
//     form.setAttribute("method", method);
//     form.setAttribute("action", path);
//
//     for(var key in params) {
//         if(params.hasOwnProperty(key)) {
//             var hiddenField = document.createElement("input");
//             hiddenField.setAttribute("type", "hidden");
//             hiddenField.setAttribute("name", key);
//             hiddenField.setAttribute("value", params[key]);
//
//             form.appendChild(hiddenField);
//         }
//     }
//
//     document.body.appendChild(form);
//     form.submit();
// }

//https://stackoverflow.com/questions/247483/http-get-request-in-javascript
var sendRequest = function() {
    this.get = function(path, callback) {
        var requestClient = new XMLHttpRequest();
        requestClient.onreadystatechange = function() {
            if (requestClient.readyState == 4 && requestClient.status == 200)
                callback(requestClient.responseText);
        }

        requestClient.open( "GET", path, true );
        requestClient.send( null );
    }
}