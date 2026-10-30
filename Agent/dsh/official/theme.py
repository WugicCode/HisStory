# -*- coding: utf-8 -*-
"""长歌官方页的样式与脚本。纯静态、无外部依赖。"""

CSS = r"""
:root{
  --paper:#f4efe4;
  --paper-2:#ece4d3;
  --paper-3:#e4d9c4;
  --ink:#171c26;
  --ink-2:#2a3241;
  --soft:#59584f;
  --muted:#8b8679;
  --line:rgba(23,28,38,.16);
  --line-strong:rgba(23,28,38,.34);
  --gold:#a67c3d;
  --gold-soft:#c2a06a;
  --red:#9e3b3b;
  --blue:#2f4a6b;
  --green:#46624d;
  --violet:#5b4a6b;
  --night:#0d131f;
  --night-2:#141d2c;
  --night-line:rgba(244,239,228,.16);
  --serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;
  --sans:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif;
  --latin:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,"Times New Roman",serif;
  --mono:"Cascadia Mono","Consolas","SFMono-Regular",monospace;
  --wrap:1180px;
  --head:72px;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--sans);font-size:16px;line-height:1.78;
  font-feature-settings:"kern" 1,"liga" 1;
  text-rendering:optimizeLegibility;
}
body::before{
  content:"";position:fixed;inset:0;z-index:9000;pointer-events:none;opacity:.13;
  mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.86' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='.6'/%3E%3C/svg%3E");
}
::selection{background:var(--red);color:var(--paper)}
img{max-width:100%;display:block}
a{color:inherit;text-decoration:none}
a:hover{color:var(--red)}
button{font:inherit;color:inherit}
h1,h2,h3,h4,p,figure,blockquote,ul,ol{margin:0}
ul,ol{padding:0;list-style:none}
hr{border:0;border-top:1px solid var(--line);margin:0}
.wrap{width:min(var(--wrap),calc(100% - 64px));margin:0 auto}
.skip{position:absolute;left:-9999px;top:0;background:var(--ink);color:var(--paper);padding:10px 16px;z-index:10000}
.skip:focus{left:12px;top:12px}
.latin{font-family:var(--latin);letter-spacing:.22em;text-transform:uppercase;font-size:11px}
.eyebrow{font-family:var(--latin);font-size:11px;letter-spacing:.24em;text-transform:uppercase;color:var(--gold);display:flex;align-items:center;gap:12px}
.eyebrow::before{content:"";display:inline-block;width:28px;height:1px;background:currentColor;opacity:.7}
.eyebrow.center{justify-content:center}
.lead{font-family:var(--serif);font-size:clamp(18px,1.7vw,21px);line-height:2;color:var(--soft);max-width:64ch}
.muted{color:var(--muted)}
.small{font-size:12px;line-height:1.8}
.mono{font-family:var(--mono);font-size:12px;letter-spacing:.04em}
.serif{font-family:var(--serif)}
.center{text-align:center}
.nowrap{white-space:nowrap}
.sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}

/* header */
.site-head{position:sticky;top:0;z-index:100;background:rgba(244,239,228,.88);backdrop-filter:blur(14px);border-bottom:1px solid transparent;transition:border-color .3s,background .3s}
.site-head.is-scrolled{border-bottom-color:var(--line);background:rgba(244,239,228,.95)}
.site-head .wrap{height:var(--head);display:flex;align-items:center;justify-content:space-between;gap:32px}
.brand{display:flex;align-items:center;gap:12px;flex-shrink:0;text-decoration:none}
.brand-dot{width:7px;height:7px;background:var(--gold);display:block;flex:0 0 7px;margin-right:2px}
.brand-seal{width:40px;height:40px;display:block;flex:0 0 40px;box-shadow:0 0 0 1px rgba(23,28,38,.12)}
.brand-mark{width:34px;height:34px;border:1px solid var(--ink);border-radius:50%;display:grid;place-items:center;font-family:var(--serif);font-size:17px;line-height:1;padding-top:2px}
.brand-text{display:flex;flex-direction:column;line-height:1.05;font-family:var(--serif);font-size:19px;letter-spacing:.18em}
.brand-text small{font-family:var(--latin);font-size:8px;letter-spacing:.34em;color:var(--gold);margin-top:5px}
.nav{display:flex;align-items:center;gap:26px;font-size:13px;letter-spacing:.1em}
.nav a{position:relative;padding:6px 0;color:var(--soft);white-space:nowrap}
.nav a::after{content:"";position:absolute;left:0;right:100%;bottom:0;height:1px;background:var(--red);transition:right .3s}
.nav a:hover,.nav a.is-active{color:var(--ink)}
.nav a:hover::after,.nav a.is-active::after{right:0}
.nav-toggle{display:none;width:42px;height:42px;border:1px solid var(--line);background:transparent;cursor:pointer;position:relative}
.nav-toggle span,.nav-toggle span::before,.nav-toggle span::after{position:absolute;left:11px;width:18px;height:1px;background:var(--ink);content:"";transition:.25s}
.nav-toggle span{top:20px}
.nav-toggle span::before{left:0;top:-6px}
.nav-toggle span::after{left:0;top:6px}

/* cover */
.cover{position:relative;min-height:min(92vh,900px);display:flex;align-items:flex-end;background:var(--night);color:var(--paper);overflow:hidden}
.cover-art{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center}
.cover::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,19,31,.12) 0%,rgba(13,19,31,.05) 40%,rgba(13,19,31,.72) 100%)}
.cover .wrap{position:relative;z-index:2;padding-top:calc(var(--head) + 60px);padding-bottom:54px}
.cover-top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(244,239,228,.24);padding-bottom:14px;font-family:var(--latin);font-size:10px;letter-spacing:.24em;text-transform:uppercase;color:rgba(244,239,228,.72)}
.cover-main{display:grid;grid-template-columns:minmax(0,1fr) minmax(220px,320px);gap:48px;align-items:end;padding:52px 0 44px}
.cover h1{font-family:var(--serif);font-weight:500;font-size:clamp(78px,14vw,180px);line-height:.92;letter-spacing:.06em;margin-left:-.04em;text-shadow:0 2px 30px rgba(0,0,0,.25)}
.cover .latin-big{font-family:var(--latin);font-size:clamp(13px,1.5vw,18px);letter-spacing:.72em;color:var(--gold-soft);margin-top:16px;text-transform:uppercase}
.cover-note{font-family:var(--serif);font-size:15px;line-height:2.1;color:rgba(244,239,228,.84);border-left:1px solid rgba(244,239,228,.32);padding-left:22px}
.cover-note b{font-weight:500;color:#fff}
.cover-bottom{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;border-top:1px solid rgba(244,239,228,.24);padding-top:18px}
.cover-stats{display:flex;gap:34px}
.cover-stats div{display:flex;flex-direction:column;gap:2px}
.cover-stats b{font-family:var(--latin);font-size:24px;font-weight:400;letter-spacing:.04em;color:var(--gold-soft)}
.cover-stats span{font-size:10px;letter-spacing:.18em;color:rgba(244,239,228,.55)}
.cover-scroll{font-family:var(--latin);font-size:9px;letter-spacing:.28em;color:rgba(244,239,228,.62);writing-mode:vertical-rl;display:flex;align-items:center;gap:12px}
.cover-scroll::after{content:"";width:1px;height:42px;background:rgba(244,239,228,.45)}
.cover--game{min-height:74vh}
.cover--game h1{font-size:clamp(62px,10vw,124px)}
.cover--game .cover-main{padding-top:38px;padding-bottom:34px}
.cover--game .cover-note{background:rgba(13,19,31,.62);border-left-color:rgba(244,239,228,.28);padding:18px 20px}

/* buttons */
.btn{display:inline-flex;align-items:center;gap:10px;border:1px solid var(--line-strong);padding:11px 18px;font-size:12px;letter-spacing:.12em;background:transparent;cursor:pointer;transition:.25s}
.btn::after{content:"→";font-family:var(--latin);transition:transform .25s}
.btn:hover{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.btn:hover::after{transform:translateX(4px)}
.btn--light{border-color:rgba(244,239,228,.42);color:var(--paper)}
.btn--light:hover{background:var(--paper);color:var(--ink);border-color:var(--paper)}
.btn--red{border-color:var(--red);color:var(--red)}
.btn--red:hover{background:var(--red);color:var(--paper);border-color:var(--red)}

/* sections */
.section{padding:96px 0;border-top:1px solid var(--line)}
.section--tight{padding:64px 0}
.section--night{background:var(--night);color:var(--paper);border-top:1px solid var(--night)}
.section--night .lead{color:rgba(244,239,228,.68)}
.section--night .eyebrow{color:var(--gold-soft)}
.section-head{display:grid;grid-template-columns:96px minmax(0,1fr);gap:28px;margin-bottom:52px;align-items:start}
.section-num{font-family:var(--latin);font-size:13px;letter-spacing:.14em;color:var(--gold);padding-top:10px;border-top:1px solid var(--gold);width:48px}
.section-head h2{font-family:var(--serif);font-weight:500;font-size:clamp(34px,4vw,52px);line-height:1.2;letter-spacing:.03em;margin:6px 0 12px}
.section-head .lead{max-width:60ch}
.section-more{margin-top:32px}

/* triptych */
.triptych{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.triptych article{background:var(--paper);padding:34px 30px 30px;display:flex;flex-direction:column;min-height:320px;position:relative;transition:background .35s}
.triptych article:hover{background:#f8f4ea}
.triptych .t-num{font-family:var(--latin);font-size:11px;letter-spacing:.2em;color:var(--gold)}
.triptych h3{font-family:var(--serif);font-size:30px;font-weight:500;margin:18px 0 4px;letter-spacing:.04em}
.triptych .t-latin{font-family:var(--latin);font-size:9px;letter-spacing:.26em;color:var(--muted);text-transform:uppercase}
.triptych p{margin-top:18px;font-size:14px;line-height:1.95;color:var(--soft);flex:1}
.triptych .t-status{font-size:10px;letter-spacing:.16em;color:var(--red);margin-top:18px}
.triptych a.t-go{margin-top:22px;font-size:12px;letter-spacing:.12em;color:var(--ink);border-bottom:1px solid var(--line-strong);padding-bottom:4px;align-self:flex-start}

/* stats */
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.stat-row div{background:var(--paper);padding:26px 24px}
.stat-row b{display:block;font-family:var(--latin);font-size:clamp(38px,4.4vw,58px);font-weight:400;line-height:1;color:var(--ink)}
.stat-row span{display:block;font-size:11px;letter-spacing:.14em;color:var(--muted);margin-top:10px}

/* game preview strip */
.night-head{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:56px;align-items:end}
.night-head h2{font-family:var(--serif);font-weight:500;font-size:clamp(40px,5.6vw,76px);line-height:1.08;letter-spacing:.03em}
.night-head .lead{color:rgba(244,239,228,.7)}
.plate-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:52px;align-items:start}
.plate-strip a{display:block;position:relative}
.plate-strip img{border:1px solid rgba(244,239,228,.22);box-shadow:0 18px 40px rgba(0,0,0,.28);transition:transform .4s,box-shadow .4s}
.plate-strip a:nth-child(2){transform:translateY(26px)}
.plate-strip a:hover img{transform:translateY(-6px);box-shadow:0 26px 54px rgba(0,0,0,.38)}
.plate-strip figcaption{display:flex;justify-content:space-between;gap:12px;margin-top:10px;font-size:10px;letter-spacing:.1em;color:rgba(244,239,228,.58)}
.game-cols{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--night-line);border:1px solid var(--night-line);margin-top:56px}
.game-cols article{background:var(--night);padding:30px 28px}
.game-cols h3{font-family:var(--serif);font-size:24px;font-weight:500;margin-bottom:8px}
.game-cols p{font-size:14px;line-height:1.95;color:rgba(244,239,228,.66)}
.game-cols .latin{color:var(--gold-soft);margin-bottom:14px}

/* page hero */
.page-hero{padding:104px 0 64px;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.page-hero .eyebrow{margin-bottom:20px}
.page-hero h1{font-family:var(--serif);font-weight:500;font-size:clamp(52px,8.4vw,108px);line-height:1.06;letter-spacing:.04em}
.page-hero .lead{margin-top:22px}
.page-hero .hero-latin{position:absolute;right:max(32px,calc((100vw - var(--wrap))/2));bottom:26px;writing-mode:vertical-rl;font-family:var(--latin);font-size:10px;letter-spacing:.4em;color:var(--muted);text-transform:uppercase}

/* chapters */
.chapter{display:grid;grid-template-columns:190px minmax(0,1fr);gap:48px;padding:76px 0;border-top:1px solid var(--line)}
.chapter-side{position:sticky;top:calc(var(--head) + 28px);align-self:start}
.chapter-side .num{font-family:var(--latin);font-size:11px;letter-spacing:.16em;color:var(--gold)}
.chapter-side h2{font-family:var(--serif);font-size:27px;font-weight:500;line-height:1.3;margin:10px 0 8px}
.chapter-side .latin{font-size:9px;color:var(--muted)}
.chapter-body{min-width:0}
.chapter-body > p{max-width:68ch;margin-bottom:22px;color:var(--soft);line-height:2}
.chapter-body > p:first-child{font-family:var(--serif);font-size:19px;color:var(--ink);line-height:2.05}
.figure{margin:34px 0}
.figure img{border:1px solid var(--line);box-shadow:0 14px 34px rgba(23,28,38,.08)}
.figure figcaption{display:flex;justify-content:space-between;gap:16px;border-bottom:1px solid var(--line);padding:10px 0;font-size:11px;color:var(--muted);letter-spacing:.06em}
.figure figcaption b{font-weight:500;color:var(--ink);letter-spacing:.1em}
.pullquote{font-family:var(--serif);font-size:clamp(22px,2.6vw,30px);line-height:1.85;border-left:2px solid var(--red);padding:8px 0 8px 26px;margin:32px 0;color:var(--ink)}
.pullquote span{display:block;font-family:var(--sans);font-size:12px;letter-spacing:.12em;color:var(--muted);margin-top:12px}

/* law grid */
.law-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:30px}
.law{border-top:2px solid var(--ink);padding-top:18px}
.law .law-num{font-family:var(--latin);font-size:12px;letter-spacing:.2em;color:var(--gold)}
.law h3{font-family:var(--serif);font-size:20px;font-weight:500;margin:10px 0 10px;line-height:1.4}
.law p{font-size:14px;line-height:1.95;color:var(--soft)}

/* race list */
.race-list{border-top:1px solid var(--line-strong)}
.race-row{display:grid;grid-template-columns:200px minmax(0,1fr);gap:28px;padding:24px 0;border-bottom:1px solid var(--line)}
.race-row h3{font-family:var(--serif);font-size:25px;font-weight:500}
.race-row .race-tag{font-size:11px;letter-spacing:.12em;color:var(--gold);margin-top:4px}
.race-row p{font-size:14px;line-height:1.95;color:var(--soft)}
.race-row p + p{margin-top:6px}

/* org / place grids */
.org-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:30px}
.org-grid article{background:var(--paper);padding:28px}
.org-grid h3{font-family:var(--serif);font-size:23px;font-weight:500;margin-bottom:6px}
.org-grid .latin{font-size:9px;color:var(--gold)}
.org-grid p{font-size:14px;line-height:1.9;color:var(--soft);margin-top:12px}
.place-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:30px}
.place-grid article{background:var(--paper);padding:22px}
.place-grid h3{font-family:var(--serif);font-size:19px;font-weight:500}
.place-grid p{font-size:13px;line-height:1.85;color:var(--soft);margin-top:8px}
.place-grid .tag{font-size:9px;letter-spacing:.12em;color:var(--muted);margin-top:12px;display:block}

/* timeline */
.timeline{margin:40px 0 0;border-left:1px solid var(--line-strong);padding-left:34px}
.tl-item{position:relative;padding-bottom:44px}
.tl-item::before{content:"";position:absolute;left:-38px;top:8px;width:7px;height:7px;border-radius:50%;background:var(--paper);border:1px solid var(--ink)}
.tl-item.is-red::before{background:var(--red);border-color:var(--red)}
.tl-item .tl-date{font-family:var(--latin);font-size:11px;letter-spacing:.14em;color:var(--gold);text-transform:uppercase}
.tl-item h3{font-family:var(--serif);font-size:24px;font-weight:500;margin:6px 0 8px}
.tl-item p{font-size:14px;line-height:1.95;color:var(--soft);max-width:70ch}
.tl-item .tl-tag{display:inline-block;font-size:9px;letter-spacing:.14em;border:1px solid var(--line);padding:2px 7px;margin-left:8px;vertical-align:3px;color:var(--muted)}

/* apocrypha */
.apocrypha{background:var(--night);color:var(--paper);padding:64px;position:relative;overflow:hidden;margin:80px 0}
.apocrypha::before{content:"";position:absolute;right:-90px;top:-110px;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle at 42% 40%,rgba(158,59,59,.55),rgba(158,59,59,.1) 58%,transparent 70%)}
.apocrypha .eyebrow{color:var(--gold-soft)}
.apocrypha h2{font-family:var(--serif);font-size:clamp(32px,4vw,48px);font-weight:500;margin:12px 0 10px}
.apocrypha .lead{color:rgba(244,239,228,.66);max-width:56ch}
.question-list{margin-top:36px;display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--night-line);border:1px solid var(--night-line);position:relative;z-index:2}
.question-list li{background:var(--night);padding:24px}
.question-list b{display:block;font-family:var(--latin);font-size:10px;letter-spacing:.2em;color:var(--gold-soft);margin-bottom:8px}
.question-list p{font-family:var(--serif);font-size:18px;line-height:1.8;color:rgba(244,239,228,.9)}
.apocrypha .ap-note{margin-top:26px;font-size:12px;color:rgba(244,239,228,.48);position:relative;z-index:2}

/* cast */
.cast-section{padding:72px 0;border-top:1px solid var(--line)}
.cast-head{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:34px}
.cast-head h2{font-family:var(--serif);font-size:clamp(32px,4vw,46px);font-weight:500}
.cast-head .lead{font-size:15px;max-width:48ch}
.cast-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}
.cast-card{background:var(--paper);padding:34px;display:grid;grid-template-columns:104px minmax(0,1fr);gap:24px;position:relative}
.cast-filler{background:var(--paper)}
.cast-sigil img{width:104px;height:104px;border:1px solid var(--line);border-radius:50%;background:#f8f3e8}
.cast-latin{font-family:var(--latin);font-size:9px;letter-spacing:.2em;color:var(--gold);text-transform:uppercase}
.cast-card h3{font-family:var(--serif);font-size:29px;font-weight:500;line-height:1.2;margin:4px 0 2px}
.cast-epithet{font-size:11px;letter-spacing:.08em;color:var(--muted)}
.cast-motto{font-family:var(--serif);font-size:16px;line-height:1.8;color:var(--red);margin:14px 0 12px}
.cast-bio p{font-size:13.5px;line-height:1.95;color:var(--soft);margin-bottom:8px}
.cast-facts{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.cast-facts span{font-size:10.5px;letter-spacing:.04em;color:var(--muted)}
.cast-facts b{font-weight:500;color:var(--ink);margin-right:4px}
.cast-status{position:absolute;right:22px;top:22px;font-size:9px;letter-spacing:.14em;color:var(--red);border:1px solid rgba(158,59,59,.45);padding:2px 7px;transform:rotate(2deg)}
.cast-more{margin-top:14px}
.cast-more a{font-size:11px;letter-spacing:.1em;border-bottom:1px solid var(--line-strong);padding-bottom:2px}

/* rules / play */
.rule-block{margin-top:44px}
.rule-block[id]{scroll-margin-top:calc(var(--head) + 24px)}
.rule-block h2{font-family:var(--serif);font-size:clamp(28px,3.4vw,40px);font-weight:500;margin-bottom:10px}
.rule-block h2 .num{font-family:var(--latin);font-size:11px;letter-spacing:.16em;color:var(--gold);display:block;margin-bottom:4px}
.rule-cols{display:grid;grid-template-columns:1fr 1fr;gap:36px;margin-top:24px}
.rule-cols h3{font-family:var(--serif);font-size:20px;font-weight:500;margin-bottom:8px}
.rule-cols p,.rule-cols li{font-size:14px;line-height:1.95;color:var(--soft)}
.rule-cols ul{margin-top:8px}
.rule-cols li{padding-left:16px;position:relative}
.rule-cols li::before{content:"—";position:absolute;left:0;color:var(--gold)}
.rule-note{border:1px solid var(--line);background:rgba(255,255,255,.24);padding:18px 20px;font-size:13px;line-height:1.9;color:var(--soft);margin-top:22px}
.rule-note b{color:var(--ink)}

/* battlefield */
.battlefield{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:32px 0 12px}
.zone{border:1px solid var(--line);min-height:170px;padding:12px;position:relative;background:rgba(255,255,255,.18);display:flex;flex-direction:column;gap:8px;transition:.3s}
.zone.is-lit{background:rgba(166,124,61,.12);border-color:var(--gold)}
.zone .z-label{font-family:var(--latin);font-size:9px;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.zone .z-name{font-family:var(--serif);font-size:16px;color:var(--ink)}
.zone.is-edge{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.zone.is-edge .z-label{color:rgba(244,239,228,.45)}
.zone.is-edge .z-name{color:var(--paper)}
.zone.is-faith{background:rgba(158,59,59,.06);border-color:rgba(158,59,59,.34)}
.zone.is-edge.is-faith{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.zone .z-flag{margin-top:auto;font-family:var(--latin);font-size:9px;letter-spacing:.12em;color:var(--red)}
.zone .z-token{font-size:11px;line-height:1.5;border-left:2px solid var(--gold);padding:4px 0 4px 8px;color:var(--soft)}
.battlefield-caption{display:flex;justify-content:space-between;gap:16px;font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px}

/* demo */
.demo{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(280px,.65fr);gap:0;border:1px solid var(--line);margin-top:34px;background:rgba(255,255,255,.16)}
.demo-stage{padding:22px;border-right:1px solid var(--line);position:relative;min-height:340px}
.demo-stage .battlefield{margin:0}
.demo-stage .zone{min-height:230px}
.demo-token{border:1px solid var(--line-strong);background:var(--paper);padding:5px 7px;font-size:10px;line-height:1.35;transition:transform .5s,opacity .4s;opacity:.35;order:-1}
.demo-token.is-on{opacity:1}
.demo-token b{display:block;font-size:11px;font-weight:500}
.demo-token span{color:var(--muted);font-size:9px}
.demo-token.is-hero{border-color:var(--gold)}
.demo-token.is-enemy{border-color:var(--red);background:#f3e3dd}
.demo-panel{padding:26px;display:flex;flex-direction:column}
.demo-kicker{font-family:var(--latin);font-size:10px;letter-spacing:.2em;color:var(--gold)}
.demo-panel h3{font-family:var(--serif);font-size:26px;font-weight:500;margin:10px 0 10px;line-height:1.35}
.demo-panel p{font-size:13.5px;line-height:1.95;color:var(--soft);flex:1}
.demo-controls{display:flex;gap:8px;margin-top:18px}
.demo-controls .btn{padding:8px 12px;font-size:11px}
.demo-dots{display:flex;gap:6px;margin-top:16px}
.demo-dots i{width:18px;height:2px;background:var(--line-strong)}
.demo-dots i.is-on{background:var(--red)}

/* unit table */
.table{width:100%;border-collapse:collapse;margin-top:24px;font-size:13.5px}
.table th,.table td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.table th{font-family:var(--latin);font-size:10px;letter-spacing:.14em;color:var(--gold);font-weight:400;text-transform:uppercase;border-bottom-color:var(--line-strong)}
.table td:first-child{font-family:var(--serif);font-size:16px;color:var(--ink);white-space:nowrap}
.table tr:hover td{background:rgba(255,255,255,.3)}

/* keywords */
.keyword-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:24px}
.keyword-grid details{background:var(--paper);padding:0 20px}
.keyword-grid summary{cursor:pointer;padding:16px 0;list-style:none;display:flex;align-items:baseline;gap:10px}
.keyword-grid summary::-webkit-details-marker{display:none}
.keyword-grid summary::before{content:"+";font-family:var(--latin);color:var(--gold);font-size:14px;width:12px}
.keyword-grid details[open] summary::before{content:"−"}
.keyword-grid summary b{font-family:var(--serif);font-size:18px;font-weight:500}
.keyword-grid summary span{font-size:11px;color:var(--muted)}
.keyword-grid details p{font-size:13px;line-height:1.9;color:var(--soft);padding:0 0 16px 22px}
.keyword-grid details p em{font-style:normal;color:var(--red)}

/* filters + cards */
.filter-bar{position:sticky;top:var(--head);z-index:60;background:rgba(244,239,228,.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:16px 0;margin-bottom:20px}
.filter-row{display:flex; align-items:center;gap:16px;flex-wrap:wrap}
.filter-group{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.filter-group .fg-label{font-family:var(--latin);font-size:9px;letter-spacing:.16em;color:var(--muted);margin-right:2px}
.chip{border:1px solid var(--line);background:transparent;padding:5px 11px;font-size:11px;letter-spacing:.04em;cursor:pointer;transition:.2s;white-space:nowrap}
.chip:hover{border-color:var(--ink)}
.chip.is-on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.search{flex:1;min-width:160px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--line-strong);padding:4px 0}
.search input{flex:1;border:0;background:transparent;font:inherit;font-size:13px;color:var(--ink);outline:none;min-width:80px}
.search input::placeholder{color:var(--muted)}
.filter-count{font-family:var(--latin);font-size:11px;letter-spacing:.08em;color:var(--muted);white-space:nowrap}
.filter-count b{color:var(--ink);font-weight:500}
.card-group{margin-top:52px}
.card-group-head{display:flex;align-items:baseline;justify-content:space-between;border-bottom:1px solid var(--line-strong);padding-bottom:10px;margin-bottom:22px}
.card-group-head h2{font-family:var(--serif);font-size:28px;font-weight:500}
.card-group-head span{font-family:var(--latin);font-size:10px;letter-spacing:.14em;color:var(--muted)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(184px,1fr));gap:26px 20px}
.card-tile{display:block;min-width:0}
.card-tile img{width:100%;height:auto;border:1px solid var(--line);box-shadow:0 10px 24px rgba(23,28,38,.09);transition:transform .35s,box-shadow .35s}
.card-tile:hover img{transform:translateY(-5px);box-shadow:0 18px 34px rgba(23,28,38,.16)}
.card-tile h3{font-family:var(--serif);font-size:16.5px;font-weight:500;line-height:1.4;margin:10px 0 2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card-tile .tile-meta{display:flex;justify-content:space-between;gap:8px;font-size:9.5px;letter-spacing:.08em;color:var(--muted)}
.card-tile .tile-meta em{font-style:normal;color:var(--red)}
.empty-note{padding:60px 0;text-align:center;font-family:var(--serif);font-size:20px;color:var(--muted)}

/* card detail */
.card-page{padding:38px 0 96px}
.breadcrumb{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:11px;color:var(--muted);letter-spacing:.06em;margin-bottom:34px}
.breadcrumb a:hover{color:var(--ink)}
.breadcrumb em{font-style:normal;color:var(--ink)}
.breadcrumb span{opacity:.5}
.card-layout{display:grid;grid-template-columns:minmax(300px,430px) minmax(0,1fr);gap:64px;align-items:start}
.plate-wrap{position:sticky;top:calc(var(--head) + 28px)}
.plate-wrap > img{border:1px solid var(--line);box-shadow:0 20px 40px rgba(23,28,38,.12)}
.plate-caption{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid var(--line);padding:9px 0;font-family:var(--latin);font-size:9px;letter-spacing:.12em;color:var(--muted)}
.plate-note{font-size:10.5px;line-height:1.8;color:var(--muted);margin-top:10px}
.card-head .kicker{font-family:var(--latin);font-size:10px;letter-spacing:.2em;color:var(--gold);text-transform:uppercase}
.card-head h1{font-family:var(--serif);font-size:clamp(40px,5.4vw,64px);font-weight:500;line-height:1.16;letter-spacing:.04em;margin:10px 0 4px}
.card-role{font-size:12px;letter-spacing:.1em;color:var(--muted)}
.tag-row{display:flex;flex-wrap:wrap;gap:7px;margin-top:18px}
.tag{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);padding:3px 9px;font-size:10.5px;letter-spacing:.05em;color:var(--soft)}
.tag.is-faction{border-color:var(--line-strong);color:var(--ink)}
.tag.is-quality{color:var(--red);border-color:rgba(158,59,59,.35)}
.tag.is-cost{font-family:var(--latin);letter-spacing:.08em}
.card-text{margin:30px 0 0;padding:24px 28px;border-left:2px solid var(--red);background:rgba(255,255,255,.28);font-family:var(--serif);font-size:17px;line-height:2.05;color:var(--ink-2);white-space:pre-line}
.card-text .stamp{display:inline-block;font-family:var(--sans);font-size:9px;letter-spacing:.16em;color:var(--red);border:1px solid rgba(158,59,59,.4);padding:2px 6px;vertical-align:3px;margin-left:8px}
.quick-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:26px}
.quick-grid div{background:var(--paper);padding:12px 14px;min-width:0}
.quick-grid dt{font-size:9px;letter-spacing:.14em;color:var(--muted);text-transform:uppercase;font-family:var(--latin)}
.quick-grid dd{margin:4px 0 0;font-family:var(--serif);font-size:17px;line-height:1.4}
.quick-grid dd small{font-family:var(--sans);font-size:10px;color:var(--muted);display:block;letter-spacing:.04em}
.card-section{margin-top:46px}
.card-section > h2{font-family:var(--serif);font-size:22px;font-weight:500;border-bottom:1px solid var(--line-strong);padding-bottom:9px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:baseline}
.card-section > h2 span{font-family:var(--latin);font-size:9px;letter-spacing:.14em;color:var(--muted)}
.relation-row{display:grid;grid-template-columns:92px minmax(0,1fr);gap:18px;padding:13px 0;border-bottom:1px solid var(--line);align-items:start}
.rel-label{font-size:10px;letter-spacing:.1em;color:var(--gold);padding-top:3px;white-space:nowrap}
.rel-label.is-in{color:var(--blue)}
.rel-body a{font-family:var(--serif);font-size:17px;border-bottom:1px solid transparent}
.rel-body a:hover{border-bottom-color:var(--red)}
.rel-why{font-size:12px;line-height:1.8;color:var(--muted);margin-top:3px}
.owned-line{font-size:13px;line-height:1.9;color:var(--soft);margin-top:12px}
.owned-line b{color:var(--ink);font-weight:500}
.kw-list{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.kw{border:1px solid var(--line);padding:6px 10px;font-size:11px;line-height:1.6;color:var(--soft);max-width:100%}
.kw b{display:block;font-family:var(--serif);font-size:14px;font-weight:500;color:var(--ink)}
.note-block{margin-top:64px;padding:38px 42px 30px;background:var(--paper-2);border:1px solid var(--line);position:relative}
.note-block::before,.note-block::after{content:"";position:absolute;width:22px;height:22px;border:1px solid var(--red);opacity:.55}
.note-block::before{left:10px;top:10px;border-right:0;border-bottom:0}
.note-block::after{right:10px;bottom:10px;border-left:0;border-top:0}
.note-block .note-kicker{font-family:var(--latin);font-size:10px;letter-spacing:.24em;color:var(--red);text-transform:uppercase}
.note-block h2{font-family:var(--serif);font-size:30px;font-weight:500;letter-spacing:.08em;margin:6px 0 22px}
.note-block p{font-family:var(--serif);font-size:16px;line-height:2.05;color:var(--ink-2);text-indent:2em;margin-bottom:14px}
.note-block p:first-of-type::first-letter{font-size:1.35em;color:var(--red)}
.note-sign{text-align:right;font-size:11px;color:var(--muted);letter-spacing:.08em;margin-top:20px}
.card-pager{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:54px}
.card-pager a{background:var(--paper);padding:18px 20px;display:flex;flex-direction:column;gap:2px}
.card-pager a:last-child{text-align:right;align-items:flex-end}
.card-pager span{font-size:9px;letter-spacing:.16em;color:var(--muted)}
.card-pager b{font-family:var(--serif);font-size:18px;font-weight:500}

/* concept */
.plate-list{display:grid;gap:72px;margin-top:56px}
.plate-item{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(260px,.75fr);gap:42px;align-items:center}
.plate-item:nth-child(even) .plate-fig{order:2}
.plate-fig{margin:0}
.plate-fig button{border:0;background:transparent;padding:0;cursor:zoom-in;display:block;width:100%}
.plate-fig img{border:1px solid var(--line);box-shadow:0 18px 36px rgba(23,28,38,.1);width:100%}
.plate-fig figcaption{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid var(--line);padding:9px 0;font-size:10px;color:var(--muted);letter-spacing:.08em}
.plate-copy .num{font-family:var(--latin);font-size:10px;letter-spacing:.16em;color:var(--gold)}
.plate-copy h2{font-family:var(--serif);font-size:clamp(26px,3vw,38px);font-weight:500;margin:8px 0 4px;line-height:1.3}
.plate-copy .latin{font-size:9px;color:var(--muted);margin-bottom:14px;display:block}
.plate-copy p{font-size:14px;line-height:2;color:var(--soft)}
.plate-copy .cap{font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px;margin-top:14px}
.lightbox{border:0;padding:0;background:transparent;max-width:min(96vw,1400px);max-height:92vh}
.lightbox::backdrop{background:rgba(8,11,18,.86)}
.lightbox img{width:auto;height:auto;max-width:92vw;max-height:86vh;border:1px solid rgba(244,239,228,.3)}
.lightbox .lb-close{position:fixed;right:22px;top:18px;background:transparent;border:0;color:var(--paper);font-size:32px;cursor:pointer;line-height:1}

/* atlas */
.atlas-line{margin-top:64px;padding-top:30px;border-top:1px solid var(--line-strong)}
.atlas-head{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-bottom:8px}
.atlas-head h2{font-family:var(--serif);font-size:30px;font-weight:500}
.atlas-head .latin{font-size:9px;color:var(--muted)}
.atlas-intro{font-size:14px;line-height:1.95;color:var(--soft);max-width:70ch;margin-bottom:22px}
.chain{margin:18px 0}
.chain-caption{font-size:10px;letter-spacing:.14em;color:var(--gold);margin-bottom:8px}
.chain-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.node{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);padding:5px 9px;background:rgba(255,255,255,.26);transition:.2s}
.node:hover{border-color:var(--ink);background:var(--paper)}
.node img{width:30px;height:37px;border:1px solid var(--line)}
.node b{font-family:var(--serif);font-size:13px;font-weight:500;white-space:nowrap}
.node span{font-size:9px;color:var(--muted);white-space:nowrap}
.arrow{color:var(--gold);font-family:var(--latin);font-size:12px;padding:0 2px}
.cross-table{margin-top:24px;border-top:1px solid var(--line-strong)}
.cross-row{display:grid;grid-template-columns:1fr 90px 1fr;gap:18px;padding:16px 0;border-bottom:1px solid var(--line);align-items:center;font-size:13px}
.cross-row .cr-a,.cross-row .cr-b{font-family:var(--serif);font-size:16px}
.cross-row .cr-t{font-size:9px;letter-spacing:.12em;color:var(--gold);text-align:center}
.cross-row p{grid-column:1/-1;font-size:12px;line-height:1.8;color:var(--muted);margin-top:-6px}

/* novel */
.coming{padding:120px 0 96px;text-align:center;border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.coming::before{content:"未完";position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);font-family:var(--serif);font-size:clamp(140px,28vw,340px);color:rgba(23,28,38,.035);white-space:nowrap;pointer-events:none}
.coming .stamp{display:inline-block;border:1px solid var(--red);color:var(--red);font-size:11px;letter-spacing:.24em;padding:5px 14px;transform:rotate(-2deg);margin-bottom:24px}
.coming h1{font-family:var(--serif);font-weight:500;font-size:clamp(56px,10vw,124px);line-height:1.1;letter-spacing:.12em;position:relative}
.coming .lead{margin:22px auto 0;max-width:52ch;position:relative}
.plan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin-top:36px}
.plan-grid article{background:var(--paper);padding:26px}
.plan-grid b{font-family:var(--latin);font-size:10px;letter-spacing:.18em;color:var(--gold)}
.plan-grid h3{font-family:var(--serif);font-size:21px;font-weight:500;margin:8px 0}
.plan-grid p{font-size:13px;line-height:1.9;color:var(--soft)}

/* about */
.about-grid{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(260px,.75fr);gap:64px;padding:32px 0 20px}
.about-body p{font-size:14.5px;line-height:2;color:var(--soft);margin-bottom:16px;max-width:70ch}
.about-body h2{font-family:var(--serif);font-size:28px;font-weight:500;margin:36px 0 12px}
.side-note{border:1px solid var(--line);background:rgba(255,255,255,.24);padding:26px;align-self:start;position:sticky;top:calc(var(--head) + 28px)}
.side-note h3{font-family:var(--serif);font-size:19px;font-weight:500;margin-bottom:10px}
.side-note p,.side-note li{font-size:12px;line-height:1.9;color:var(--soft)}
.side-note li{padding:7px 0;border-bottom:1px solid var(--line)}
.side-note li:last-child{border-bottom:0}
.source-list li{padding:9px 0;border-bottom:1px solid var(--line);font-size:12px;color:var(--soft)}
.source-list b{color:var(--ink);font-weight:500}

/* 404 */
.err{padding:140px 0;text-align:center}
.err .code{font-family:var(--latin);font-size:clamp(90px,18vw,200px);line-height:1;color:var(--line-strong)}
.err h1{font-family:var(--serif);font-size:40px;font-weight:500;margin:12px 0}
.err p{color:var(--soft)}

/* footer */
.site-foot{background:var(--night);color:var(--paper);padding:58px 0 26px;margin-top:96px;position:relative;overflow:hidden}
.site-foot::after{content:"长歌";position:absolute;right:-10px;bottom:-70px;font-family:var(--serif);font-size:240px;color:rgba(244,239,228,.035);pointer-events:none;line-height:1}
.foot-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr;gap:48px;position:relative;z-index:2}
.foot-brand{font-family:var(--serif);font-size:26px;letter-spacing:.16em}
.foot-brand span{font-family:var(--latin);font-size:9px;letter-spacing:.28em;color:var(--gold-soft);margin-left:10px}
.foot-grid p{font-size:12px;line-height:1.9;color:rgba(244,239,228,.56);margin-top:12px;max-width:38ch}
.foot-grid h3{font-family:var(--latin);font-size:9px;letter-spacing:.2em;color:rgba(244,239,228,.45);margin-bottom:12px;font-weight:400;text-transform:uppercase}
.foot-links a{display:block;font-size:12px;color:rgba(244,239,228,.72);padding:4px 0}
.foot-links a:hover{color:var(--gold-soft)}
.foot-meta{font-size:11px;line-height:2;color:rgba(244,239,228,.5)}
.foot-bottom{display:flex;justify-content:space-between;gap:20px;border-top:1px solid rgba(244,239,228,.14);margin-top:40px;padding-top:16px;font-size:10px;letter-spacing:.08em;color:rgba(244,239,228,.38);position:relative;z-index:2}

/* reveal */
.js [data-reveal]{opacity:0;transform:translateY(16px);transition:opacity .8s ease,transform .8s ease}
.js [data-reveal].is-in{opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .js [data-reveal]{opacity:1;transform:none;transition:none}
  *{transition-duration:.01ms!important;animation-duration:.01ms!important}
}

/* responsive */
@media (max-width:1080px){
  .card-layout{gap:40px;grid-template-columns:minmax(260px,360px) minmax(0,1fr)}
  .cover-main{grid-template-columns:1fr;gap:26px}
  .cover-note{max-width:52ch}
  .chapter{grid-template-columns:150px minmax(0,1fr);gap:32px}
  .cast-card{grid-template-columns:84px minmax(0,1fr);padding:28px}
  .cast-sigil img{width:84px;height:84px}
  .about-grid{grid-template-columns:1fr;gap:36px}
  .side-note{position:static}
}
@media (max-width:860px){
  .nav{position:fixed;left:0;right:0;top:var(--head);background:var(--paper);border-bottom:1px solid var(--line);flex-direction:column;align-items:stretch;gap:0;padding:10px 32px 22px;transform:translateY(-12px);opacity:0;pointer-events:none;transition:.3s}
  .nav.is-open{transform:none;opacity:1;pointer-events:auto}
  .nav a{padding:11px 0;border-bottom:1px solid var(--line);font-size:14px}
  .nav-toggle{display:block}
  .triptych{grid-template-columns:1fr}
  .stat-row{grid-template-columns:1fr 1fr}
  .night-head{grid-template-columns:1fr;gap:20px}
  .plate-strip{grid-template-columns:1fr 1fr}
  .plate-strip a:nth-child(2){transform:none}
  .plate-strip a:nth-child(3){display:none}
  .game-cols{grid-template-columns:1fr}
  .law-grid{grid-template-columns:1fr}
  .org-grid{grid-template-columns:1fr}
  .place-grid{grid-template-columns:1fr 1fr}
  .cast-grid{grid-template-columns:1fr}
  .cast-filler{display:none}
  .question-list{grid-template-columns:1fr}
  .apocrypha{padding:40px 28px}
  .chapter{grid-template-columns:1fr;gap:20px;padding:52px 0}
  .chapter-side{position:static}
  .race-row{grid-template-columns:1fr;gap:8px}
  .rule-cols{grid-template-columns:1fr;gap:22px}
  .battlefield{grid-template-columns:repeat(5,minmax(110px,1fr));overflow-x:auto;padding-bottom:10px}
  .demo{grid-template-columns:1fr}
  .demo-stage{border-right:0;border-bottom:1px solid var(--line)}
  .demo-stage .battlefield{grid-template-columns:repeat(5,minmax(90px,1fr))}
  .keyword-grid{grid-template-columns:1fr}
  .card-layout{grid-template-columns:1fr;gap:36px}
  .plate-wrap{position:static;max-width:420px}
  .quick-grid{grid-template-columns:1fr 1fr}
  .plate-item{grid-template-columns:1fr;gap:24px}
  .plate-item:nth-child(even) .plate-fig{order:0}
  .plan-grid{grid-template-columns:1fr}
  .foot-grid{grid-template-columns:1fr;gap:28px}
  .card-section > h2{flex-direction:column;gap:2px}
}
@media (max-width:560px){
  .wrap{width:calc(100% - 36px)}
  .site-head .wrap{height:62px}
  :root{--head:62px}
  .brand-text{font-size:17px}
  .cover{min-height:88vh}
  .cover .wrap{padding-top:calc(var(--head) + 30px);padding-bottom:28px}
  .cover h1{font-size:clamp(64px,22vw,110px)}
  .cover-bottom{flex-direction:column;align-items:flex-start;gap:16px}
  .cover-stats{width:100%;justify-content:space-between;gap:12px}
  .cover-stats b{font-size:19px}
  .cover-scroll{display:none}
  .section{padding:64px 0}
  .section-head{grid-template-columns:1fr;gap:10px;margin-bottom:34px}
  .section-num{width:40px}
  .stat-row b{font-size:40px}
  .triptych article{min-height:0;padding:26px 22px}
  .plate-strip{grid-template-columns:1fr 1fr;gap:12px}
  .page-hero{padding:70px 0 44px}
  .page-hero .hero-latin{display:none}
  .place-grid{grid-template-columns:1fr}
  .cast-card{grid-template-columns:1fr;gap:16px}
  .cast-sigil img{width:76px;height:76px}
  .cast-head{flex-direction:column;align-items:flex-start}
  .card-grid{grid-template-columns:repeat(auto-fill,minmax(142px,1fr));gap:20px 12px}
  .card-tile h3{font-size:14px}
  .filter-row{gap:10px}
  .filter-group{gap:4px}
  .chip{padding:4px 8px;font-size:10px}
  .search{order:9;flex-basis:100%}
  .note-block{padding:28px 22px 22px}
  .note-block h2{font-size:24px}
  .relation-row{grid-template-columns:1fr;gap:4px}
  .card-pager{grid-template-columns:1fr}
  .card-pager a:last-child{text-align:left;align-items:flex-start;border-top:1px solid var(--line)}
  .cross-row{grid-template-columns:1fr;gap:2px}
  .cross-row .cr-t{text-align:left}
  .foot-bottom{flex-direction:column;gap:6px}
}

/* print */
@media print{
  body::before,.site-head,.site-foot,.card-pager,.demo-controls,.filter-bar{display:none!important}
  body{background:#fff;color:#000}
  .card-layout{grid-template-columns:1fr}
  .plate-wrap{position:static}
  a{text-decoration:none}
}
"""

JS = r"""
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
"""
