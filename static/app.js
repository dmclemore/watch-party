const API_KEY = "AIzaSyC41i0e4xqeXcovjteNG1_l6u_i_FPRu-Q";
// const socket = io.connect("http://" + document.domain + ":" + location.port);
const roomId = $("#roomId").val();
const socket = io.connect(
    f`http://capstone-watch-party.herokuapp.com/room/${roomId}`
);

$(() => {
    // Main

    socket.on("renderMessage", data => {
        if (typeof data.username !== "undefined" && data.message !== "") {
            const newMessage = $(generateChatMessageHTML(data));
            $("#chat-all-messages").append(newMessage);
        }
    });

    $("#chat-form").on("submit", handleChatMessage);
    $("#chat-submit").on("click", handleChatMessage);

    $("#nextVideoForm").on("submit", handleVideoSubmit);
    $("#nextVideoSubmit").on("click", handleVideoSubmit);
});

async function handleChatMessage(evt) {
    evt.preventDefault();
    const username = $("#chat-user").val();
    const message = $("#chat-message").val();
    if (message == "" || username == "") {
        return;
    }
    socket.emit("send_chat", {
        username: username,
        message: message,
    });
    $("#chat-all-messages").scrollTop($("#chat-all-messages").height());
    $("#chat-form").trigger("reset");
}

function generateChatMessageHTML(message) {
    return `
        <p>
            <span class="font-weight-bold text-danger">${message.username}: </span>${message.message}
        </p>
    `;
}

function handleVideoSubmit(evt) {
    evt.preventDefault();
    username = $("#nextVideoUser").val();
    url = $("#nextVideo").val();
    socket.emit("send_chat", {
        username: "[SYSTEM]",
        message: `${username} queued a video!`,
    });
    $("#nextVideoForm").trigger("reset");
}
