"use strict";

/**
* Start the script, and display an abstract.
*/
function start() {
    var id_ = document.getElementById("id-field").value;
    if (id_) {
      post("/start/", {"userid": id_});
    }
}

$("#start-but").click(start);
