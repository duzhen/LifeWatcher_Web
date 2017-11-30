document.body.onload = loadFrames;

function loadFrames() {
    addElement ();
    addElement ();
    addElement ();
}

function addElement () {
    // create a new div element
    // var newDiv = document.createElement("div");
    // newDiv.className = 'col-sm-6 col-md-4'
    // var div2 = document.createElement("div");
    // div2.className = "frame-wrapper"
    // newDiv.appendChild(div2)
    // var div3 = document.createElement("div");
    // div3.className = "frame-title"
    // div3.appendChild(document.createTextNode("Title1"))
    // div2.appendChild(div3)

    var div1 = document.createElement("div");
    div1.className = "detector-list"
    var ul1 = document.createElement("ul");
    ul1.className = "list-group"
    div1.appendChild(ul1)

    addLi(ul1);



    // add the newly created element and its content into the DOM
    var currentDiv = document.getElementById("detectors");
    currentDiv.appendChild(div1)
}

function addLi(parent_ul) {
    var li = document.createElement("li");
    li.className = "list-group-item"
    li.appendChild(document.createTextNode("Detector"))
    parent_ul.appendChild(li)
}


function post(path, params, method) {
    method = "post";

    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}