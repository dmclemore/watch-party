const socket = io.connect("http://" + document.domain + ":" + location.port);

let done = false;
let queuedVideos = [];
let player;

// Iframe API code being called

const tag = document.createElement("script");
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName("script")[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

$(() => {
    socket.emit("join", {
        room: $("#roomId").val(),
    });

    socket.on("setCurrentVideo", data => {
        // console.log(`http://www.youtube.com/v/${data.url}?version=3`);
        // if (data.url)
        //     player.cueVideoByUrl(
        //         `http://www.youtube.com/v/${data.url}?version=3`
        //     );
        socket.emit("send_chat", {
            username: "[SYSTEM]",
            message: `${$("#chat-user").val()} has connected.`,
        });
    });

    socket.on("renderMessage", data => {
        if (typeof data.username !== "undefined" && data.message !== "") {
            const newMessage = $(generateChatMessageHTML(data));
            $("#chat-all-messages").append(newMessage);
        }
    });

    socket.on("nextVideo", data => {
        player.cueVideoByUrl(data.url);
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

function handleChatMessage(evt) {
    evt.preventDefault();
    const username = $("#chat-user").val();
    const message = $("#chat-message").val();
    if (message == "" || username == "") return;
    if (message == "!skip") {
        socket.emit("next_video", {
            url: queuedVideos[0].video,
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
    queueVideo(url, username);
    $("#nextVideoForm").trigger("reset");
}

// API FUNCTIONS

function onYouTubeIframeAPIReady(url = "5qap5aO4i9A") {
    player = new YT.Player("player", {
        height: "100%",
        width: "100%",
        videoId: url,
        events: {
            onReady: onPlayerReady,
            onStateChange: onPlayerStateChange,
        },
    });
}

function onPlayerReady(event) {
    // player.loadVideoByUrl("https://www.youtube.com/watch?v=DWcJFNfaw9c");
}

function onPlayerStateChange(event) {
    if (event.data === 0) {
        if (queuedVideos.length === 0) {
            queuedVideos.push({
                video: `http://www.youtube.com/v/5qap5aO4i9A?version=3`,
                user: "[SYSTEM]",
            });
        }
        socket.emit("next_video", {
            url: queuedVideos[0].video,
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
    const url = `http://www.youtube.com/v/${videoId}?version=3`;
    queuedVideos.push({ video: url, user: username });
}
