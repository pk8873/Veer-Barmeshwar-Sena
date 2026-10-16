document.addEventListener("click", async (event) => {
  const button = event.target.closest(".share-button");
  if (!button) return;
  const url = button.dataset.shareUrl || window.location.href;
  try {
    if (navigator.share) await navigator.share({ title: document.title, url });
    else if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(url);
      const label = button.querySelector("span");
      if (label) { const old = label.textContent; label.textContent = "Copied!"; setTimeout(() => label.textContent = old, 1500); }
    } else window.prompt("Copy this link:", url);
  } catch (error) { if (error.name !== "AbortError") window.prompt("Copy this link:", url); }
});
