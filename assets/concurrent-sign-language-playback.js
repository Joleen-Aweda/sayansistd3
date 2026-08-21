/* Keep sign-language video and read-aloud narration independent. */
(function () {
  "use strict";

  const nativePause = HTMLMediaElement.prototype.pause;

  function isSignLanguageVideo(media) {
    return (
      media instanceof HTMLVideoElement &&
      media.currentSrc.includes("/content/sign-language/") &&
      media.closest('[class*="fixed"][class*="w-80"]') !== null
    );
  }

  // The reader normally pauses this video when narration takes ownership of
  // playback. Ignore only that programmatic pause; native video controls still
  // let the learner pause and resume the clip directly.
  HTMLMediaElement.prototype.pause = function () {
    if (isSignLanguageVideo(this)) return;
    return nativePause.call(this);
  };

  // The reader also stops narration when the sign-language video emits play.
  // Intercept that coordination event before React receives it. Playback itself
  // has already started and continues normally.
  window.addEventListener(
    "play",
    function (event) {
      if (isSignLanguageVideo(event.target)) event.stopImmediatePropagation();
    },
    true
  );
})();
