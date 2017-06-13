/* global YT, window */

// Returns an instance of the YT API.
export async function getYT() {
  if (YT && YT.Player) {
    return YT;
  } else {
    await afterYouTubeIframeAPIReady();
    return YT;
  }
}

function afterYouTubeIframeAPIReady() {
  return new Promise((resolve, reject) => {
    window.onYouTubeIframeAPIReady = function() {
      resolve();
      window.onYouTubeIframeAPIReady = undefined;
    };
  });
}

