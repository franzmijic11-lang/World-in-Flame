import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r'C:\Users\franz\.claude\projects\C--Program-Files--x86--Microsoft-Visual-Studio-18-BuildTools\de52f83b-b1b2-4bd5-bb23-a1c0652b49a5\tool-results\artifact-928cd84e-1794226332-ccd0.html'
h = open(SRC, encoding='utf-8').read()
# strip the publish skeleton: the authored page starts at <title>
h = h[h.index('<title>Siberian Collapse Planner</title>'):]
h = h[:h.rindex('</body></html>')] if h.rstrip().endswith('</body></html>') else h


def rep(a, b, n=1):
    global h
    assert h.count(a) == n, (a[:80], h.count(a))
    h = h.replace(a, b)


states = json.load(open(os.path.join(HERE, 'states.json'), encoding='utf-8'))
world = json.load(open(os.path.join(HERE, 'world.json'), encoding='utf-8'))
W1950 = {
    'own': {str(s['id']): s['o'] for s in states},
    'why': {str(s['id']): s['why'] for s in states if s['why'] and s['o'] != s['o36']},
    'countries': {t: {k: v for k, v in c.items() if k in ('name', 'color', 'overlord', 'tree')} for t, c in world['countries'].items()},
}

# ---- CSS
rep('.lbl.world { font-weight: 400; }', '''.lbl.world { font-weight: 400; }
/* the 1950 world */
:root { --gold: #c08a14; --gold-halo: rgba(50, 30, 0, .55); }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --gold: #e8b53a; --gold-halo: rgba(0, 0, 0, .8); } }
:root[data-theme="dark"] { --gold: #e8b53a; --gold-halo: rgba(0, 0, 0, .8); }
.nat50 { fill: none; stroke: var(--ink); stroke-opacity: .7; stroke-width: 1.1; vector-effect: non-scaling-stroke; pointer-events: none; }
.gold50u { fill: none; stroke: var(--gold-halo); stroke-width: 4.4; vector-effect: non-scaling-stroke; pointer-events: none; stroke-linejoin: round; }
.gold50 { fill: none; stroke: var(--gold); stroke-width: 2.4; vector-effect: non-scaling-stroke; pointer-events: none; stroke-linejoin: round; }
.sel50 { fill: none; stroke: var(--accent); stroke-width: 2; stroke-dasharray: 5 3; vector-effect: non-scaling-stroke; pointer-events: none; }
.lbl50 { font-family: var(--f-display); font-weight: 700; text-anchor: middle; fill: var(--ink); paint-order: stroke; stroke: var(--halo); stroke-width: 2.4px; stroke-linejoin: round; pointer-events: none; }
svg#map.nosib .lbl50 { display: none; }
.g50list { display: flex; flex-direction: column; gap: 2px; max-height: 300px; overflow: auto; }
.g50item { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: 8px; align-items: center; padding: 4px 6px; border: 0; border-radius: 3px; background: none; text-align: left; cursor: pointer; width: 100%; }
.g50item:hover, .g50item.on { background: var(--bg); }
.g50item.on { box-shadow: inset 3px 0 0 var(--accent); }
.g50item i, .g50chip i { width: 12px; height: 12px; border-radius: 2px; display: inline-block; flex: none; border: 1px solid var(--line); }
.g50item .tg { font-family: var(--f-mono); font-size: 11.5px; color: var(--muted); }
.g50item .nm { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.g50chips { display: flex; flex-wrap: wrap; gap: 4px; }
.g50chip { display: inline-flex; align-items: center; gap: 5px; border: 1px solid var(--line); border-radius: 12px; padding: 1px 8px 1px 5px; font-size: 13px; background: var(--bg); cursor: pointer; }
.g50tree { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; }
.g50tree::before { content: ""; width: 18px; border-top: 3px solid var(--gold); box-shadow: 0 0 0 1px var(--gold-halo); }
.btn[aria-pressed="true"] { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); font-weight: 700; }''')

# ---- markup
rep('<button id="vToday" type="button" aria-pressed="false">Today\'s borders</button>',
    '<button id="vToday" type="button" aria-pressed="false">Today\'s borders</button>\n        <button id="v1950" type="button" aria-pressed="false">1950</button>')
rep('<section class="panel" id="detail"></section>', '''<section class="panel" id="p1950" hidden>
      <h2>The world in 1950 <small id="g50Count"></small></h2>
      <p class="hint">One possible 1950 after a German and Japanese victory, from the mod's own peace deals. Gold borders mark countries with a post-war focus tree. Click a country to select it; Shift-click or Multi-select picks several.</p>
      <div id="sel50"></div>
      <div class="row">
        <button class="btn primary" id="hl50" type="button" disabled>Highlight selected</button>
        <button class="btn" id="clr50" type="button" disabled>Clear selection</button>
        <button class="btn" id="multi50" type="button" aria-pressed="false">Multi-select</button>
      </div>
      <div class="g50list" id="g50List"></div>
      <div class="row">
        <button class="btn" id="reset50" type="button">Only focus-tree countries</button>
        <button class="btn" id="none50" type="button">Remove all gold</button>
      </div>
    </section>
    <section class="panel" id="detail"></section>''')

# ---- data
rep('const OWNERS = MAP.owners;', 'const W1950 = ' + json.dumps(W1950, ensure_ascii=False, separators=(',', ':')) + ';\nconst OWNERS = MAP.owners;')

# ---- logic hooks
rep('return { factions: Array.isArray(p.factions) ? p.factions : [], assign: p.assign || {}, notes: p.notes || {}, updatedAt: p.updatedAt || 0 };',
    'return { factions: Array.isArray(p.factions) ? p.factions : [], assign: p.assign || {}, notes: p.notes || {}, gold: Array.isArray(p.gold) ? p.gold : null, updatedAt: p.updatedAt || 0 };')
rep('function fillOf(s) {\n', 'function fillOf(s) {\n  if (view === "1950") return color50(own50(s.id));\n')
rep('function clickState(sid) {\n', '''function clickState(sid) {
  if (view === "1950") {
    selected = sid; const t = own50(sid);
    if (multi50 || shift50) { sel50.has(t) ? sel50.delete(t) : sel50.add(t); }
    else if (sel50.size === 1 && sel50.has(t)) sel50.clear(); else { sel50.clear(); sel50.add(t); }
    render(); return;
  }
''')
rep('$("vToday").onclick = () => { view = "today"; render(); };',
    '$("vToday").onclick = () => { view = "today"; render(); };\n$("v1950").onclick = () => { view = "1950"; render(); };')
rep('  seg("vPlan", "vToday", view === "plan"); seg("mPaint", "mLook", mode === "paint");',
    '  for (const [bid, v] of [["vPlan", "plan"], ["vToday", "today"], ["v1950", "1950"]]) $(bid).setAttribute("aria-pressed", String(view === v));\n  seg("mPaint", "mLook", mode === "paint");')
rep('  renderBrush(); renderFactions(); renderDetail();\n}', '  renderBrush(); renderFactions(); renderDetail(); render1950();\n}')
rep('  if (view === "today") { b.textContent = "Today\'s borders. Switch to Your plan to paint."; return; }',
    '  if (view === "1950") { b.textContent = "1950: click a country to select it. Shift-click picks several."; return; }\n  if (view === "today") { b.textContent = "Today\'s borders. Switch to Your plan to paint."; return; }')
rep('  row("Held today by", ow);\n', '''  row("Held today by", ow);
  if (view === "1950") {
    const o5 = own50(s.id), w5 = document.createElement("span"); w5.className = "owner";
    const i5 = document.createElement("i"); i5.style.background = color50(o5); w5.append(i5, document.createTextNode(name50(o5)));
    row("In 1950", w5);
    if (W1950.why[s.id]) row("Why", W1950.why[s.id]);
  }
''')

JS = r'''
// ---------------- the 1950 world ----------------
const C50 = W1950.countries;
function own50(sid) { return W1950.own[sid] || byId[sid].owner; }
function name50(t) { return (C50[t] && C50[t].name) || (OWNERS[t] && OWNERS[t].name) || t; }
function color50(t) { return (C50[t] && C50[t].color) || (OWNERS[t] && OWNERS[t].color) || "#9a9a9a"; }
function treeTags() { return Object.keys(C50).filter((t) => C50[t].tree); }
function gold50() { return new Set(Array.isArray(plan.gold) ? plan.gold : treeTags()); }
const sel50 = new Set(); let multi50 = false, shift50 = false;
svg.addEventListener("pointerdown", (ev) => { shift50 = ev.shiftKey || ev.ctrlKey || ev.metaKey; }, true);

// Every state outline is cut into unit grid edges; a country border is an edge whose
// two sides have different 1950 owners.
const EW = (MAP.w + 1) * 2, edges = new Map();
function addEdge(k, id) { const e = edges.get(k); if (!e) edges.set(k, [id, 0]); else if (e[0] !== id && !e[1]) e[1] = id; }
for (const s of MAP.states) {
  const tok = s.path.match(/[MmHhVvZz]|-?\d+(?:\.\d+)?/g); let x = 0, y = 0, i = 0, cmd = "";
  while (i < tok.length) {
    const t = tok[i];
    if (/[A-Za-z]/.test(t)) { cmd = t; i++; if (cmd === "z" || cmd === "Z") continue; }
    if (cmd === "M") { x = +tok[i]; y = +tok[i + 1]; i += 2; cmd = "L"; continue; }
    const d = +tok[i]; i++;
    if (cmd === "h") { const a = Math.min(x, x + d), b = Math.max(x, x + d); for (let k = a; k < b; k++) addEdge(k * 2 + y * EW, s.id); x += d; }
    else if (cmd === "v") { const a = Math.min(y, y + d), b = Math.max(y, y + d); for (let k = a; k < b; k++) addEdge(x * 2 + 1 + k * EW, s.id); y += d; }
  }
}
function outline50(pred) {
  const hs = new Map(), vs = new Map();
  for (const [k, e] of edges) {
    const a = own50(e[0]), b = e[1] ? own50(e[1]) : null;
    if (!pred(a, b)) continue;
    const row = Math.floor(k / EW), r = k - row * EW, col = r >> 1;
    if ((r & 1) === 0) { if (!hs.has(row)) hs.set(row, []); hs.get(row).push(col); }
    else { if (!vs.has(col)) vs.set(col, []); vs.get(col).push(row); }
  }
  let d = "";
  const runs = (m, horiz) => {
    for (const [c, list] of m) {
      list.sort((p, q) => p - q);
      let s = list[0], p = list[0];
      for (let i = 1; i <= list.length; i++) {
        if (i < list.length && list[i] === p + 1) { p = list[i]; continue; }
        d += horiz ? `M${s} ${c}h${p + 1 - s}` : `M${c} ${s}v${p + 1 - s}`;
        if (i < list.length) s = p = list[i];
      }
    }
  };
  runs(hs, true); runs(vs, false);
  return d;
}
const gNat = el("g", {}, null), pNat = el("path", { class: "nat50" }, gNat), pGoldU = el("path", { class: "gold50u" }, gNat),
  pGold = el("path", { class: "gold50" }, gNat), pSel = el("path", { class: "sel50" }, gNat), g50L = el("g", {}, null);
let natDone = false, lastKey = null;
function labels50() {
  const by = {};
  for (const s of MAP.states) (by[own50(s.id)] = by[own50(s.id)] || []).push(s);
  for (const t in by) {
    const list = by[t], big = list.reduce((a, b) => (b.cells > a.cells ? b : a));
    let sx = 0, sy = 0, sw = 0;
    for (const s of list) { if (Math.hypot(s.lp[0] - big.lp[0], s.lp[1] - big.lp[1]) > 140) continue; sx += s.lp[0] * s.cells; sy += s.lp[1] * s.cells; sw += s.cells; }
    if (sw < 150) continue;
    const txt = el("text", { x: (sx / sw).toFixed(1), y: (sy / sw).toFixed(1), class: "lbl50", "font-size": Math.max(5, Math.min(24, Math.sqrt(sw) / 7)).toFixed(1) }, g50L);
    txt.textContent = name50(t).replace(/^Reichskommissariat /, "RK ").replace(/ \(.*\)$/, "");
  }
}
function esc50(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
function render1950() {
  const on = view === "1950";
  if (!gNat.isConnected && gStates.isConnected) { gStates.after(gNat); svg.append(g50L); }
  $("p1950").hidden = !on; gNat.style.display = on ? "" : "none"; g50L.style.display = on ? "" : "none";
  gLabels.style.display = on ? "none" : "";
  if (!on) return;
  if (!natDone) { natDone = true; pNat.setAttribute("d", outline50((a, b) => a !== b)); labels50(); }
  const gold = gold50();
  const key = [...gold].sort().join() + "|" + [...sel50].sort().join();
  if (key !== lastKey) {
    lastKey = key;
    const g = gold.size ? outline50((a, b) => a !== b && (gold.has(a) || gold.has(b))) : "";
    pGoldU.setAttribute("d", g); pGold.setAttribute("d", g);
    pSel.setAttribute("d", sel50.size ? outline50((a, b) => a !== b && (sel50.has(a) || sel50.has(b))) : "");
  }
  const box = $("sel50");
  if (!sel50.size) box.innerHTML = '<p class="hint">Nothing selected.</p>';
  else if (sel50.size > 1) {
    box.innerHTML = '<div class="g50chips">' + [...sel50].map((t) => `<span class="g50chip" data-t="${t}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}</span>`).join("") + "</div>";
    box.querySelectorAll(".g50chip").forEach((c) => c.onclick = () => { sel50.delete(c.dataset.t); render(); });
  } else {
    const t = [...sel50][0], c = C50[t] || {};
    const n = MAP.states.filter((s) => own50(s.id) === t).length;
    box.innerHTML = `<dl><dt>Country</dt><dd><span class="owner"><i style="background:${color50(t)}"></i>${esc50(name50(t))}</span></dd><dt>Tag</dt><dd>${t}</dd><dt>States</dt><dd>${n}</dd>`
      + (c.overlord ? `<dt>Subject of</dt><dd>${esc50(name50(c.overlord))}</dd>` : "") + `<dt>Border</dt><dd>${gold.has(t) ? "Gold" : "Plain"}</dd></dl>`
      + (c.tree ? `<span class="g50tree">Post-war tree: ${esc50(c.tree)}</span>` : "");
  }
  const all = sel50.size && [...sel50].every((t) => gold.has(t));
  $("hl50").disabled = !sel50.size; $("clr50").disabled = !sel50.size;
  $("hl50").textContent = all ? "Unhighlight selected" : "Highlight selected";
  $("multi50").setAttribute("aria-pressed", String(multi50));
  const tags = [...gold].filter((t) => C50[t]).sort((a, b) => name50(a).localeCompare(name50(b)));
  $("g50Count").textContent = tags.length + " gold";
  $("g50List").innerHTML = tags.map((t) => `<button class="g50item${sel50.has(t) ? " on" : ""}" type="button" data-t="${t}"><i style="background:${color50(t)}"></i><span class="nm">${esc50(name50(t))}</span><span class="tg">${t}</span></button>`).join("")
    || '<p class="hint">No gold borders. Select countries and press Highlight.</p>';
  $("g50List").querySelectorAll(".g50item").forEach((b) => b.onclick = () => { const t = b.dataset.t; if (multi50) { sel50.has(t) ? sel50.delete(t) : sel50.add(t); } else { sel50.clear(); sel50.add(t); } render(); });
}
function setGold(set) { plan.gold = [...set]; save(); render(); }
$("hl50").onclick = () => { const g = gold50(), all = [...sel50].every((t) => g.has(t)); sel50.forEach((t) => all ? g.delete(t) : g.add(t)); setGold(g); };
$("clr50").onclick = () => { sel50.clear(); render(); };
$("multi50").onclick = () => { multi50 = !multi50; render(); };
$("reset50").onclick = () => { plan.gold = null; save(); render(); };
$("none50").onclick = () => setGold(new Set());

'''
rep('// ---------------- buttons ----------------', JS + '// ---------------- buttons ----------------')
open(os.path.join(HERE, 'planner_1950.html'), 'w', encoding='utf-8').write(h)
js = h.split('<script>')[1].split('</script>')[0]
open(os.path.join(HERE, 'planner_check.js'), 'w', encoding='utf-8').write(js)
print('ok', len(h))
