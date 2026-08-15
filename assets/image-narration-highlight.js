(() => {
  const ACTIVE_TTS_CLASS = "tts-active-block";
  const IMAGE_FRAME_CLASS = "adt-image-narration-active";
  let activeMediaId = null;

  function imageIdFromMedia(media) {
    const source = media.currentSrc || media.src || "";
    const filename = decodeURIComponent(source.split("/").pop() || "");
    const stem = filename.replace(/\.mp3(?:\?.*)?$/i, "");
    return stem.includes("_im") ? stem : null;
  }

  function syncImageFrames() {
    const activeIds = new Set(
      Array.from(
        document.querySelectorAll(
          `.adt-image-description.${ACTIVE_TTS_CLASS}[data-id]`,
        ),
      ).map((description) => description.getAttribute("data-id")),
    );
    if (activeMediaId) activeIds.add(activeMediaId);

    document.querySelectorAll("img[data-duplicate-id]").forEach((image) => {
      const isActive = activeIds.has(image.getAttribute("data-duplicate-id"));
      const isVisible = image.getClientRects().length > 0;
      image.classList.toggle(IMAGE_FRAME_CLASS, isActive && isVisible);
    });
  }

  function start() {
    const content = document.getElementById("content");
    if (!content) return;

    syncImageFrames();
    new MutationObserver(syncImageFrames).observe(content, {
      subtree: true,
      attributes: true,
      attributeFilter: ["class"],
    });
    window.addEventListener("resize", syncImageFrames, { passive: true });
  }

  /* The ADT player may use detached Audio objects, so also follow their
     actual playing/ended events instead of relying only on visible TTS text. */
  const nativePlay = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function (...args) {
    if (!this.dataset.adtImageFrameBound) {
      this.dataset.adtImageFrameBound = "true";
      this.addEventListener("playing", () => {
        activeMediaId = imageIdFromMedia(this);
        syncImageFrames();
      });
      const clear = () => {
        if (activeMediaId === imageIdFromMedia(this)) activeMediaId = null;
        syncImageFrames();
      };
      this.addEventListener("pause", clear);
      this.addEventListener("ended", clear);
      this.addEventListener("error", clear);
    }
    return nativePlay.apply(this, args);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
