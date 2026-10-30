/* 长歌 · 归档页 — 图鉴筛选 */
(function () {
  "use strict";
  var root = document.getElementById("archive");
  if (!root) return;

  var items = Array.prototype.slice.call(root.querySelectorAll(".card-item"));
  var blocks = Array.prototype.slice.call(root.querySelectorAll(".cluster-block"));
  var countEl = document.getElementById("fcount");
  var emptyEl = document.getElementById("fempty");
  var input = document.getElementById("q");
  var state = { fac: "", q: "", cat: "", text: "" };

  function match(el) {
    var d = el.dataset;
    if (state.fac && d.fac !== state.fac && d.fac !== "通用") return false;
    if (state.q && d.q !== state.q) return false;
    if (state.cat && d.cat !== state.cat) return false;
    if (state.text && (d.search || "").indexOf(state.text) < 0) return false;
    return true;
  }

  function apply() {
    var shown = 0;
    items.forEach(function (el) {
      var ok = match(el);
      el.classList.toggle("hidden", !ok);
      if (ok) shown++;
    });
    blocks.forEach(function (b) {
      var vis = b.querySelectorAll(".card-item:not(.hidden)").length;
      b.classList.toggle("hidden", vis === 0);
      var c = b.querySelector(".cnt");
      if (c) c.textContent = vis + " / " + b.querySelectorAll(".card-item").length;
    });
    if (countEl) countEl.textContent = "显示 " + shown + " / " + items.length + " 张";
    if (emptyEl) emptyEl.classList.toggle("hidden", shown !== 0);
  }

  root.querySelectorAll(".fchips").forEach(function (grp) {
    var group = grp.dataset.group;
    grp.querySelectorAll(".fchip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        grp.querySelectorAll(".fchip").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        state[group] = btn.dataset.val || "";
        apply();
      });
    });
  });

  if (input) {
    input.addEventListener("input", function () {
      state.text = input.value.trim().toLowerCase();
      apply();
    });
  }

  // 阵营芯片上标注「含通用」
  root.querySelectorAll('.fchips[data-group="fac"] .fchip[data-val]:not([data-val=""])').forEach(function (b) {
    if (b.dataset.val !== "通用") b.title = b.dataset.val + "（同时显示通用牌）";
  });

  apply();
})();
