const socket = io.connect("http://" + document.domain + ":" + location.port);

let done = false;
let queuedVideos = [];
let player;
let roomId = $("#roomId").val();

// Iframe API code being called

const tag = document.createElement("script");
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(() => {
    socket.emit("join", {
        room: roomId,
    });

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

    $("#chat-form").on("submit", handleChatMessage);
    $("#chat-submit").on("click", handleChatMessage);

    $("#nextVideoForm").on("submit", handleVideoSubmit);
    $("#nextVideoSubmit").on("click", handleVideoSubmit);
});

async function handleChatMessage(evt) {
    evt.preventDefault();
    const username = $("#chat-user").val();
    const message = $("#chat-message").val();
    if (message == "" || username == "") return;
    socket.emit("send_chat", {
        username: username,
        message: message,
    });
    if (message == "!skip") {
        socket.emit("next_video", {
            id: queuedVideos[0].videoId,
            user: queuedVideos[0].user,
        });
        queuedVideos.shift();
    }
    if (message == "!play") socket.emit("play_video");
    if (message == "!stop") socket.emit("stop_video");
    if (message == "!sync") {
        socket.emit("sync_video", {
            time: player.getCurrentTime(),
        });
    }
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
    $("#chat-all-messages").scrollTop(
        $("#chat-all-messages").prop("scrollHeight")
    );
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
    queueVideo(url, username);
    $("#nextVideoForm").trigger("reset");
}

// API FUNCTIONS

async function onYouTubeIframeAPIReady() {
    let response = await axios.get(`/api/${roomId}/current`);
    player = new YT.Player("player", {
        height: "100%",
        width: "100%",
        videoId: response.data.current_video,
        events: {
            onReady: onPlayerReady,
            onStateChange: onPlayerStateChange,
        },
    });
}

function onPlayerReady(event) {
    // player.loadVideoByUrl("https://www.youtube.com/watch?v=DWcJFNfaw9c");
}

async function onPlayerStateChange(event) {
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

    if (event.data === 1) socket.emit("play_video");
    if (event.data === 2) socket.emit("stop_video");
    if (event.data === 3) {
        socket.emit("sync_video", {
            time: player.getCurrentTime(),
        });
    }
}

function stopVideo() {
    player.stopVideo();
}

function queueVideo(input, username) {
    const videoId = input.split("=")[1];
    queuedVideos.push({ videoId: videoId, user: username });
}
