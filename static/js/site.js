function getCookie(name) {
  const prefix = name + "=";
  const cookie = document.cookie.split(";").map((item) => item.trim()).find((item) => item.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : "";
}

async function postForm(form) {
  const response = await fetch(form.action, {
    method: "POST",
    body: new FormData(form),
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "X-Requested-With": "XMLHttpRequest",
      "Accept": "application/json"
    },
    credentials: "same-origin"
  });
  const data = await response.json();
  if (!response.ok || !data.ok) throw new Error(data.error || "अभी अनुरोध पूरा नहीं हो सका। दोबारा कोशिश करें।");
  return data;
}

function updateCount(scope, selector, count) {
  if (!scope) return;
  scope.querySelectorAll(selector).forEach((node) => { node.textContent = count; });
}

function appendComment(target, data) {
  const item = document.createElement("div");
  item.className = "comment";
  const avatar = document.createElement("div");
  avatar.className = "comment-avatar";
  avatar.textContent = (data.author || "?").trim().charAt(0).toUpperCase();
  const content = document.createElement("div");
  content.className = "comment-content";
  const author = document.createElement("strong");
  author.textContent = data.author;
  const time = document.createElement("small");
  time.textContent = data.created_at;
  const body = document.createElement("p");
  body.textContent = data.body;
  content.append(author, time, body);
  item.append(avatar, content);
  target.append(item);
}

document.addEventListener("submit", async (event) => {
  const likeForm = event.target.closest(".ajax-like-form");
  const commentForm = event.target.closest(".ajax-comment-form");
  const form = likeForm || commentForm;
  if (!form) return;
  event.preventDefault();
  const button = form.querySelector("button[type=submit], button:not([type])");
  if (button) button.disabled = true;
  const feedback = form.querySelector(".form-feedback");
  if (feedback) feedback.textContent = "";
  try {
    const data = await postForm(form);
    if (likeForm) {
      const card = form.closest("[data-post-card]") || document;
      const likeButton = form.querySelector("[data-like-button]");
      updateCount(form, "[data-like-count]", data.count);
      if (likeButton) {
        likeButton.classList.toggle("liked", data.liked);
        likeButton.setAttribute("aria-pressed", data.liked ? "true" : "false");
      }
    } else {
      const card = form.closest("[data-post-card]") || document.querySelector(".detail-card");
      const inlineTarget = card && card.querySelector("[data-inline-comments]");
      const detailTarget = document.querySelector("[data-comments-list]");
      const target = inlineTarget || detailTarget;
      if (target) {
        const empty = target.querySelector("[data-empty-comments]");
        if (empty) empty.remove();
        appendComment(target, data);
      }
      updateCount(card || document, "[data-comment-count]", data.count);
      form.reset();
      if (feedback) feedback.textContent = "आपकी टिप्पणी प्रकाशित हो गई।";
    }
  } catch (error) {
    const message = error.message || "नेटवर्क समस्या है। कृपया दोबारा कोशिश करें।";
    if (feedback) feedback.textContent = message;
    else {
      let notice = form.querySelector(".ajax-error");
      if (!notice) {
        notice = document.createElement("p");
        notice.className = "ajax-error";
        form.insertAdjacentElement("afterend", notice);
      }
      notice.textContent = message;
    }
  } finally {
    if (button) button.disabled = false;
  }
});

async function recordShare(url) {
  if (!url) return;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken"), "X-Requested-With": "XMLHttpRequest" },
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
