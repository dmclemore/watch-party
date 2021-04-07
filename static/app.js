const socket = io.connect("http://" + document.domain + ":" + location.port)

$(() => {
    // Main

    // socket.on("connection", () => {
    //     socket.emit("user_connected", {data: "I'm connected!"})
    // })

    socket.on("renderMessage", (data) => {
        // SOCKET DEBUG
        // console.log(data)
        if (typeof data.username !== "undefined" && data.message !== "") {
            const newMessage = $(generateChatMessageHTML(data))
            $("#chat-all-messages").append(newMessage)
        }
    })

    $("#chat-form").on("submit", handleChatMessage)
    $("#chat-submit").on("click", handleChatMessage)
})

async function handleChatMessage(evt){

    evt.preventDefault()
    const username = $("#chat-user").val()
    const message = $("#chat-message").val()
    if (message == "" || username == ""){
        return
    }
    socket.emit("send_chat", {
        username: username,
        message: message
    })
    $("#chat-all-messages").scrollTop($("#chat-all-messages").height())
    $("#chat-form").trigger("reset")
}

function generateChatMessageHTML(message){
    return `
        <p>
            <span class="font-weight-bold text-primary">${message.username}: </span>${message.message}
        </p>
    `
}

