document.body.onload = loadFrames;

function loadFrames() {
    addElement ();
    addElement ();
    addElement ();
}

function addElement () {
    // create a new div element
    var newDiv = document.createElement("div");
    newDiv.className = 'col-sm-6 col-md-4'
    var div2 = document.createElement("div");
    div2.className = "frame-wrapper"
    newDiv.appendChild(div2)
    var div3 = document.createElement("div");
    div3.className = "frame-title"
    div3.appendChild(document.createTextNode("Title1"))
    div2.appendChild(div3)
    var div4 = document.createElement("div");
    div4.className = "frame-stage"
    div2.appendChild(div4)
    var div5 = document.createElement("div");
    div5.className = "embed-responsive embed-responsive-16by9"
    div4.appendChild(div5)
    var iframe1 = document.createElement("iframe");
    iframe1.className = "embed-responsive-item"
    iframe1.src = "https://www.youtube.com/embed/H0q7C-8oeIw"
    div5.appendChild(iframe1)
    var div6 = document.createElement("div");
    div6.className = "switch-toggle"
    div2.appendChild(div6)
    var div7 = document.createElement("div");
    div7.className = "frame-notes"
    div7.appendChild(document.createTextNode("Description"))
    div2.appendChild(div7)



    expand_menu(div7)



    // add the newly created element and its content into the DOM
    var currentDiv = document.getElementById("detectors");
    currentDiv.appendChild(newDiv)
}

function expand_menu(div_parent){
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
    but_func.appendChild(document.createTextNode("Detector1"))
    cont2.appendChild(but_func)

}
