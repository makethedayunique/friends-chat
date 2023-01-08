function getCSRFToken() {
	let cookies = document.cookie.split(";")
	for (let i = 0; i < cookies.length; i++) {
		let c = cookies[i].trim()
		if (c.startsWith("csrftoken=")) {
			return c.substring("csrftoken=".length, c.length)
		}
	}
	return "unknown";
}

function sendSearch() {
    // Send the search request and get the result
    let search_input = $("#id_search_input").val();
    $("#id_search_input").val("");
    // Clear the result place
    $("#id_request_search_res").empty();
    // Send the ajax
    $.ajax({
        url: "/search_user",
        type: "POST",
        data: "email=" + search_input + "&csrfmiddlewaretoken=" + getCSRFToken(),
        dataType: "json",
        timeout: 5000,
        success: display_search_res,
        error: display_search_error,
    });
}

function display_search_res(response) {
    // Display the search result
    var result = '<img alt="32x32" class="mr-2 rounded" style="width: 32px; height: 32px;" src="' +
                    response.user_pic + '">' + 
                    '<div class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">' + 
                    '<div class="d-flex justify-content-between align-items-center w-100">' + 
                    '<div><strong class="text-gray-dark">' + response.user_name + '</strong>' + 
                    '<span class="d-block">' + response.user_desc + '</span>' + 
                    '</div>';
    if (response.disable) {
        result += '<button type="button" class="btn btn-success" disabled>Add</button></div></div>';
    } else {
        result = result +
            '<button type="button" class="btn btn-success" onclick="send_add(this,' + response.user_id +
            ')">Add</button></div></div>';
    }    
    $("#id_request_search_res").append(result);
}

function display_search_error(error) {
    // Display the search error
    var result = '<div class="alert alert-warning alert-dismissible" role="alert">';
    if (error == undefined || error.responseJSON == undefined) {
        result += "There is something going wrong!";
    } else if ("message" in error.responseJSON) {
        result += error.responseJSON.message;
    } else {
        result += "There is something going wrong!";
    }            
    result = result + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span></button>' + 
                '</div>';
    $("#id_request_search_res").append(result);
}

function send_add(obj, user_id="NONE") {
    // Send the request to add user
    $.ajax({
        url: "/send_adding_friend",
        type: "POST",
        data: "user_id=" + user_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
        dataType: "json",
        timeout: 5000,
        success: function(data, status, xhr) {
            $(obj).attr("disabled", "disabled");
            show_modal_success(data, "Successfully sent friend request!");
        },
        error: show_modal_fail,
    });
}

function accept_friend(obj, user_id="NONE") {
    // Accept the user request
    $.ajax({
        url: "/accept_friend",
        type: "POST",
        data: "user_id=" + user_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
        dataType: "json",
        timeout: 5000,
        success: function(data, status, xhr) {
            $(obj).attr("disabled", "disabled");
            show_modal_success(data, "Accept the request!");
        },
        error: show_modal_fail,
    })
}

function show_modal_success(res, message) {
    $("#requestResModalLabel").text(message);
    $("#requestResModal").modal();
}

function show_modal_fail(error) {
    if (error == undefined || error.responseJSON == undefined) {
        $("#requestResModalLabel").text("There is something going wrong!");
    } else if ("message" in error.responseJSON) {
        $("#requestResModalLabel").text(error.responseJSON.message);
    } else {
        $("#requestResModalLabel").text("There is something going wrong!");
    }
    $("#requestResModal").modal();  
}
