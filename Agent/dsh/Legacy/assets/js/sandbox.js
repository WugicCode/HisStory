/* 长歌 · 归档页 — 构筑沙盘 */
(function () {
  "use strict";
  var mount = document.getElementById("sandbox");
  if (!mount || !window.CARDS) return;
  // 【域外】与【觉醒】不可构筑：不出现在池子里，也不接受加入
  var CARDS = window.CARDS.filter(function (c) { return c.q !== "域外" && c.cat !== "觉醒"; });
  var byId = {};
  CARDS.forEach(function (c) { byId[c.id] = c; });

  var KEY = "hisstory.deck.v1";
  var deck = {};
  try { deck = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { deck = {}; }

  var pool = document.getElementById("pool");
  var deckList = document.getElementById("deckList");
  var deckCount = document.getElementById("deckCount");
  var track = document.getElementById("deckTrack");
  var issuesEl = document.getElementById("issues");
  var curveEl = document.getElementById("curve");
  var facState = document.getElementById("facState");
  var searchEl = document.getElementById("sbq");

  var filter = { fac: "", q: "", text: "" };
  var LAB = { "N": "普通", "R": "稀有", "E": "史诗", "L": "传说", "域外": "域外", "—": "天赋" };
  var QKEY = { "N": "N", "R": "R", "E": "E", "L": "L", "域外": "O", "—": "T" };

  function lim(c) { var n = parseInt(c.lim, 10); return isNaN(n) ? 99 : n; }
  function cost(c) { var n = parseInt(c.cost, 10); return isNaN(n) ? 0 : n; }
  function total() { var n = 0; for (var k in deck) n += deck[k]; return n; }
  function facSet() {
    var s = {};
    for (var k in deck) { if (deck[k] > 0 && byId[k] && byId[k].fac !== "通用") s[byId[k].fac] = 1; }
    return Object.keys(s);
  }

  /* ---------- 池 ---------- */
  function face(c, cls) {
    var qk = QKEY[c.q] || "N";
    var art = "assets/img/cards/" + c.id + ".svg";
    return '<div class="cface ' + (cls || "") + '" data-q="' + qk + '" style="pointer-events:none">' +
      '<div class="cface-cost">' + (c.cost || "—") + "</div>" +
      '<div class="cface-q">' + (LAB[c.q] || "") + "</div>" +
      '<div class="cface-art"><img src="' + art + '" alt="" loading="lazy"></div>' +
      '<div class="cface-body">' +
        '<div class="cface-name">' + c.name + "</div>" +
        '<div class="cface-type">' + c.cat + " · " + (c.utype || c.fac) + "</div>" +
        (c.stats && c.stats !== "-" ? '<div class="cface-stats">' + c.stats + "</div>" : "") +
      "</div></div>";
  }

  function renderPool() {
    var html = "";
    CARDS.forEach(function (c) {
      var ok = (!filter.fac || c.fac === filter.fac || c.fac === "通用" || filter.fac === "通用" && c.fac === "通用") &&
               (!filter.q || c.q === filter.q) &&
               (!filter.text || (c.name + c.text + (c.tags || []).join("")).toLowerCase().indexOf(filter.text) >= 0);
      if (!ok) return;
      html += '<div class="sb-cell" data-id="' + c.id + '" data-n="' + (c.name) + '">' +
        face(c) + '<button class="add" type="button" data-add="' + c.id + '">加入卡组</button></div>';
    });
    pool.innerHTML = html || '<p class="tiny dim">没有符合条件的卡牌。</p>';
  }

  /* ---------- 校验 ---------- */
  function check() {
    var out = [], n = total(), fs = facSet();
    if (n === 0) {
      out.push({ t: true, m: "从左侧点选卡牌，开始构筑一副 40 张的卡组" });
      return out;
    }
    out.push({ t: n === 40, m: n > 40 ? "超出上限：" + n + " / 40 张" : "数量：" + n + " / 40 张" });
    if (fs.length > 1) out.push({ t: false, m: "跨阵营：" + fs.join(" / ") + " 不可混编" });
    else if (fs.length === 1) out.push({ t: true, m: "阵营：" + fs[0] + "（含通用）" });
    var tal = {};
    for (var k in deck) {
      if (!deck[k]) continue;
      var c = byId[k];
      if (c && c.cat === "天赋" && c.hero) tal[c.hero] = (tal[c.hero] || 0) + 1;
    }
    Object.keys(tal).forEach(function (h) {
      if (tal[h] > 1) out.push({ t: false, m: "天赋重复：同一英雄只能带一张天赋" });
    });
    return out;
  }

  function renderDeck() {
    var n = total();
    deckCount.textContent = n;
    track.style.width = Math.min(100, (n / 40) * 100) + "%";
    track.className = "sb-track" + (n > 40 ? " bad" : "");
    var fs = facSet();
    facState.textContent = "阵营：" + (fs.length ? fs.join(" + ") + "（含通用）" : "未选定");

    // 费用曲线
    if (n === 0) {
      curveEl.style.height = "auto";
      curveEl.innerHTML = '<p class="tiny dim" style="margin:0;padding:2px 0 4px">还没有卡牌。费用曲线会随选择实时生成。</p>';
    } else {
      curveEl.style.height = "";
      var buckets = new Array(13).fill(0);
      for (var k in deck) {
        if (!deck[k]) continue;
        var p = Math.min(12, Math.max(0, cost(byId[k])));
        buckets[p] += deck[k];
      }
      var max = Math.max.apply(null, buckets) || 1;
      curveEl.innerHTML = buckets.map(function (v, i) {
        return '<i data-c="' + i + '" style="height:' + Math.max(2, (v / max) * 100) + '%" title="' + i + " 费 · " + v + " 张\"></i>";
      }).join("");
    }

    // 列表
    var rows = Object.keys(deck).filter(function (k) { return deck[k] > 0; })
      .sort(function (a, b) { return cost(byId[a]) - cost(byId[b]) || byId[a].name.localeCompare(byId[b].name, "zh"); })
      .map(function (k) {
        var c = byId[k];
        return '<div class="sb-row"><span class="c">' + (c.cost || "—") + '</span>' +
          '<a class="n" href="cards/' + k + '.html">' + c.name + "</a>" +
          '<span class="c">×' + deck[k] + "</span>" +
          '<button class="x" data-del="' + k + '" type="button" aria-label="移除">×</button></div>';
      });
    deckList.innerHTML = rows.length ? rows.join("") : '<p class="tiny dim">尚未选择任何卡牌。</p>';

    // 校验
    issuesEl.innerHTML = check().slice(0, 6).map(function (i) {
      return '<li class="' + (i.t ? "ok" : "") + '">' + i.m + "</li>";
    }).join("");

    // 池子高亮
    pool.querySelectorAll(".sb-cell").forEach(function (cell) {
      var id = cell.dataset.id, cnt = deck[id] || 0, c = byId[id];
      cell.classList.toggle("is-in", cnt > 0);
      cell.classList.toggle("is-full", cnt >= lim(c));
      cell.setAttribute("data-n", cnt > 0 ? "×" + cnt : c.name);
    });
  }

  function add(id) {
    var c = byId[id];
    if (!c) return;
    if (c.q === "域外" || c.cat === "觉醒") return;
    var cur = deck[id] || 0;
    if (cur >= lim(c)) return;
    if (total() >= 40 && !(deck[id] > 0)) return;
    if (c.cat === "天赋" && c.hero) {
      for (var k in deck) {
        if (k !== id && deck[k] && byId[k].cat === "天赋" && byId[k].hero === c.hero) return;
      }
    }
    var fs = facSet();
    if (c.fac !== "通用" && fs.length && fs.indexOf(c.fac) < 0) return;
    deck[id] = cur + 1;
    save(); renderDeck();
  }
  function del(id) {
    if (!deck[id]) return;
    deck[id]--;
    if (!deck[id]) delete deck[id];
    save(); renderDeck();
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(deck)); } catch (e) {}
  }

  /* ---------- 事件 ---------- */
  pool.addEventListener("click", function (e) {
    var t = e.target.closest("[data-add]");
    if (!t) {
      var cell = e.target.closest(".sb-cell");
      if (cell) add(cell.dataset.id);
      return;
    }
    add(t.getAttribute("data-add"));
  });
  deckList.addEventListener("click", function (e) {
    var t = e.target.closest("[data-del]");
    if (t) del(t.getAttribute("data-del"));
  });

  mount.querySelectorAll(".fchips").forEach(function (grp) {
    grp.querySelectorAll(".fchip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        grp.querySelectorAll(".fchip").forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        filter[grp.dataset.group] = btn.dataset.val || "";
        renderPool(); renderDeck();
      });
    });
  });
  if (searchEl) {
    searchEl.addEventListener("input", function () {
      filter.text = searchEl.value.trim().toLowerCase();
      renderPool(); renderDeck();
    });
  }

  var clear = document.getElementById("clearDeck");
  if (clear) clear.addEventListener("click", function () {
    if (!total()) return;
    deck = {}; save(); renderDeck();
  });

  var copy = document.getElementById("copyDeck");
  if (copy) copy.addEventListener("click", function () {
    var lines = ["长歌 · 卡组（" + total() + "/40）"];
    var fs = facSet();
    lines.push("阵营：" + (fs.join(" + ") || "未定") + "（含通用）");
    Object.keys(deck).filter(function (k) { return deck[k] > 0; })
      .sort(function (a, b) { return cost(byId[a]) - cost(byId[b]); })
      .forEach(function (k) { lines.push("×" + deck[k] + "　" + byId[k].name); });
    var text = lines.join("\n");
    var done = function () { copy.textContent = "已复制"; setTimeout(function () { copy.textContent = "复制牌表"; }, 1600); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { fallback(); });
    } else { fallback(); }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { copy.textContent = "复制失败"; }
      document.body.removeChild(ta);
    }
  });

  renderPool();
  renderDeck();
})();
