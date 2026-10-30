/* 长歌官方页 · 本地文本编辑器 */
(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const frame = $("#frame");
  const pageList = $("#page-list");
  const search = $("#search");
  const saveBtn = $("#save");
  const resetBtn = $("#reset");
  const rebuildBtn = $("#rebuild");
  const dirtyEl = $("#dirty");
  const statusEl = $("#status");
  const buildInfo = $("#build-info");
  const crumb = $("#crumb");
  const emptyEl = $("#frame-empty");
  const toastEl = $("#toast");

  const state = {
    pages: [],
    current: null,
    dirty: false,
    busy: false,
    loading: false,
    toastTimer: 0,
  };

  const SKIP_SELECTOR = "script,style,code,pre,svg,button,textarea,select,option";
  const EDITOR_CSS = `
    html { scroll-behavior: auto !important; }
    .site-header, .site-head, .site-foot, .skip-link, .nav-toggle, .mobile-nav { display: none !important; }
    main { padding-top: 20px !important; }
    a { cursor: text !important; }
    .ed-text {
      outline: 1px dashed transparent;
      outline-offset: 2px;
      border-radius: 2px;
      transition: background .12s ease, outline-color .12s ease;
      cursor: text;
    }
    .ed-text:hover { background: rgba(166,124,61,.10); outline-color: rgba(166,124,61,.38); }
    .ed-text:focus {
      background: #fffaf0;
      outline: 1px solid #a67c3d;
      box-shadow: 0 0 0 3px rgba(166,124,61,.12);
    }
    .ed-text.is-dirty { background: rgba(158,59,59,.075); }
    .ed-text.is-dirty:focus { background: #fff7f2; outline-color: #9e3b3b; }
    ::selection { background: rgba(166,124,61,.25); }
  `;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function api(url, options = {}) {
    const opts = { ...options };
    opts.headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    const res = await fetch(url, opts);
    let data = null;
    try {
      data = await res.json();
    } catch (err) {
      throw new Error(`服务返回了非 JSON 内容（${res.status}）`);
    }
    if (!res.ok || !data || data.ok === false) {
      throw new Error((data && data.error) || `请求失败（${res.status}）`);
    }
    return data;
  }

  function toast(message, isError = false) {
    window.clearTimeout(state.toastTimer);
    toastEl.textContent = message;
    toastEl.classList.toggle("is-error", !!isError);
    toastEl.classList.add("is-show");
    state.toastTimer = window.setTimeout(() => toastEl.classList.remove("is-show"), isError ? 6500 : 4200);
  }

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function setBusy(busy, text) {
    state.busy = busy;
    resetBtn.disabled = busy;
    rebuildBtn.disabled = busy;
    saveBtn.disabled = busy || !state.dirty;
    if (busy && text) setStatus(text);
    document.body.classList.toggle("is-busy", busy);
  }

  function syncDirty() {
    const doc = frame.contentDocument;
    const spans = doc && !state.loading ? [...doc.querySelectorAll(".ed-text")] : [];
    const changed = spans.filter((span) => span.classList.contains("is-dirty"));
    state.dirty = changed.length > 0;
    dirtyEl.classList.toggle("is-dirty", state.dirty);
    dirtyEl.classList.toggle("is-clean", !state.dirty);
    dirtyEl.querySelector("b").textContent = state.dirty ? `未保存 ${changed.length} 处` : "未修改";
    saveBtn.disabled = state.busy || !state.dirty;
  }

  function markSpan(span) {
    if (!span) return;
    const text = span.textContent.trim();
    span.classList.toggle("is-dirty", text !== span.dataset.orig);
    syncDirty();
  }

  function renderList() {
    const query = search.value.trim().toLowerCase();
    const groups = ["总览", "游戏编", "卡牌档案"];
    const fragment = document.createDocumentFragment();
    let shown = 0;

    for (const group of groups) {
      const items = state.pages.filter((page) => {
        if (page.group !== group) return false;
        if (!query) return true;
        return `${page.title} ${page.path}`.toLowerCase().includes(query);
      });
      if (!items.length) continue;

      const label = document.createElement("div");
      label.className = "group-label";
      label.textContent = `${group} · ${items.length}`;
      fragment.append(label);

      for (const page of items) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "page-item" + (page.path === state.current ? " is-active" : "");
        btn.dataset.path = page.path;
        btn.title = page.path;
        btn.innerHTML = `
          <span class="t">${escapeHtml(page.title)}</span>
          <span class="m">${escapeHtml(page.path)}</span>
          ${page.patched ? `<span class="count">${page.patched}</span>` : ""}
        `;
        btn.addEventListener("click", () => loadPage(page.path));
        fragment.append(btn);
        shown += 1;
      }
    }

    pageList.replaceChildren(fragment);
    if (!shown) {
      const empty = document.createElement("div");
      empty.className = "empty-list";
      empty.textContent = query ? "没有匹配的页面。" : "还没有页面，先运行 build.py。";
      pageList.append(empty);
    }
  }

  function updateActive() {
    for (const btn of pageList.querySelectorAll(".page-item")) {
      btn.classList.toggle("is-active", btn.dataset.path === state.current);
    }
  }

  function siteUrl(path) {
    return `/site/${path.split("/").map(encodeURIComponent).join("/")}?v=${Date.now()}`;
  }

  function loadPage(path, options = {}) {
    if (!path) return;
    if (!options.force && state.dirty) {
      const ok = window.confirm("当前页面还有未保存的修改。切换页面会丢失这些修改，继续吗？");
      if (!ok) return;
    }
    state.current = path;
    state.dirty = false;
    state.loading = true;
    syncDirty();
    updateActive();
    const page = state.pages.find((item) => item.path === path);
    crumb.innerHTML = `${escapeHtml(page ? page.title : path)}<em>${escapeHtml(path)}</em>`;
    emptyEl.classList.add("is-hidden");
    setStatus("正在载入页面…");
    try {
      history.replaceState(null, "", `#${encodeURIComponent(path)}`);
    } catch (err) {
      /* 某些 file:// 环境不允许改 hash；忽略。 */
    }
    frame.src = siteUrl(path);
  }

  function injectEditorStyle(doc) {
    if (doc.getElementById("__editor_style")) return;
    const style = doc.createElement("style");
    style.id = "__editor_style";
    style.textContent = EDITOR_CSS;
    (doc.head || doc.documentElement).append(style);
  }

  function wrapTextNodes(doc, root) {
    const walker = doc.createTreeWalker(root, 4, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return 2; // FILTER_REJECT
        const parent = node.parentElement;
        if (!parent) return 2;
        if (parent.closest(SKIP_SELECTOR)) return 2;
        if (parent.closest(".ed-text")) return 2;
        if (parent.closest("[contenteditable]")) return 2;
        return 1; // FILTER_ACCEPT
      },
    });

    const nodes = [];
    let node = walker.nextNode();
    while (node) {
      nodes.push(node);
      node = walker.nextNode();
    }

    nodes.forEach((textNode, index) => {
      const span = doc.createElement("span");
      span.className = "ed-text";
      span.dataset.orig = textNode.nodeValue.trim();
      span.dataset.index = String(index);
      span.setAttribute("contenteditable", "plaintext-only");
      span.setAttribute("spellcheck", "false");
      span.textContent = textNode.nodeValue;
      textNode.parentNode.replaceChild(span, textNode);
    });
    return nodes.length;
  }

  function setupFrame() {
    if (!state.current) return;
    const doc = frame.contentDocument;
    if (!doc) throw new Error("无法访问页面内容。");
    const main = doc.querySelector("main");
    if (!main) throw new Error("这个页面没有 <main> 区域，无法进入编辑模式。");

    injectEditorStyle(doc);

    doc.addEventListener("click", (event) => {
      const link = event.target && event.target.closest ? event.target.closest("a") : null;
      if (link) event.preventDefault();
    }, true);
    doc.addEventListener("auxclick", (event) => {
      if (event.target && event.target.closest && event.target.closest("a")) event.preventDefault();
    }, true);
    doc.addEventListener("submit", (event) => event.preventDefault(), true);

    doc.addEventListener("input", (event) => {
      const span = event.target && event.target.closest ? event.target.closest(".ed-text") : null;
      if (span) markSpan(span);
    });

    doc.addEventListener("paste", (event) => {
      const span = event.target && event.target.closest ? event.target.closest(".ed-text") : null;
      if (!span) return;
      event.preventDefault();
      const text = (event.clipboardData || window.clipboardData).getData("text/plain").replace(/\s*\n+\s*/g, " ");
      doc.execCommand("insertText", false, text);
    });

    doc.addEventListener("beforeinput", (event) => {
      if (event.inputType === "insertParagraph" || event.inputType === "insertLineBreak") {
        event.preventDefault();
      }
    });

    doc.addEventListener("keydown", (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        save();
      } else if (event.key === "Escape") {
        if (doc.activeElement && doc.activeElement.blur) doc.activeElement.blur();
      } else if (event.key === "Enter") {
        event.preventDefault();
      }
    });

    const count = wrapTextNodes(doc, main);
    state.loading = false;
    state.dirty = false;
    syncDirty();
    setStatus(`可编辑文本 ${count} 处`);
    emptyEl.classList.add("is-hidden");
  }

  function collectChanges() {
    const doc = frame.contentDocument;
    if (!doc) return [];
    const changes = [];
    for (const span of doc.querySelectorAll(".ed-text")) {
      const next = span.textContent.trim();
      if (next === span.dataset.orig) continue;
      changes.push({
        old: span.dataset.orig,
        new: next,
        index: Number(span.dataset.index),
      });
    }
    return changes;
  }

  async function save() {
    if (state.busy || !state.current) return;
    const changes = collectChanges();
    if (!changes.length) {
      toast("没有需要保存的修改。");
      syncDirty();
      return;
    }
    setBusy(true, `正在保存 ${changes.length} 处修改并重建…`);
    try {
      const data = await api("/api/save", {
        method: "POST",
        body: JSON.stringify({ path: state.current, changes }),
      });
      if (data.output) buildInfo.textContent = data.output.replace(/\s+/g, " ").slice(0, 160);
      toast(`已保存 ${data.count} 处修改，站点已重建。`);
      await loadPages();
      state.loading = true;
      reloadFrame();
    } catch (error) {
      toast(error.message, true);
      setStatus("保存失败");
    } finally {
      setBusy(false);
      syncDirty();
    }
  }

  async function resetPage() {
    if (state.busy || !state.current) return;
    const ok = window.confirm("删除这一页已保存的所有文字补丁，并重建站点？\n（当前未保存的修改也会丢失。）");
    if (!ok) return;
    setBusy(true, "正在还原并重建…");
    try {
      const data = await api("/api/reset", {
        method: "POST",
        body: JSON.stringify({ path: state.current }),
      });
      if (data.output) buildInfo.textContent = data.output.replace(/\s+/g, " ").slice(0, 160);
      toast("已还原此页。");
      await loadPages();
      state.loading = true;
      reloadFrame();
    } catch (error) {
      toast(error.message, true);
      setStatus("还原失败");
    } finally {
      setBusy(false);
      syncDirty();
    }
  }

  async function rebuild() {
    if (state.busy) return;
    setBusy(true, "正在重建站点…");
    try {
      const data = await api("/api/rebuild", { method: "POST", body: "{}" });
      if (data.output) buildInfo.textContent = data.output.replace(/\s+/g, " ").slice(0, 160);
      toast("站点已重建。");
      await loadPages();
      state.loading = true;
      reloadFrame();
    } catch (error) {
      toast(error.message, true);
      setStatus("重建失败");
    } finally {
      setBusy(false);
      syncDirty();
    }
  }

  function reloadFrame() {
    if (!state.current) return;
    frame.src = siteUrl(state.current);
  }

  async function loadPages() {
    const data = await api("/api/pages");
    state.pages = Array.isArray(data.pages) ? data.pages : [];
    renderList();
  }

  frame.addEventListener("load", () => {
    if (!state.current) return;
    try {
      setupFrame();
    } catch (error) {
      state.loading = false;
      emptyEl.classList.remove("is-hidden");
      emptyEl.innerHTML = `<span class="eyebrow">EDITOR ERROR</span><p>${escapeHtml(error.message)}</p>`;
      setStatus("页面无法编辑");
      toast(error.message, true);
    }
  });

  search.addEventListener("input", renderList);
  saveBtn.addEventListener("click", save);
  resetBtn.addEventListener("click", resetPage);
  rebuildBtn.addEventListener("click", rebuild);

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
      event.preventDefault();
      save();
    }
  });

  window.addEventListener("beforeunload", (event) => {
    if (!state.dirty) return;
    event.preventDefault();
    event.returnValue = "";
  });

  async function boot() {
    try {
      setStatus("正在读取页面清单…");
      await loadPages();
      let requested = "";
      try {
        requested = decodeURIComponent(location.hash.slice(1));
      } catch (err) {
        requested = "";
      }
      const exists = requested && state.pages.some((page) => page.path === requested);
      const first = exists ? requested : "index.html";
      loadPage(first, { force: true });
    } catch (error) {
      setStatus("无法连接本地服务");
      emptyEl.classList.remove("is-hidden");
      emptyEl.innerHTML = `<span class="eyebrow">SERVER ERROR</span><p>${escapeHtml(error.message)}</p>`;
      toast(error.message, true);
    }
  }

  boot();
})();
