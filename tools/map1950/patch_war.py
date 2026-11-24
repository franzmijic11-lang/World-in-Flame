"""Adds the 'Ostschild War' playback mode to planner_1950.html (run after patch_planner.py)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
h = open(os.path.join(HERE, 'planner_1950.html'), encoding='utf-8').read()
WAR = json.load(open(os.path.join(HERE, 'war.json'), encoding='utf-8'))


def rep(a, b, n=1):
    global h
    assert h.count(a) == n, (a[:90], h.count(a))
    h = h.replace(a, b)


rep('.btn[aria-pressed="true"] {', '''/* the Ostschild war */
:root { --good: #3f7d4c; --bad: #a33a2a; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --good: #6dbb7c; --bad: #e0745f; } }
:root[data-theme="dark"] { --good: #6dbb7c; --bad: #e0745f; }
.wb { display: flex; flex-direction: column; gap: 4px; }
.wb-track { position: relative; height: 18px; border-radius: 3px; background: var(--bg); border: 1px solid var(--line); overflow: hidden; }
.wb-fill { position: absolute; top: 0; bottom: 0; transition: left .4s, width .4s, background .4s; }
.wb-zero { position: absolute; top: -2px; bottom: -2px; width: 2px; background: var(--ink); opacity: .6; }
.wb-mark { position: absolute; top: -3px; bottom: -3px; width: 3px; margin-left: -1px; background: var(--ink); transition: left .4s; }
.wb-scale { display: flex; justify-content: space-between; font-family: var(--f-mono); font-size: 11px; color: var(--muted); }
.wb-score { font-size: 15px; display: flex; gap: 8px; align-items: baseline; }
.wb-score b { font-family: var(--f-mono); font-size: 22px; font-variant-numeric: tabular-nums; }
.wb-delta { font-family: var(--f-mono); font-weight: 700; }
.wb-delta.up { color: var(--good); } .wb-delta.down { color: var(--bad); }
.warctl { display: grid; grid-template-columns: auto auto auto minmax(0, 1fr); gap: 6px; align-items: center; }
.warctl input[type=range] { width: 100%; min-width: 0; accent-color: var(--accent); }
.wartext { margin: 0; font-size: 14.5px; min-height: 3.2em; }
.warsides { display: flex; flex-wrap: wrap; gap: 4px; }
.warside { display: inline-flex; align-items: center; gap: 5px; border: 1px solid var(--line); border-radius: 12px; padding: 1px 8px 1px 5px; font-size: 13px; background: var(--bg); }
.warside i { width: 11px; height: 11px; border-radius: 2px; border: 1px solid var(--line); }
.warside.out { text-decoration: line-through; opacity: .6; }
.warlog { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 2px; max-height: 260px; overflow: auto; font-size: 13px; }
.warlog li { display: grid; grid-template-columns: 74px 40px minmax(0, 1fr); gap: 6px; padding: 3px 4px; border-radius: 3px; cursor: pointer; }
.warlog li:hover { background: var(--bg); }
.warlog li.now { background: var(--accent-soft); }
.warlog .dt, .warlog .dl { font-family: var(--f-mono); font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
.warlog .dl.up { color: var(--good); } .warlog .dl.down { color: var(--bad); }
.warlog .tx { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.btn[aria-pressed="true"] {''')

rep('<button id="v1950" type="button" aria-pressed="false">1950</button>',
    '<button id="v1950" type="button" aria-pressed="false">1950</button>\n        <button id="vWar" type="button" aria-pressed="false">Ostschild War</button>')
rep('<section class="panel" id="p1950" hidden>', '''<section class="panel" id="pWar" hidden>
      <h2>The First West Russian War <small id="warDate"></small></h2>
      <p class="hint">Imagined runs of the war from March 1952, scored by the mod's own rules: each city's points when the SME takes it, double back when the Ostschild retakes it, 40 for an SME home state (55 for Gorky), +20 a capitulation, -10 for 40 idle days.</p>
      <div class="row" role="group" aria-label="Which run of the war" id="warScens"></div>
      <div class="wb">
        <div class="wb-track" aria-hidden="true"><div class="wb-fill" id="wbFill"></div><div class="wb-zero" id="wbZero"></div><div class="wb-mark" id="wbMark"></div></div>
        <div class="wb-scale"><span>-100 SME collapses</span><span>0</span><span>+170 SME wins</span></div>
      </div>
      <div class="wb-score">War score <b id="wbScore">+5</b><span class="wb-delta" id="wbDelta"></span></div>
      <div class="warctl">
        <button class="btn" id="warPrev" type="button" aria-label="Previous step">&#9664;</button>
        <button class="btn primary" id="warPlay" type="button">Play</button>
        <button class="btn" id="warNext" type="button" aria-label="Next step">&#9654;</button>
        <input type="range" id="warRange" min="0" value="0" aria-label="War timeline">
      </div>
      <p class="wartext" id="warText"></p>
      <div class="warsides" id="warSides"></div>
      <div class="warsides" id="warGerman"></div>
      <div class="warsides" id="warUkraine"></div>
      <div class="warsides" id="warOstland"></div>
      <ol class="warlog" id="warLog"></ol>
    </section>
    <section class="panel" id="p1950" hidden>''')
rep('const OWNERS = MAP.owners;', 'const WAR = ' + json.dumps(WAR, ensure_ascii=False, separators=(',', ':')) + ';\nconst OWNERS = MAP.owners;')
rep('function fillOf(s) {\n', 'function fillOf(s) {\n  if (view === "war") return warFill(s.id);\n')
rep('function clickState(sid) {\n', 'function clickState(sid) {\n  if (view === "war") { selected = sid; render(); return; }\n')
rep('$("v1950").onclick = () => { view = "1950"; render(); };',
    '$("v1950").onclick = () => { view = "1950"; render(); };\n$("vWar").onclick = () => { const first = view !== "war"; view = "war"; render(); if (first) fitWar(); };')
rep('for (const [bid, v] of [["vPlan", "plan"], ["vToday", "today"], ["v1950", "1950"]])',
    'for (const [bid, v] of [["vPlan", "plan"], ["vToday", "today"], ["v1950", "1950"], ["vWar", "war"]])')
rep('  if (view === "1950") { b.textContent = "1950: click a country to select it. Shift-click picks several."; return; }',
    '  if (view === "war") { b.textContent = "The Ostschild War: play it, or step through it. Hatching marks occupied land."; return; }\n  if (view === "1950") { b.textContent = "1950: click a country to select it. Shift-click picks several."; return; }')
rep('renderBrush(); renderFactions(); renderDetail(); render1950();\n}', 'renderBrush(); renderFactions(); renderDetail(); render1950(); renderWar();\n}')
# outline50 reads owners through a swappable function
rep('const a = own50(e[0]), b = e[1] ? own50(e[1]) : null;', 'const a = ownFn(e[0]), b = e[1] ? ownFn(e[1]) : null;')
rep('function outline50(pred) {', 'let ownFn = own50;\nfunction outline50(pred) {')
# render1950 must not hide the shared border layer in war view
rep('  $("p1950").hidden = !on; gNat.style.display = on ? "" : "none"; g50L.style.display = on ? "" : "none";\n  gLabels.style.display = on ? "none" : "";\n  if (!on) return;',
    '''  $("p1950").hidden = !on; gNat.style.display = (on || view === "war") ? "" : "none"; g50L.style.display = on ? "" : "none";
  for (const e of [pGoldU, pGold, pSel]) e.style.display = on ? "" : "none";
  gLabels.style.display = on ? "none" : "";
  if (!on) return;
  if (ownFn !== own50) { ownFn = own50; pNat.setAttribute("d", outline50((a, b) => a !== b)); }''')

JS = r'''
// ---------------- the Ostschild war ----------------
let warStep = 0, warTimer = null, warOwn = {}, warCtrl = {}, warOut = new Set(), warDrawn = -1;
const defs = el("defs", {}, null);
let warScen = 0;
Object.assign(C50, WAR.countries);
function steps() { return WAR.scenarios[warScen].steps; }
function warCompute(n) {
  warOwn = {}; warCtrl = {}; warOut = new Set();
  for (const s of MAP.states) { warOwn[s.id] = own50(s.id); warCtrl[s.id] = warOwn[s.id]; }
  for (let i = 0; i <= n; i++) {
    const st = steps()[i];
    for (const [sid, t] of st.c) warCtrl[sid] = t;
    for (const [sid, t] of st.o) { warOwn[sid] = t; warCtrl[sid] = t; }
    for (const t of st.out) warOut.add(t);
    if (st.k === "lose") warOut.add("SME");
    if (st.k === "win") warOut.add("_won");
    if (st.k === "reunify") warOut.add("_reich");
  }
}
function hatch(a, b) {
  const id = "hx_" + a + "_" + b;
  if (!document.getElementById(id)) {
    if (!defs.isConnected) svg.prepend(defs);
    const p = el("pattern", { id, width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
    el("rect", { width: 6, height: 6, fill: color50(b) }, p);
    el("rect", { width: 3, height: 6, fill: color50(a) }, p);
  }
  return "url(#" + id + ")";
}
function warFill(sid) { const c = warCtrl[sid], o = warOwn[sid]; return c && c !== o ? hatch(c, o) : color50(o); }
function fitWar() {
  let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
  for (const s of MAP.states) {
    const o = own50(s.id);
    if (!(WAR.scenarios[warScen].focus || ["RKM", "RKK", "SME"]).includes(o)) continue;
    const b = pathEls[s.id].getBBox(); x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
  }
  const r = svg.clientWidth / Math.max(1, svg.clientHeight);
  let w = x1 - x0 + 30, hh = y1 - y0 + 30; if (w / hh > r) hh = w / r; else w = hh * r;
  vb = { x: (x0 + x1) / 2 - w / 2, y: (y0 + y1) / 2 - hh / 2, w, h: hh }; setVB();
}
function signed(n) { return (n > 0 ? "+" : n < 0 ? "−" : "±") + Math.abs(n); }
function renderWar() {
  const on = view === "war";
  $("pWar").hidden = !on;
  if (!on) { if (warTimer) { clearInterval(warTimer); warTimer = null; $("warPlay").textContent = "Play"; } return; }
  if (!gNat.isConnected && gStates.isConnected) { gStates.after(gNat); svg.append(g50L); }
  const N = steps().length - 1, st = steps()[warStep];
  const sb = $("warScens"); if (!sb.children.length) WAR.scenarios.forEach((sc, k) => { const b = document.createElement("button"); b.type = "button"; b.className = "btn"; b.textContent = sc.name; b.onclick = () => warPick(k); sb.append(b); });
  [...sb.children].forEach((b, k) => b.setAttribute("aria-pressed", String(warScen === k)));
  $("warRange").max = String(N); $("warRange").value = String(warStep);
  if (warDrawn !== warStep || ownFn === own50) {
    warCompute(warStep);
    for (const s of MAP.states) pathEls[s.id].style.fill = warFill(s.id);
    ownFn = (sid) => warOwn[sid];
    pNat.setAttribute("d", outline50((a, b) => a !== b));
    warDrawn = warStep;
  }
  const pct = (v) => (v + 100) / 270 * 100, z = pct(0), m = pct(st.sc);
  $("wbZero").style.left = z + "%"; $("wbMark").style.left = m + "%";
  const f = $("wbFill"); f.style.left = Math.min(z, m) + "%"; f.style.width = Math.abs(m - z) + "%"; f.style.background = st.sc >= 0 ? "var(--good)" : "var(--bad)";
  $("wbScore").textContent = signed(st.sc);
  const d = $("wbDelta"); d.textContent = st.dl ? signed(st.dl) : ""; d.className = "wb-delta " + (st.dl > 0 ? "up" : st.dl < 0 ? "down" : "");
  $("warDate").textContent = new Date(st.d + "T00:00:00Z").toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
  $("warText").textContent = st.t;
  const scen = WAR.scenarios[warScen], late = scen.late || {};
  const sides = scen.sides.filter((t) => !late[t] || warOut.has("_reich"));
  const rk = warOut.has("_rk");
  const re = (t) => warOut.has("_re_" + t) || (t === "RKU" && warOut.has("_rkback"));
  const gone = (t) => warOut.has(t) && !re(t);
  const sideNote = (t) => re(t) ? " — re-established" : gone(t) ? (t === "SME" ? " — collapsing" : (t === "RKM" || t === "RKK") && warOut.has("_won") ? " — annexed by the SME" : " — capitulated") : (rk && t !== "SME" && t !== "GER" ? " — a Reichskommissariat again" : (late[t] ? " — at war" : ""));
  $("warSides").innerHTML = sides.map((t) => `<span class="warside${gone(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t).replace(/^Reichskommissariat /, "RK ").replace(/ \(.*\)$/, ""))}${sideNote(t)}</span>`).join("");
  const gs = scen.gsides || [];
  $("warGerman").hidden = !gs.length || warOut.has("_reich");
  $("warGerman").innerHTML = gs.length ? '<span class="hint" style="width:100%">The German civil war</span>' + gs.map((t) => `<span class="warside${warOut.has(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}${warOut.has(t) ? " \u2014 gone" : ""}</span>`).join("") : "";
  const us = scen.usides || [];
  const urose = warOut.has("_ukr");
  $("warUkraine").hidden = !us.length || !urose;
  $("warUkraine").innerHTML = us.length ? '<span class="hint" style="width:100%">The Ukrainian rising (fights for the SME\'s score)</span>' + us.map((t) => `<span class="warside${warOut.has(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}${warOut.has(t) ? " \u2014 gone" : ""}</span>`).join("") : "";
  const os = scen.osides || [];
  const orose = warOut.has("_rko");
  const present = new Set(Object.values(warOwn));
  const oshow = os.filter((t) => present.has(t) || warOut.has(t));
  const onote = (t) => t === "FBR" && warOut.has("_bun") ? " \u2014 now the Baltic Union" : t === "EST" && warOut.has("_esw") ? " \u2014 now a Swedish supervised state" : warOut.has(t) ? " \u2014 gone" : "";
  $("warOstland").hidden = !os.length || !orose;
  $("warOstland").innerHTML = os.length ? '<span class="hint" style="width:100%">The Ostland rising (fights for the SME\'s score)</span>' + oshow.map((t) => `<span class="warside${warOut.has(t) || (t === "FBR" && warOut.has("_bun")) || (t === "EST" && warOut.has("_esw")) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}${onote(t)}</span>`).join("") : "";
  const log = $("warLog");
  log.innerHTML = steps().slice(0, warStep + 1).map((x, i) => `<li data-i="${i}" class="${i === warStep ? "now" : ""}"><span class="dt">${x.d}</span><span class="dl ${x.dl > 0 ? "up" : x.dl < 0 ? "down" : ""}">${x.dl ? signed(x.dl) : ""}</span><span class="tx">${esc50(x.t)}</span></li>`).reverse().join("");
  log.querySelectorAll("li").forEach((li) => li.onclick = () => { warStep = +li.dataset.i; render(); });
  $("warPlay").textContent = warTimer ? "Pause" : (warStep >= N ? "Replay" : "Play");
  $("warPrev").disabled = warStep <= 0; $("warNext").disabled = warStep >= N;
}
function warGo(n) { warStep = Math.max(0, Math.min(steps().length - 1, n)); render(); }
function warPick(k) { if (warTimer) { clearInterval(warTimer); warTimer = null; } warScen = k; warStep = 0; warDrawn = -1; render(); fitWar(); }

$("warPrev").onclick = () => warGo(warStep - 1);
$("warNext").onclick = () => warGo(warStep + 1);
$("warRange").oninput = () => warGo(+$("warRange").value);
$("warPlay").onclick = () => {
  if (warTimer) { clearInterval(warTimer); warTimer = null; render(); return; }
  if (warStep >= steps().length - 1) warStep = 0;
  warTimer = setInterval(() => { if (warStep >= steps().length - 1) { clearInterval(warTimer); warTimer = null; render(); return; } warGo(warStep + 1); }, 1400);
  render();
};

'''
rep('// ---------------- buttons ----------------', JS + '// ---------------- buttons ----------------')
# leaving war view restores the plain owners' fills via render(); make sure the 1950 view resets borders too
open(os.path.join(HERE, 'planner_war.html'), 'w', encoding='utf-8').write(h)
open(os.path.join(HERE, 'planner_war_check.js'), 'w', encoding='utf-8').write(h.split('<script>')[1].split('</script>')[0])
print('ok', len(h))
