
(() => {
  'use strict';
  const doc = document.documentElement;
  doc.classList.add('js');

  const head = document.querySelector('.site-head');
  if (head) {
    const onScroll = () => head.classList.toggle('is-scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, {passive:true});
    onScroll();
  }

  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.addEventListener('click', (e) => {
      if (e.target.closest('a')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const reveal = document.querySelectorAll('[data-reveal]');
  if (reveal.length) {
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
        });
      }, {rootMargin:'0px 0px -8% 0px', threshold:.06});
      reveal.forEach((el) => io.observe(el));
    } else {
      reveal.forEach((el) => el.classList.add('is-in'));
    }
  }

  const bar = document.querySelector('[data-card-filters]');
  if (bar) {
    const tiles = Array.from(document.querySelectorAll('.card-tile'));
    const groups = Array.from(document.querySelectorAll('.card-group'));
    const count = document.querySelector('[data-filter-count]');
    const search = bar.querySelector('[data-filter-search]');
    const state = {faction:'all', quality:'all', group:'all', q:''};
    const apply = () => {
      let shown = 0;
      tiles.forEach((tile) => {
        const d = tile.dataset;
        const ok = (state.faction === 'all' || d.faction === state.faction)
          && (state.quality === 'all' || d.quality === state.quality)
          && (state.group === 'all' || d.group === state.group)
          && (!state.q || (d.name || '').toLowerCase().includes(state.q));
        tile.hidden = !ok;
        if (ok) shown += 1;
      });
      groups.forEach((g) => {
        g.hidden = !Array.from(g.querySelectorAll('.card-tile')).some((t) => !t.hidden);
      });
      if (count) count.textContent = String(shown).padStart(2, '0');
      const empty = document.querySelector('[data-empty-note]');
      if (empty) empty.hidden = shown !== 0;
      bar.querySelectorAll('[data-filter]').forEach((b) => {
        const on = state[b.dataset.filter] === b.dataset.value;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-pressed', String(on));
      });
    };
    bar.addEventListener('click', (e) => {
      const b = e.target.closest('[data-filter]');
      if (!b) return;
      state[b.dataset.filter] = b.dataset.value;
      apply();
    });
    if (search) {
      search.addEventListener('input', () => {
        state.q = search.value.trim().toLowerCase();
        apply();
      });
    }
    const reset = bar.querySelector('[data-filter-reset]');
    if (reset) reset.addEventListener('click', () => {
      state.faction = 'all'; state.quality = 'all'; state.group = 'all'; state.q = '';
      if (search) search.value = '';
      apply();
    });
    apply();
  }

  const demo = document.querySelector('[data-demo]');
  const demoData = document.getElementById('demo-data');
  if (demo && demoData) {
    let data;
    try { data = JSON.parse(demoData.textContent); } catch (err) { data = null; }
    if (data && data.steps && data.steps.length) {
      const zones = Array.from(demo.querySelectorAll('[data-demo-zone]'));
      const tokens = Array.from(demo.querySelectorAll('[data-token]'));
      const title = demo.querySelector('[data-demo-title]');
      const text = demo.querySelector('[data-demo-text]');
      const kicker = demo.querySelector('[data-demo-kicker]');
      const dots = demo.querySelector('[data-demo-dots]');
      let index = 0;
      if (dots && !dots.children.length) {
        data.steps.forEach(() => {
          const i = document.createElement('i');
          dots.appendChild(i);
        });
      }
      const render = () => {
        const step = data.steps[index];
        if (kicker) kicker.textContent = step.kicker || ('STEP ' + String(index + 1).padStart(2, '0'));
        if (title) title.textContent = step.title || '';
        if (text) text.textContent = step.text || '';
        zones.forEach((z, i) => z.classList.toggle('is-lit', (step.zones || []).includes(i)));
        if (step.pos) {
          tokens.forEach((t) => {
            const target = step.pos[t.dataset.token];
            if (typeof target === 'number' && zones[target] && t.parentElement !== zones[target]) {
              zones[target].appendChild(t);
            }
          });
        }
        tokens.forEach((t) => {
          const on = !step.tokens || step.tokens.includes(t.dataset.token);
          t.classList.toggle('is-on', on);
          t.style.display = on ? '' : 'none';
        });
        if (dots) Array.from(dots.children).forEach((d, i) => d.classList.toggle('is-on', i === index));
        const prev = demo.querySelector('[data-demo-prev]');
        const next = demo.querySelector('[data-demo-next]');
        if (prev) prev.disabled = index === 0;
        if (next) next.textContent = index === data.steps.length - 1 ? '重看一遍' : '下一步';
      };
      demo.addEventListener('click', (e) => {
        if (e.target.closest('[data-demo-next]')) {
          index = index === data.steps.length - 1 ? 0 : index + 1;
          render();
        } else if (e.target.closest('[data-demo-prev]')) {
          index = Math.max(0, index - 1);
          render();
        }
      });
      render();
    }
  }

  const lightbox = document.getElementById('lightbox');
  if (lightbox) {
    const img = lightbox.querySelector('img');
    document.querySelectorAll('[data-zoom]').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (img) img.src = btn.dataset.zoom;
        if (typeof lightbox.showModal === 'function') lightbox.showModal();
      });
    });
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox || e.target.closest('.lb-close')) lightbox.close();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && lightbox.open) lightbox.close();
    });
  }
})();
