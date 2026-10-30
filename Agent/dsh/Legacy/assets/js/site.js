/* ============================================================
   长歌 · 归档页 — 交互层
   1 导航/进度  2 滚动渐显  3 卡面倾斜  4 井字提示
   5 魔力曲线  6 战场射程演示  7 关系星图  8 目录高亮
   ============================================================ */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var fine = window.matchMedia("(hover:hover) and (pointer:fine)").matches;
  var reduce = window.matchMedia("(prefers-reduced-motion:reduce)").matches;

  /* ---------- 1. 导航 + 进度 ---------- */
  var nav = $(".nav"), prog = $(".nav-prog");
  function onScroll() {
    var y = window.scrollY || document.documentElement.scrollTop;
    if (nav) nav.classList.toggle("is-stuck", y > 40);
    if (prog) {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.width = (h > 0 ? Math.min(100, (y / h) * 100) : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- 2. 滚动渐显 ---------- */
  var reveals = $$(".reveal");
  if (reveals.length) {
    if (reduce || !("IntersectionObserver" in window)) {
      reveals.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
      reveals.forEach(function (el) { io.observe(el); });
    }
  }

  /* ---------- 3. 卡面倾斜 ---------- */
  if (fine && !reduce) {
    $$(".cface").forEach(function (card) {
      card.addEventListener("pointermove", function (ev) {
        var r = card.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width - 0.5;
        var py = (ev.clientY - r.top) / r.height - 0.5;
        card.style.transform =
          "perspective(900px) rotateX(" + (-py * 7).toFixed(2) + "deg) rotateY(" +
          (px * 8).toFixed(2) + "deg) translateY(-6px)";
        card.style.setProperty("--mx", (px * 100 + 50).toFixed(1) + "%");
        card.style.setProperty("--my", (py * 100 + 50).toFixed(1) + "%");
      });
      card.addEventListener("pointerleave", function () { card.style.transform = ""; });
    });
  }

  /* ---------- 4. 井字提示：触屏点击切换 ---------- */
  document.addEventListener("pointerdown", function (ev) {
    var t = ev.target.closest ? ev.target.closest(".term") : null;
    $$(".term.is-open").forEach(function (el) { if (el !== t) el.classList.remove("is-open"); });
    if (t) { t.classList.toggle("is-open"); }
  });
  $$(".term").forEach(function (t) {
    t.setAttribute("tabindex", "0");
    t.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); t.classList.toggle("is-open"); }
    });
  });

  /* ---------- 5. 魔力曲线 ---------- */
  var manaIn = $("#manaInput");
  if (manaIn) {
    var bars = $$(".mbar"), readB = $("#manaCap"), readT = $("#manaTurn"), readN = $("#manaNote");
    var paint = function () {
      var v = parseInt(manaIn.value, 10);
      bars.forEach(function (b, i) {
        var n = i + 1;
        var on = n <= v;
        b.style.height = (16 + Math.min(n, 12) / 12 * 84) + "%";
        b.style.opacity = on ? "1" : ".28";
        b.classList.toggle("is-soft", n > 12);
      });
      if (readB) readB.textContent = v;
      if (readT) readT.textContent = v > 12 ? "第 " + v + " 回合之后 · 已超出自然增长" : "第 " + v + " 回合 · 自然增长中";
      if (readN) readN.textContent = v > 12
        ? "正常情况下上限停在 12。要走到这里，得靠「绯红」一类的卡牌把上限推上去。"
        : (v === 12 ? "上限到 12，从此不再自然增长——之后的每一点，都得自己想办法。" : "回合开始：上限 +1，并回复至上限。");
    };
    manaIn.addEventListener("input", paint);
    paint();
  }

  /* ---------- 6. 战场射程演示 ---------- */
  var board = $("#board");
  if (board) {
    var LAB = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ"];
    var UNITS = {
      knight: { name: "战士 · 骑士", all: false, noDef: false, extra: "物理伤害；攻击会被反击。只能打相邻的战区——所以他必须走。" },
      ranger: { name: "战士 · 游侠", all: false, noDef: false, extra: "可在一回合中移动并攻击：先换线，再动手。战士里唯一能自己决定打谁的。" },
      guard: { name: "战士 · 近卫", all: false, noDef: false, extra: "可在一回合中攻击并防御：既能换血，也能替人挡刀。站得住，才打得久。" },
      mage: { name: "法师 · 魔法使", all: true, noDef: false, extra: "魔法伤害，可打任意战区。魔法使不受反击——所以她不必挑软的打。" },
      archer: { name: "弓箭手", all: true, noDef: true, extra: "物理伤害，无视守护；既不受到、也不造成反击。全场唯一能越过前排直取后排的单位。" }
    };
    var cur = "knight", pos = 3;
    var token = $("#demo-token", board);
    var zones = $$(".zone", board);
    var outName = $("#rangeName"), outAtk = $("#rangeAtk"), outDef = $("#rangeDef"), outExtra = $("#rangeExtra");
    var wrap = board.parentNode;

    function rectOf(z) { return $("rect", board.querySelector('[data-z="' + z + '"]')); }
    function center(z) {
      var r = rectOf(z);
      return { x: +r.getAttribute("x") + +r.getAttribute("width") / 2, y: +r.getAttribute("y") + +r.getAttribute("height") / 2 };
    }
    function paintBoard() {
      var u = UNITS[cur], c = center(pos);
      if (token) token.setAttribute("transform", "translate(" + c.x + "," + (c.y + 30) + ")");
      zones.forEach(function (g) {
        var z = +g.getAttribute("data-z");
        var inAtk = u.all ? z !== pos : Math.abs(z - pos) === 1;
        var rect = rectOf(z);
        rect.classList.toggle("is-attack", inAtk);
        rect.classList.toggle("is-self", z === pos);
      });
      var adj = [pos - 1, pos + 1].filter(function (n) { return n >= 1 && n <= 5; })
        .map(function (n) { return LAB[n - 1]; }).join("、");
      if (outName) outName.textContent = u.name + " · 位于 " + LAB[pos - 1] + " 区";
      if (outAtk) outAtk.textContent = u.all ? "五个战区全部" : (adj || "无");
      if (outDef) outDef.textContent = u.noDef ? "——（弓箭手没有防御范围）" : (u.all ? "五个战区全部" : "自身与相邻战区");
      if (outExtra) outExtra.textContent = u.extra;
    }
    $$(".rb", wrap).forEach(function (b) {
      b.addEventListener("click", function () {
        cur = b.getAttribute("data-unit");
        $$(".rb", wrap).forEach(function (o) { o.setAttribute("aria-pressed", o === b ? "true" : "false"); });
        paintBoard();
      });
    });
    zones.forEach(function (g) {
      g.style.cursor = "pointer";
      g.addEventListener("click", function () { pos = +g.getAttribute("data-z"); paintBoard(); });
    });
    paintBoard();
  }

  /* ---------- 7. 关系星图 ---------- */
  $$(".const svg").forEach(function (svg) {
    var nodes = $$(".cnode", svg), edges = $$(".cedge", svg);
    function clear() {
      nodes.forEach(function (n) { n.classList.remove("is-lit", "is-dim"); });
      edges.forEach(function (e) { e.classList.remove("is-hot", "is-dim"); });
    }
    nodes.forEach(function (n) {
      var id = n.getAttribute("data-id");
      var near = {};
      near[id] = 1;
      n.addEventListener("pointerenter", function () {
        edges.forEach(function (e) {
          var a = e.getAttribute("data-a"), b = e.getAttribute("data-b");
          if (a === id || b === id) {
            e.classList.add("is-hot"); near[a] = 1; near[b] = 1;
          } else { e.classList.add("is-dim"); }
        });
        nodes.forEach(function (o) { o.classList.toggle("is-dim", !near[o.getAttribute("data-id")]); });
      });
      n.addEventListener("pointerleave", clear);
      n.addEventListener("focus", function () { n.dispatchEvent(new Event("pointerenter")); });
      n.addEventListener("blur", clear);
    });
  });

  /* ---------- 8. 目录 / 锚点高亮（规则页） ---------- */
  var toc = $$(".rb-toc a");
  if (toc.length && "IntersectionObserver" in window) {
    var map = {};
    toc.forEach(function (a) {
      var t = $(a.getAttribute("href"));
      if (t) map[t.id] = a;
    });
    var io2 = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          toc.forEach(function (a) { a.classList.remove("is-active"); });
          if (map[e.target.id]) map[e.target.id].classList.add("is-active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { io2.observe(document.getElementById(id)); });
  }
})();
