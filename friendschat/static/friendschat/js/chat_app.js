window.onload = function() {
    $('#chat_rooms .chat_room').eq(0).show();
    if ($('#chat_rooms .chat_room').length > 1) {
        $("#plist ul li").eq(0).addClass("active");
        // Need to scroll to the height of the ul
        $('.chat-history').eq(0).scrollTop($('ul[id^=id_chat_ul_]').eq(0).height());
    }
};

$(function(){
    $("span[id^=id_chat_button_with_]").click(function(){
        // Send message button clicked
        let inputbox_group = $("span[id^=id_chat_button_with_]");
        let inputbox = $("input[id^=id_chat_inputbox_with_]").eq(inputbox_group.index($(this)));
        if (inputbox.val() == '') {
            return;
        }
        const message = inputbox.val();
        inputbox.val(""); // Clear the send box
        chatSocket.send(JSON.stringify({
            "friend_box": inputbox.attr("id"),
            "message": message
        }));
    });

    $('#plist ul li').click(function(){  
        $('#chat_rooms > .chat_room').hide();
        $('#chat_rooms > .chat_room').eq($(this).index()).show();
        $('#plist > ul > li').removeClass("active");
        $(this).addClass("active");
        $(this).find(".badge").remove(); // Remove the badge
        // Show the last
        $('.chat-history').eq($(this).index()).scrollTop($('ul[id^=id_chat_ul_]').eq($(this).index()).height());
     });
});

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/onetoonechat'
);

chatSocket.onmessage = function(e) {
    const received_data = JSON.parse(e.data);
    if (received_data.msg_type == 0) {
        // This is the message sent
        let new_message =
            '<li class="clearfix" id="id_message_' + received_data.msg_id + '">';
        if (received_data.msg_from_self) {
            new_message = new_message + '<div class="message-data text-right">';
        } else {
            new_message = new_message + '<div class="message-data">';
        }
        let sent_date = new Date(received_data.msg_datetime);
        let display_date = sent_date.toLocaleDateString() + " " + 
                        sent_date.toLocaleTimeString().split(":")[0] + ":" + 
                        sent_date.toLocaleTimeString().split(":")[1] + " " + 
                        sent_date.toLocaleTimeString().slice(-2);
        new_message = new_message + '<span class="message-data-time">' + 
                    display_date + '</span>' +
                    '<img src="';
        if (received_data.msg_from_self) {
            new_message = new_message + $(".my-profile img").eq(0).attr("src"); 
        } else {
            new_message = new_message + $("#id_friend_img_" + received_data.msg_user).attr("src"); 
        }
        new_message = new_message + '" alt="avatar"></div>';
        if (received_data.msg_from_self) {
            new_message = new_message + '<div class="message other-message float-right"> ';
        } else {
            new_message = new_message + '<div class="message my-message"> ';
        }
        new_message = new_message + received_data.msg + ' </div></li>';
        $("#id_chat_ul_" + received_data.msg_user).append(new_message);
        // Check whether this tab is clicked
        if ($("#id_friend_tab_" + received_data.msg_user).hasClass("active")) {
            // Scroll the chat history to the bottom
            let id_chat_history = "#id_chat_history_with_" + received_data.msg_user;
            $(id_chat_history).scrollTop($("#id_chat_ul_" + received_data.msg_user).height());
        } else if ($("#id_friend_tab_" + received_data.msg_user).find(".badge").length) {
            // The badge has alreay been there
        } else {
            // Add the badge
            $("#id_friend_tab_" + received_data.msg_user).append('<span class="badge badge-danger float-right">New</span>')
        }

    }
}

window.addEventListener("unload", function() {
    if (chatSocket.readyState == WebSocket.OPEN) {
        chatSocket.close();
    }
});


function show_people_list() {
    $("#plist").animate({left: "0px"}, 500);
}

function hide_people_list() {
    $("#plist").animate({left: "-400px"}, 500);
}

$(window).on("resize", function(){
    // Function to put the people list to the right position
    if ($(window).width() > 767) {
        $(".people-list").css("left", 0);
    }
})
