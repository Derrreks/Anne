"use-strict";
function preventMultiCheck() {
    var box = $(this);
    if (box.is(":checked")) {
        var group = "input:checkbox";
        $(group).prop("checked", false);
        box.prop("checked", true);
    } else {
        box.prop("checked", false);
    }
}

function checkFromLabel() {
    box = $(this).prev('input');
    if(box.is(":checked")) {
        box.prop("checked", false);
    } else {
        var group = "input:checkbox";
        $(group).prop("checked", false);
        box.prop("checked", true);
    }
    document.getElementById("check-warning").style.visibility = "hidden";
}

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
    $("#text").html($("#text").html().replace(
        highlighted,
        "<span style=\"font-weight: bold;\">" + highlighted + "</span>")
    );
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
    var choice = "";
    $("input:checkbox:checked").each(function(){
        choice = $(this).next("label").text();
    });
    return choice;
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

$("input:checkbox").click(preventMultiCheck);
$("label").click(checkFromLabel);
$("#add-but").click(add);
$("#submit-but").click(submit);
$("#restart-but").click(clear);
