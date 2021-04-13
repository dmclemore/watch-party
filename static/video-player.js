// 2. This code loads the IFrame Player API code asynchronously.
const tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
let player;
let done = false;

function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
    height: '100%',
    width: '100%',
    events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
    }
    })
}

function onPlayerReady(event) {
    // $()
}


function onPlayerStateChange(event) {
    if (event.data == YT.PlayerState.PLAYING && !done) {
    setTimeout(stopVideo, 6000)
    done = true
    }
}

function stopVideo() {
    player.stopVideo()
}

// event.target.playVideo()