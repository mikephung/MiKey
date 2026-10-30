// Optional: puts the download button for the visitor's system first. Without it both buttons simply show.
(function () {
  var p = ((navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || navigator.userAgent || "").toLowerCase();
  var os = p.indexOf("win") >= 0 ? "win" : p.indexOf("mac") >= 0 ? "mac" : null;
  if (!os) return;
  var buttons = document.querySelectorAll('.cta a[data-os="' + os + '"]');
  for (var i = 0; i < buttons.length; i++) {
    if (buttons[i].getAttribute("href").indexOf("#windows") >= 0) continue;   // not released yet: keep macOS first
    buttons[i].classList.add("first");
    buttons[i].classList.remove("alt");
    var other = buttons[i].parentNode.querySelector('a[data-os]:not([data-os="' + os + '"])');
    if (other) other.classList.add("alt");
  }
})();
