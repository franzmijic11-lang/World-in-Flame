"""Move provinces between states, and carry everything that indexes them.

    python tools/move_provinces.py 4780:571 10600:571          # dry run
    python tools/move_provinces.py 4780:571 10600:571 --apply   # write it

Each argument is PROVINCE:TARGET_STATE.

A province is not just a member of a state. Six other things point at it, and
every one of them has to follow it or the game breaks - usually at map init,
with an empty error.log and no crash dump:

  1. history/states/            the provinces={} list of both states
  2. map/strategicregions/      the air zone. A state must lie wholly inside
                                ONE region; this is engine-enforced, and a
                                state straddling two regions crashes during
                                gamestate construction
  3. victory_points             a VP names a province, and lives in the state
                                file - it has to move to the new state's file
  4. buildings={ <prov> = {} }  province-keyed building entries in the state
                                file, which are addressed by province id
  5. map/buildings.txt          rocket_site_spawn, the naval slots, air_base
                                and radar_station are PROVINCE-level buildings.
                                If one ends up on ground its declaring state no
                                longer owns, the game dies ~1s after you press
                                Start - confirmed in game, twice
  6. state_category etc.        untouched - listed here so it is clear it was
                                considered and is genuinely state-level

(5) is the one with no obvious fix, and the reason a lot of moves look
randomly cursed. The way round it: do NOT rewrite the entry's state id to
follow the ground - that gives some states two of a singleton slot and you get
"Failed to load the map". Instead keep the state id and move the entry's
COORDINATES to another province the state still owns. The engine validates
per-state slot counts, not whether a spawn point lies inside its own state
(vanilla itself ships 10 such mismatches), so counts stay exactly vanilla and
the building simply stands somewhere else in the same state.

Relocation coordinates are never invented. They are copied wholesale from an
existing non-blocking entry in the destination province - a real point on real
ground that the game already accepts. 10154 of the 10272 land provinces carry
such an anchor. naval_base_spawn additionally needs an adjacent sea province,
which is read off provinces.bmp rather than guessed.

Refuses, rather than guessing, when:
  * the declaring state has no other province to put the spawn in
  * a naval slot has nowhere coastal to go
  * a move would empty a state, or a province is already in the target

Edit VANILLA and MOD below if the game ever moves.
"""

import os, re, sys, csv, glob, io, shutil, collections

VANILLA = r"D:\Steam\steamapps\common\Hearts of Iron IV"
MOD     = r"C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen"

# Province-level buildings: they stand at a spot on the map, so the spawn point
# marks where the building physically is. If one ends up on ground its declaring
# state no longer owns, the game dies about a second after you press Start.
#
# air_base and radar_station were added 2026-08-31 after a confirmed in-game
# crash: province 9122 carried BOTH of Yaroslavl's, and moving it to Vologda
# killed the game. The original bisect never moved a province hosting one, so
# they sat on neither the blocking list nor the known-harmless list, and were
# wrongly assumed safe. Do not assume again - a type absent from BOTH lists is
# untested, not safe.
#
# Known harmless, verified by displacement: arms_factory, industrial_complex,
# fuel_silo, synthetic_refinery, stronghold_network, dam_spawn,
# anti_air_building, bunker, supply_node, special_project_facility_spawn.
BLOCKING = ("rocket_site_spawn", "naval_base_spawn", "naval_headquarters",
            "naval_supply_hub", "air_base", "radar_station")
NEEDS_SEA = ("naval_base_spawn",)
NEEDS_COAST = ("naval_base_spawn", "naval_headquarters", "naval_supply_hub")


# --------------------------------------------------------------------------
# reading the world the way the game does: vanilla first, mod wins by FILENAME
# --------------------------------------------------------------------------

def effective(subdir):
    out = {}
    for f in glob.glob(os.path.join(VANILLA, subdir, "*.txt")):
        out[os.path.basename(f)] = f
    for f in glob.glob(os.path.join(MOD, subdir, "*.txt")):
        out[os.path.basename(f)] = f
    return out


def read(path):
    raw = open(path, "rb").read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    return raw.decode("utf-8-sig", "replace"), bom


def write(path, text, bom):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode("utf-8")
    open(path, "wb").write((b"\xef\xbb\xbf" if bom else b"") + data)


def decomment(t):
    return re.sub(r"#[^\n]*", "", t)


class World(object):
    def __init__(self):
        self.state_src, self.state_txt = {}, {}      # sid -> path, text
        self.state_bom, self.state_file = {}, {}
        self.prov2state = {}
        for fn, path in effective("history/states").items():
            t, bom = read(path)
            m = re.search(r"\bid\s*=\s*(\d+)", decomment(t))
            if not m:
                continue
            sid = int(m.group(1))
            self.state_src[sid], self.state_txt[sid] = path, t
            self.state_bom[sid], self.state_file[sid] = bom, fn
            for p in self.provinces_of(sid):
                self.prov2state[p] = sid

        self.reg_src, self.reg_txt, self.reg_bom, self.reg_file = {}, {}, {}, {}
        self.prov2region = {}
        for fn, path in effective("map/strategicregions").items():
            t, bom = read(path)
            m = re.search(r"\bid\s*=\s*(\d+)", decomment(t))
            if not m:
                continue
            rid = int(m.group(1))
            self.reg_src[rid], self.reg_txt[rid] = path, t
            self.reg_bom[rid], self.reg_file[rid] = bom, fn
            for p in self.region_provinces(rid):
                self.prov2region[p] = rid

        # definition.csv: colour -> id, plus type and coastal flag
        self.by_rgb, self.ptype, self.coastal = {}, {}, set()
        with open(os.path.join(VANILLA, "map", "definition.csv"), encoding="latin-1") as fh:
            for row in csv.reader(fh, delimiter=";"):
                if len(row) < 8 or not row[0].isdigit():
                    continue
                pid = int(row[0])
                self.by_rgb[(int(row[1]), int(row[2]), int(row[3]))] = pid
                self.ptype[pid] = row[4]
                if row[5] == "true":
                    self.coastal.add(pid)

        self.loc = {}
        for d in (os.path.join(VANILLA, "localisation", "english"),
                  os.path.join(MOD, "localisation", "english")):
            for f in glob.glob(os.path.join(d, "*.yml")):
                t = io.open(f, encoding="utf-8-sig", errors="replace").read()
                for k, v in re.findall(r'^\s*([\w.@\[\]-]+):\d*\s+"(.*)"\s*$', t, re.M):
                    self.loc[k] = v

        self._bmp = None

    # ---- state file accessors --------------------------------------------
    def provinces_of(self, sid):
        m = re.search(r"provinces\s*=\s*\{([^}]*)\}", decomment(self.state_txt[sid]))
        return [int(x) for x in re.findall(r"\d+", m.group(1))] if m else []

    def region_provinces(self, rid):
        m = re.search(r"provinces\s*=\s*\{([^}]*)\}", decomment(self.reg_txt[rid]))
        return [int(x) for x in re.findall(r"\d+", m.group(1))] if m else []

    def sname(self, sid):
        return self.loc.get("STATE_%d" % sid, "state %d" % sid)

    def pname(self, pid):
        return self.loc.get("VICTORY_POINTS_%d" % pid, "")

    # ---- provinces.bmp ----------------------------------------------------
    def bmp(self):
        if self._bmp is None:
            raw = open(os.path.join(VANILLA, "map", "provinces.bmp"), "rb").read()
            off = int.from_bytes(raw[10:14], "little")
            w = int.from_bytes(raw[18:22], "little")
            h = int.from_bytes(raw[22:26], "little")
            assert int.from_bytes(raw[28:30], "little") == 24 and (w * 3) % 4 == 0
            self._bmp = (raw, off, w, h, w * 3)
        return self._bmp

    def prov_at(self, x, z):
        raw, off, w, h, stride = self.bmp()
        c, r = int(x), int(z)
        if not (0 <= c < w and 0 <= r < h):
            return None
        p = off + r * stride + c * 3
        return self.by_rgb.get((raw[p + 2], raw[p + 1], raw[p]))

    def sea_neighbours(self):
        """province -> a set of adjacent sea province ids (one full bitmap pass)."""
        raw, off, w, h, stride = self.bmp()
        adj = collections.defaultdict(set)
        rgb = self.by_rgb.get
        for r in range(h):
            base = off + r * stride
            nbase = base + stride if r + 1 < h else None
            prev = None
            for c in range(w):
                p = base + c * 3
                a = rgb((raw[p + 2], raw[p + 1], raw[p]))
                if prev is not None and a != prev:
                    adj[a].add(prev); adj[prev].add(a)
                prev = a
                if nbase is not None:
                    q = nbase + c * 3
                    b = rgb((raw[q + 2], raw[q + 1], raw[q]))
                    if b != a:
                        adj[a].add(b); adj[b].add(a)
        return {k: {p for p in v if self.ptype.get(p) == "sea"} for k, v in adj.items()}


# --------------------------------------------------------------------------
# buildings.txt
# --------------------------------------------------------------------------

class Buildings(object):
    def __init__(self, world):
        src = os.path.join(MOD, "map", "buildings.txt")
        self.overridden = os.path.exists(src)
        if not self.overridden:
            src = os.path.join(VANILLA, "map", "buildings.txt")
        self.lines = io.open(src, encoding="latin-1").read().split("\n")
        self.rows = {}                                    # index -> parsed fields
        self.by_prov = collections.defaultdict(list)      # province -> [index]
        for i, line in enumerate(self.lines):
            f = line.rstrip("\r").split(";")
            if len(f) < 7 or not f[0].isdigit():
                continue
            pid = world.prov_at(float(f[2]), float(f[4]))
            self.rows[i] = f
            self.by_prov[pid].append(i)
        self.dirty = False

    def anchors(self, pid):
        """entries in this province that are safe to copy a ground point from"""
        return [i for i in self.by_prov.get(pid, []) if self.rows[i][1] not in BLOCKING]

    def blocking_in(self, pid):
        return [i for i in self.by_prov.get(pid, []) if self.rows[i][1] in BLOCKING]

    def relocate(self, idx, x, y, z, sea=None):
        f = self.rows[idx]
        f[2], f[3], f[4] = x, y, z
        if sea is not None:
            f[6] = sea
        self.lines[idx] = ";".join(f)
        self.dirty = True

    def counts_by_state(self):
        c = collections.Counter()
        for f in self.rows.values():
            c[(int(f[0]), f[1])] += 1
        return c

    def save(self):
        path = os.path.join(MOD, "map", "buildings.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="latin-1", newline="").write("\n".join(self.lines))
        return path


# --------------------------------------------------------------------------
# editing state and region text
# --------------------------------------------------------------------------

def set_province_list(text, provs):
    provs = sorted(set(provs))
    body = " ".join(str(p) for p in provs)
    def rep(m):
        return m.group(1) + "{\n\t\t" + body + " \n\t}"
    new, n = re.subn(r"(provinces\s*=\s*)\{[^}]*\}", rep, text, count=1)
    assert n == 1, "no provinces={} block"
    return new


def pull_victory_point(text, pid):
    """remove `pid value` from victory_points, return (text, value or None)"""
    m = re.search(r"(victory_points\s*=\s*\{)([^}]*)(\})", text)
    if not m:
        return text, None
    nums = re.findall(r"\d+", m.group(2))
    pairs = [(int(nums[i]), int(nums[i + 1])) for i in range(0, len(nums) - 1, 2)]
    keep = [p for p in pairs if p[0] != pid]
    if len(keep) == len(pairs):
        return text, None
    val = [p[1] for p in pairs if p[0] == pid][0]
    if keep:
        body = "".join("\n\t\t\t%d %d" % p for p in keep) + "\n\t\t"
        new = m.group(1) + body + m.group(3)
    else:
        new = ""                                    # drop an emptied block
    return text[:m.start()] + new + text[m.end():], val


def push_victory_point(text, pid, val):
    m = re.search(r"(victory_points\s*=\s*\{)([^}]*)(\})", text)
    if m:
        body = m.group(2).rstrip()
        return text[:m.start()] + m.group(1) + body + "\n\t\t\t%d %d\n\t\t" % (pid, val) + m.group(3) + text[m.end():]
    m = re.search(r"(history\s*=\s*\{)", text)
    assert m, "no history={} block to add victory_points to"
    ins = "\n\t\tvictory_points = {\n\t\t\t%d %d\n\t\t}" % (pid, val)
    return text[:m.end()] + ins + text[m.end():]


def pull_province_building(text, pid):
    """remove `<pid> = { ... }` from buildings={}, return (text, snippet or None)"""
    m = re.search(r"buildings\s*=\s*\{", text)
    if not m:
        return text, None
    b = re.search(r"(\n\s*%d\s*=\s*\{[^}]*\})" % pid, text[m.end():])
    if not b:
        return text, None
    s, e = m.end() + b.start(1), m.end() + b.end(1)
    return text[:s] + text[e:], b.group(1).strip()


def push_province_building(text, snippet):
    m = re.search(r"buildings\s*=\s*\{", text)
    assert m, "no buildings={} block to add a province building to"
    return text[:m.end()] + "\n\t\t\t" + snippet + text[m.end():]


# --------------------------------------------------------------------------

def main(argv):
    apply_ = "--apply" in argv
    moves = {}
    for a in argv:
        if a.startswith("--"):
            continue
        if ":" not in a:
            sys.exit("bad argument %r - want PROVINCE:STATE" % a)
        p, s = a.split(":", 1)
        moves[int(p)] = int(s)
    if not moves:
        sys.exit(__doc__)

    w = World()
    b = Buildings(w)
    before_counts = b.counts_by_state()
    plan, problems = [], []

    for pid, dst in sorted(moves.items()):
        if pid not in w.prov2state:
            problems.append("province %d is in no state" % pid); continue
        src = w.prov2state[pid]
        if src == dst:
            problems.append("province %d is already in %s" % (pid, w.sname(dst))); continue
        if dst not in w.state_txt:
            problems.append("no state %d" % dst); continue
        if len(w.provinces_of(src)) <= 1:
            problems.append("%s has only province %d - moving it would empty the state"
                            % (w.sname(src), pid)); continue
        plan.append((pid, src, dst))

    print("=" * 72)
    for pid, src, dst in plan:
        nm = w.pname(pid) or "unnamed"
        print("province %-6d %-18s %s (%d)  ->  %s (%d)"
              % (pid, nm, w.sname(src), src, w.sname(dst), dst))
    for p in problems:
        print("REFUSED: " + p)
    if not plan:
        return 1
    print("=" * 72)

    moved = {pid for pid, _, _ in plan}

    # ---- 5. buildings.txt spawns that would end up on foreign ground ------
    sea_adj, relocations = None, []
    for pid, src, dst in plan:
        for idx in b.blocking_in(pid):
            f = b.rows[idx]
            owner, kind = int(f[0]), f[1]
            if owner == dst:
                continue                       # follows the ground anyway, fine
            # candidate destination provinces: still owned by `owner` after the moves
            cands = [q for q in w.provinces_of(owner) if q not in moved]
            if kind in NEEDS_COAST:
                cands = [q for q in cands if q in w.coastal]
            cands = [q for q in cands if b.anchors(q)]
            # prefer somewhere that is not already hosting the same slot
            quiet = [q for q in cands
                     if not any(b.rows[i][1] == kind for i in b.by_prov.get(q, []))]
            pick = (quiet or cands)
            if not pick:
                problems.append("%s (%d): %s sits in province %d and there is nowhere "
                                "else in the state to put it%s"
                                % (w.sname(owner), owner, kind, pid,
                                   " (needs a coastal province)" if kind in NEEDS_COAST else ""))
                continue
            q = pick[0]
            a = b.rows[b.anchors(q)[0]]
            sea = None
            if kind in NEEDS_SEA:
                have = [b.rows[i][6] for i in b.by_prov.get(q, [])
                        if b.rows[i][1] in NEEDS_SEA and b.rows[i][6] not in ("0", "")]
                if have:
                    sea = have[0]
                else:
                    if sea_adj is None:
                        print("scanning provinces.bmp for sea adjacency ...")
                        sea_adj = w.sea_neighbours()
                    opts = sorted(sea_adj.get(q, []))
                    if not opts:
                        problems.append("%s (%d): naval_base_spawn needs a sea province next "
                                        "to province %d and none was found" % (w.sname(owner), owner, q))
                        continue
                    sea = str(opts[0])
            relocations.append((idx, kind, owner, pid, q, a[2], a[3], a[4], sea))

    for idx, kind, owner, frm, to, x, y, z, sea in relocations:
        print("relocate %-20s of %s (%d): province %d -> %d  at %s;%s;%s%s"
              % (kind, w.sname(owner), owner, frm, to, x, y, z,
                 "  sea " + sea if sea else ""))
    if not relocations:
        print("no rocket site or naval slot is affected - buildings.txt untouched")

    if problems:
        print("\n".join("REFUSED: " + p for p in problems))
        print("\nnothing written.")
        return 1

    # ---- apply -----------------------------------------------------------
    touched = []
    for pid, src, dst in plan:
        ts = w.state_txt[src]
        ts = set_province_list(ts, [p for p in w.provinces_of(src) if p != pid])
        ts, vp = pull_victory_point(ts, pid)
        ts, bl = pull_province_building(ts, pid)
        w.state_txt[src] = ts

        td = w.state_txt[dst]
        td = set_province_list(td, w.provinces_of(dst) + [pid])
        if vp is not None:
            td = push_victory_point(td, pid, vp)
            print("victory point %d (value %d) follows the province" % (pid, vp))
        if bl is not None:
            td = push_province_building(td, bl)
            print("province building %r follows the province" % bl)
        w.state_txt[dst] = td

        # ---- 2. strategic region / air zone -------------------------------
        rs, rd = w.prov2region.get(pid), None
        for q in w.provinces_of(dst):
            if q != pid and q in w.prov2region:
                rd = w.prov2region[q]; break
        if rd is None:
            problems.append("cannot tell which region %s belongs to" % w.sname(dst))
        elif rs != rd:
            w.reg_txt[rs] = set_province_list(w.reg_txt[rs],
                                              [p for p in w.region_provinces(rs) if p != pid])
            w.reg_txt[rd] = set_province_list(w.reg_txt[rd],
                                              w.region_provinces(rd) + [pid])
            w.prov2region[pid] = rd
            print("air zone: province %d moves from region %d to region %d" % (pid, rs, rd))
        else:
            print("air zone: region %d unchanged (both states are inside it)" % rs)

    for idx, kind, owner, frm, to, x, y, z, sea in relocations:
        b.relocate(idx, x, y, z, sea)

    if problems:
        print("\n".join("REFUSED: " + p for p in problems))
        return 1

    # counts in buildings.txt must stay exactly vanilla
    assert b.counts_by_state() == before_counts, "per-state slot counts changed - refusing"

    if not apply_:
        print("\ndry run - rerun with --apply to write %d state file(s), the regions "
              "and %d buildings.txt relocation(s)"
              % (len({s for _, s, _ in plan} | {d for _, _, d in plan}), len(relocations)))
        return 0

    for sid in {s for _, s, _ in plan} | {d for _, _, d in plan}:
        dst = os.path.join(MOD, "history", "states", w.state_file[sid])
        write(dst, w.state_txt[sid], w.state_bom[sid])
        touched.append(dst)
    for rid, txt in w.reg_txt.items():
        if txt != read(w.reg_src[rid])[0]:
            dst = os.path.join(MOD, "map", "strategicregions", w.reg_file[rid])
            write(dst, txt, w.reg_bom[rid])
            touched.append(dst)
    if b.dirty:
        touched.append(b.save())

    print("\nwrote:")
    for t in touched:
        print("   " + os.path.relpath(t, MOD).replace("\\", "/"))
    print("\nnow run:  python tools/check_map.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
