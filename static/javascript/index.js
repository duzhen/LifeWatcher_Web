document.body.onload = loadFrames;

function loadFrames() {
    addElement ();
    addElement ();
    addElement ();
}

function loadDetector(parent) {
    // addElement ();

    var client = new sendRequest();
    client.get('http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/rest/api/detector', function(response) {
        var detData = JSON.parse(response).detectors;
        for (index in detData){
            de = detData[index];
            expand_menu(de, parent)
        }
    });
}

function loadFrames() {
    // addElement ();

    var client = new sendRequest();
    client.get('http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/rest/api/camera', function(response) {
        var camera = JSON.parse(response);
        for (index in camera){
            id = camera[index];
            addElement (id);
        }
    });
}

function addElement (id) {
    // create a new div element
    var newDiv = document.createElement("div");
    newDiv.className = 'col-sm-6 col-md-4'
    var div2 = document.createElement("div");
    div2.className = "frame-wrapper"
    newDiv.appendChild(div2)
    var div3 = document.createElement("div");
    div3.className = "frame-title"
    div3.appendChild(document.createTextNode(id))
    div2.appendChild(div3)
    var div4 = document.createElement("div");
    div4.className = "frame-stage"
    div2.appendChild(div4)
    var div5 = document.createElement("div");
    div5.className = "embed-responsive embed-responsive-16by9"
    div4.appendChild(div5)
    var iframe1 = document.createElement("img");
    iframe1.className = "embed-responsive-item"
    iframe1.src = "http://ec2-18-216-37-90.us-east-2.compute.amazonaws.com/static/schoolbus.jpg"
    div5.appendChild(iframe1)
    var div6 = document.createElement("div");
    div6.className = "switch-toggle"
    div2.appendChild(div6)
    var div7 = document.createElement("div");
    div7.className = "frame-notes"
    div7.appendChild(document.createTextNode("Description"))
    div2.appendChild(div7)

    loadDetector(div7)


    // add the newly created element and its content into the DOM
    var currentDiv = document.getElementById("cameras");
    currentDiv.appendChild(newDiv)
}

function expand_menu(de, div_parent){
    //dropdown menu
    var cont1 = document.createElement("div");
    cont1.className = "dropdown"
    div_parent.appendChild(cont1)
    var button1 = document.createElement("button");
    button1.className = "btn btn-secondary dropdown-toggle"
    button1.setAttribute('type', 'button')
    button1.setAttribute('id','dropdownMenuButton')
    button1.setAttribute('data-toggle', 'dropdown')
    button1.setAttribute('aria-haspopup', 'true')
    button1.setAttribute('aria-expanded', 'false')
    button1.appendChild(document.createTextNode("DetectorList"))
    cont1.appendChild(button1)
    var cont2 = document.createElement("div");
    cont2.className = "dropdown-menu"
    cont2.setAttribute('aria-labelledby', 'dropdownMenuButton')
    cont1.appendChild(cont2)
    var but_func = document.createElement("a");
    but_func.className = "dropdown-item"
    but_func.setAttribute('href', '#')
    but_func.setAttribute('type', 'button')
    but_func.setAttribute('onclick', 'Function()')
    but_func.setAttribute('return', 'false')
    but_func.appendChild(document.createTextNode(de.name))
    cont2.appendChild(but_func)

}

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