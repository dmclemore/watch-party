const socket = io.connect("https://" + document.domain + ":" + location.port);
let queuedVideos = [];
let player;
let roomId = $("#roomId").val();

// Iframe API Initialization

const tag = document.createElement("script");
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(() => {
    socket.emit("join", {
        room: roomId,
    });

    // Client-side socket event listeners

    socket.on("renderMessage", data => {
        if (typeof data.username !== "undefined" && data.message !== "") {
            const newMessage = $(generateChatMessageHTML(data));
            $("#chat-all-messages").append(newMessage);
        }
    });

    socket.on("nextVideo", data => {
        let url = `http://www.youtube.com/v/${data.id}?version=3`;
        player.cueVideoByUrl(url);
        $("#videoUser").text(data.user);
    });

    socket.on("playVideo", () => {
        player.playVideo();
    });

    socket.on("stopVideo", () => {
        player.pauseVideo();
    });

    socket.on("syncVideo", data => {
        player.pauseVideo();
        player.seekTo(data.time, true);
        player.playVideo();
    });

    // DOM event listeners

    $("#chat-form").on("submit", handleChatMessage);
    $("#chat-submit").on("click", handleChatMessage);

    $("#nextVideoForm").on("submit", handleVideoSubmit);
    $("#nextVideoSubmit").on("click", handleVideoSubmit);
});

// API FUNCTIONS

async function onYouTubeIframeAPIReady() {
    // Get the rooms current video from the database, and initialize the video player

    let response = await axios.get(`/api/${roomId}/current`);
    player = new YT.Player("player", {
        height: "100%",
        width: "100%",
        videoId: response.data.current_video,
        events: {
            onStateChange: onPlayerStateChange,
        },
    });
}

async function onPlayerStateChange(event) {
    // Handle what to do when the video player has a state change

    // State Change: Video Ended
    if (event.data === 0) {
        if (queuedVideos.length === 0) {
            queuedVideos.push({
                videoId: "5qap5aO4i9A",
                user: "[SYSTEM]",
            });
        }
        socket.emit("next_video", {
            id: queuedVideos[0].videoId,
            user: queuedVideos[0].user,
        });
        queuedVideos.shift();
    }
    // State Change: Video Played
    if (event.data === 1) socket.emit("play_video");
    // State Change: Video Paused
    if (event.data === 2) socket.emit("stop_video");
    // State Change: Video Buffering
    if (event.data === 3) {
        socket.emit("sync_video", {
            time: player.getCurrentTime(),
        });
    }
}

// HANDLERS

async function handleChatMessage(evt) {
    // When a chat message is sent, display it in the chat. If the message contains a command, execute the command.

    evt.preventDefault();
    const username = $("#chat-user").val();
    const message = $("#chat-message").val();
    if (message == "" || username == "") return;
    socket.emit("send_chat", {
        username: username,
        message: message,
    });
    // Skip Command
    if (message == "!skip") {
        socket.emit("next_video", {
            id: queuedVideos[0].videoId,
            user: queuedVideos[0].user,
        });
        queuedVideos.shift();
    }
    // Play Command
    if (message == "!play") socket.emit("play_video");
    // Stop Command
    if (message == "!stop") socket.emit("stop_video");
    // Sync Command
    if (message == "!sync") {
        socket.emit("sync_video", {
            time: player.getCurrentTime(),
        });
    }
    // Help Command
    if (message == "!help") {
        socket.emit("send_chat", {
            username: "[SYSTEM]",
            message: `Chat Commands:<br>
            "!play": Play the video.<br>
            "!stop": Stop the video.<br>
            "!skip": Skip to the next video in queue.<br>
            "!sync": Sync all chatters videos' to your timestamp.`,
        });
    }
    $("#chat-all-messages").scrollTop($("#chat-all-messages").height());
    $("#chat-form").trigger("reset");
}

function handleVideoSubmit(evt) {
    // When a video is submitted for queue, add it to the queue and let the chat know

    evt.preventDefault();
    username = $("#nextVideoUser").val();
    url = $("#nextVideo").val();
    socket.emit("send_chat", {
        username: "[SYSTEM]",
        message: `${username} queued a video!`,
    });
    queueVideo(url, username);
    $("#nextVideoForm").trigger("reset");
}

// HELPERS

function generateChatMessageHTML(message) {
    // Return the HTML to display a chat message

    return `
        <p>
            <span class="font-weight-bold text-danger">${message.username}: </span>${message.message}
        </p>
    `;
}

function queueVideo(input, username) {
    // Grab the video ID from the URL, and add it to queue

    const videoId = input.split("=")[1];
    queuedVideos.push({ videoId: videoId, user: username });
}
