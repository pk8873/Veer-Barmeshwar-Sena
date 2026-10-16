function getCookie(name) {
  const prefix = name + "=";
  const cookie = document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
}

async function recordShare(url) {
  if (!url) return;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      credentials: "same-origin",
      mode: "same-origin"
    });
  } catch (error) {
    // Sharing should still work if activity logging is temporarily unavailable.
  }
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".share-button");
  if (!button) return;
  const url = button.dataset.shareUrl || window.location.href;
  const logUrl = button.dataset.shareLogUrl;
  try {
    if (navigator.share) {
      await navigator.share({ title: document.title, url });
      await recordShare(logUrl);
    } else if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(url);
      await recordShare(logUrl);
      const label = button.querySelector("span");
      if (label) {
        const old = label.textContent;
        label.textContent = "लिंक कॉपी हो गया";
        setTimeout(() => label.textContent = old, 1800);
      }
    } else {
      const copied = window.prompt("इस लिंक को कॉपी करें:", url);
      if (copied !== null) await recordShare(logUrl);
    }
  } catch (error) {
    if (error.name !== "AbortError") window.prompt("इस लिंक को कॉपी करें:", url);
  }
});
