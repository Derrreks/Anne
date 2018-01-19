/**
* Start the script, and display an abstract.
*/
function start() {
    var id_ = document.getElementById("textfield").value;
    if (id_ === undefined || id_ === '') {
      return ;
    } else {
      post("/start/", {"userid": id_})
    }

}

// When you click the start button, call the "start" function.
$("#start-but").click(start);
