"""The focus-icon mold: turn any picture into a HoI4 focus icon, ready to use.

    python tools/make_focus_icon.py mold
        Writes the mold to tools/art/focus_mold/:
          focus_mold_blank.png   100x88, transparent - paint your icon on this
          focus_mold_guides.png  the same with guides: the frame, the art area
                                 vanilla uses (5,3)-(95,86), and the centre lines
          focus_mold_example.png a vanilla icon, for size and style

    python tools/make_focus_icon.py <picture> <NAME> [--cut] [--plain] [--fill]
        Makes GFX_focus_<NAME> from <picture> (png/jpg/webp, any size):
          - fits it into vanilla's art area (keeps proportions, centred);
          - --cut  removes a flat background (the colour of the corners) - use it
                   for pictures without transparency;
          - --fill crops to fill the whole art area instead of fitting inside it;
          - adds vanilla's dark outline and drop shadow (--plain: don't);
          - writes gfx/interface/goals/wif/focus_<NAME>.dds (HoI4's exact DDS
            format) and a preview PNG next to the source picture;
          - registers GFX_focus_<NAME> in interface/wif_focus_icons.gfx and the
            shine version GFX_focus_<NAME>_shine in interface/wif_focus_icons_shine.gfx
            (the game looks for <icon>_shine when a focus can be taken).
        Then use it in a focus:   icon = GFX_focus_<NAME>

Example:
    python tools/make_focus_icon.py tools/art/hun/crown.png HUN_holy_crown --cut
"""
import os, re, struct, sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
W, H = 100, 88                       # vanilla focus icon canvas
ART = (5, 3, 95, 86)                 # where vanilla puts the artwork (median of 400 icons)
GFX = os.path.join(MOD, 'interface', 'wif_focus_icons.gfx')
GFX_SHINE = os.path.join(MOD, 'interface', 'wif_focus_icons_shine.gfx')


def write_dds(im, path):
    """Uncompressed 32-bit BGRA, one mip - the format of vanilla's own icons (header as in tools/bop_icons.py)."""
    w, h = im.size
    hdr = bytearray(128)
    hdr[0:4] = b'DDS '
    struct.pack_into('<7I', hdr, 4, 124, 0x100F, h, w, w * 4, 0, 1)
    struct.pack_into('<8I', hdr, 76, 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    struct.pack_into('<I', hdr, 108, 0x1000)
    r, g, b, a = im.split()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(bytes(hdr))
        fh.write(Image.merge('RGBA', (b, g, r, a)).tobytes())


def mold():
    d = os.path.join(MOD, 'tools', 'art', 'focus_mold')
    os.makedirs(d, exist_ok=True)
    Image.new('RGBA', (W, H), (0, 0, 0, 0)).save(os.path.join(d, 'focus_mold_blank.png'))
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(g)
    dr.rectangle((0, 0, W - 1, H - 1), outline=(255, 0, 0, 255))                 # the canvas
    dr.rectangle((ART[0], ART[1], ART[2] - 1, ART[3] - 1), outline=(0, 200, 255, 255))   # the art area
    for x in range(0, W, 4):
        dr.point((x, H // 2), fill=(255, 255, 0, 160))
    for y in range(0, H, 4):
        dr.point((W // 2, y), fill=(255, 255, 0, 160))
    g.save(os.path.join(d, 'focus_mold_guides.png'))
    big = g.resize((W * 4, H * 4), Image.NEAREST)
    big.save(os.path.join(d, 'focus_mold_guides_x4.png'))
    try:
        Image.open(os.path.join(GAME, 'gfx', 'interface', 'goals', 'focus_generic_steel.dds')).convert('RGBA').save(os.path.join(d, 'focus_mold_example.png'))
    except OSError:
        pass
    print('wrote the mold to', d)
    print('  red = the 100x88 canvas, blue = the art area vanilla uses, yellow = centre lines')


def cut_background(im, tol=40):
    """Make the corners' colour transparent, flood-filled from the edges only."""
    im = im.convert('RGBA')
    px = im.load()
    w, h = im.size
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    ref = tuple(sorted(c[i] for c in corners)[1] for i in range(3))
    seen = set()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        seen.add((x, y))
        r, g, b, a = px[x, y]
        if a and max(abs(r - ref[0]), abs(g - ref[1]), abs(b - ref[2])) > tol:
            continue
        px[x, y] = (r, g, b, 0)
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return im


def make(src, name, cut=False, plain=False, fill=False):
    im = Image.open(src).convert('RGBA')
    if cut:
        im = cut_background(im)
    bb = im.split()[3].getbbox()
    if bb:
        im = im.crop(bb)
    aw, ah = ART[2] - ART[0], ART[3] - ART[1]
    pad = 0 if plain else 3                      # room for the outline and shadow
    tw, th = aw - pad, ah - pad
    k = (max if fill else min)(tw / im.width, th / im.height)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    if fill:
        x0, y0 = (im.width - tw) // 2, (im.height - th) // 2
        im = im.crop((x0, y0, x0 + tw, y0 + th))
    art = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ox = ART[0] + (aw - pad - im.width) // 2
    oy = ART[1] + (ah - pad - im.height) // 2
    art.alpha_composite(im, (ox, oy))
    if plain:
        out = art
    else:
        a = art.split()[3]
        # vanilla's look: a thin dark outline and a soft shadow down-right
        outline = a.filter(ImageFilter.MaxFilter(3))
        shadow = ImageChops.offset(a.filter(ImageFilter.MaxFilter(3)), 2, 2).filter(ImageFilter.GaussianBlur(1.5))
        out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        out.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (W, H), 0)] * 3, shadow.point(lambda v: v * 0.6))))
        out.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (W, H), 12)] * 3, outline.point(lambda v: v * 0.85))))
        out.alpha_composite(art)
    rel = f'gfx/interface/goals/wif/focus_{name}.dds'
    write_dds(out, os.path.join(MOD, *rel.split('/')))
    prev = os.path.splitext(src)[0] + f'_focus_{name}_preview.png'
    out.resize((W * 3, H * 3), Image.LANCZOS).save(prev)
    register(name, rel)
    print(f'wrote {rel}\n  preview {prev}\n  use it as:  icon = GFX_focus_{name}')


def _add(path, header, entry, key):
    t = open(path, encoding='utf-8').read() if os.path.exists(path) else header + 'spriteTypes = {\n}\n'
    if f'"{key}"' in t:
        t = re.sub(r'\tspriteType = \{\n\t\tname = "' + re.escape(key) + r'"\n.*?\n\t\}\n', '', t, flags=re.S)
    i = t.rstrip().rfind('}')
    t = t[:i] + entry + '}\n'
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(t.replace('\r\n', '\n'))


def register(name, rel):
    key = f'GFX_focus_{name}'
    _add(GFX, '# Focus icons drawn for Welt in Flammen.\n\n', f'\tspriteType = {{\n\t\tname = "{key}"\n\t\ttexturefile = "{rel}"\n\t}}\n', key)
    anim = lambda rot, sx: (f'\t\tanimation = {{\n\t\t\tanimationmaskfile = "{rel}"\n\t\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"\n'
                           f'\t\t\tanimationrotation = {rot}\n\t\t\tanimationlooping = no\n\t\t\tanimationtime = 0.75\n\t\t\tanimationdelay = 0\n'
                           f'\t\t\tanimationblendmode = "add"\n\t\t\tanimationtype = "scrolling"\n\t\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}\n'
                           f'\t\t\tanimationtexturescale = {{ x = {sx} y = 1.0 }}\n\t\t}}\n')
    shine = (f'\tspriteType = {{\n\t\tname = "{key}_shine"\n\t\ttexturefile = "{rel}"\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n'
             + anim('-90.0', '2.0') + anim('90.0', '1.0') + '\t\tlegacy_lazy_load = no\n\t}\n')
    _add(GFX_SHINE, '# The shine versions of the icons in wif_focus_icons.gfx (tools/make_focus_icon.py).\n\n', shine, key + '_shine')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
    elif a[0] == 'mold':
        mold()
    else:
        flags = {x for x in a if x.startswith('--')}
        pos = [x for x in a if not x.startswith('--')]
        assert len(pos) == 2, 'usage: make_focus_icon.py <picture> <NAME> [--cut] [--plain] [--fill]'
        make(pos[0], pos[1], cut='--cut' in flags, plain='--plain' in flags, fill='--fill' in flags)
