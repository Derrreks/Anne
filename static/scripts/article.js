"use-strict";
function getSelectedText() {
    var text = "";

    if (window.getSelection) {
        text = window.getSelection().toString();
    } else if (document.selection && document.selection.type != "Control") {
        text = document.selection.createRange().text;
    }
    window.getSelection().removeAllRanges();

    text = text.trim();
    return text;
}

function isAlreadyHighlighted(highlighted) {
    var highlights = getFinalText();
    for (var i = 0; i < highlights.length; i++) {
        if (highlights[i].includes(highlighted)) {
            return true;
        }
    }
    return false;
}

function add() {
    var highlighted = getSelectedText();

    if (isAlreadyHighlighted(highlighted) === true) {
        $("#warning").append("<p>Text has already been selected.</p>")
        return;
    }

    $("#selected").append("<li>" + highlighted + "</li>");
    $("#warning").empty();
}

function getFinalText() {
    var results = [];
    var annotations = $("#selected li");
    annotations.each(function(idx, li) {
        results.push($(li).text());
    });
    return results;
}

function getCheckBoxSelection() {
    var e = document.getElementById("checkbox-list");
    var text = e.options[e.selectedIndex].text;
    return text;
}

function submit() {
    var userid = document.getElementById("userid").innerHTML;
    var id = document.getElementById("id").innerHTML;
    var annotations = getFinalText();
    var selection = getCheckBoxSelection();

    if (annotations.length > 0 || selection == 'Cannot tell based on the abstract') {
        post("/submit/", {"userid": userid, "id": id,
                          "annotations": JSON.stringify(annotations),
                          "selection": selection});
    }

}

function clear() {
    $("#selected").empty();
    $("#warning").empty();
    $("#warning").hide();
}

$("#add-but").click(add);
$("#submit-but").click(submit);
$("#restart-but").click(clear);
