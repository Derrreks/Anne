"use strict";

/**
* Get the text that was highlighted by the user.
*/
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

/**
* Check that the string is already highlighted.
*
* @param highlighted represents that the user wants to add to the highlighted list.
*/
function isAlreadyHighlighted(highlighted) {
    var highlights = getFinalText();
    for (var i = 0; i < highlights.length; i++) {
        if (highlights[i].includes(highlighted)) {
            return true;
        }
    }
    return false;
}

/**
* Add the text to the ongoing list.
*/
function add() {
    var highlighted = getSelectedText();

    if (isAlreadyHighlighted(highlighted) === true) {
        $("#warning").append("<p>Text has already been selected.</p>")
        return;
    }

    $("#selected").append("<li>" + highlighted + "</li>");
    $("#warning").empty();
}

/**
* Returns an array of all the text that has been highlighted by the user.
*/
function getFinalText() {
    var results = [];
    var annotations = $("#selected li");
    annotations.each(function(idx, li) {
        results.push($(li).text());
    });
    return results;
}

/**
* Returns the text of what the user selected from the drop-down menu.
*/
function getCheckBoxSelection() {
    var checkbox = document.getElementById("checkbox-list");
    return checkbox.options[checkbox.selectedIndex].text;
}

/**
* Send the data to the python code.
*/
function submit() {
    var userid = document.getElementById("userid").innerHTML;
    var id = document.getElementById("id").innerHTML;
    var annotations = getFinalText();
    var selection = getCheckBoxSelection();
    var article_path = document.getElementById("article_path").innerHTML;

    if (annotations.length > 0 || selection == 'Cannot tell based on the abstract') {
        post("/submit/", {"userid": userid, "id": id,
                          "annotations": JSON.stringify(annotations),
                          "selection": selection,
                          "article_path": article_path});
    }
}

/**
* Clear all input.
*/
function clear() {
    $("#selected").empty();
    $("#warning").empty();
    $("#warning").hide();
}

$("#add-but").click(add);
$("#submit-but").click(submit);
$("#restart-but").click(clear);
