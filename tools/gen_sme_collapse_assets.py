"""Flags, leader portraits and the war-score slider for the SME war and collapse.

Run from anywhere; paths are absolute. Re-running overwrites the outputs.
Source pictures are the user's, in OneDrive/Bilder.
"""
import os
import shutil
from PIL import Image, ImageDraw

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAN = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
PICS = r'C:\Users\franz\OneDrive\Bilder'

FLAGS = {
    'RUE': os.path.join(PICS, 'Rus Empire.jpg'),
    'VGD': os.path.join(PICS, 'Volgoda.webp'),
    'GRK': os.path.join(PICS, 'FLAG_GOR.webp.png'),
    'ZWF': os.path.join(PICS, 'Red army.webp'),
    'OSG': os.path.join(PICS, 'FLAG_GAY.webp'),
    'KMR': os.path.join(VAN, 'gfx', 'flags', 'KOM_democratic.tga'),
    'ARB': os.path.join(PICS, 'Aryan_Brotherhood.webp'),
    'RNS': os.path.join(PICS, 'PRG.webp'),
    'RFS': os.path.join(PICS, 'Natioan.webp'),
    'SPT': os.path.join(VAN, 'gfx', 'flags', 'SOV_communism.tga'),
    # Cosmetic: the SME under Zhukov as the West Russian Army Front.
    'SME_WRAF': os.path.join(PICS, 'Red army.webp'),
}
# Cosmetic: ZWF as the southern Emergency Government keeps the SME's own flags.
EMERGENCY_FROM = 'SME'

PORTRAITS = {
    'kasparov': os.path.join(PICS, 'Skärmbilder', 'Skärmbild 2026-10-31 212817.png'),
    'raziv': os.path.join(PICS, 'Leyanold Raziv.png'),
    'pavlov': os.path.join(PICS, 'Cyril_Pavlov.webp'),
    'voznesensky': os.path.join(PICS, 'Voznesensky.webp'),
    'dobrovolsky': os.path.join(PICS, 'Vagner2.webp'),
    'yeltsin': os.path.join(PICS, 'Yeltisn.png'),
    'molotov': os.path.join(PICS, 'Russian Fascist.webp'),
    'brezhnev': os.path.join(PICS, 'Brezjev.webp'),
}

SIZES = [('', (82, 52)), ('medium', (41, 26)), ('small', (10, 7))]
VARIANTS = ['', '_communism', '_democratic', '_fascism', '_neutrality']


def write_flags(tag, img):
    img = img.convert('RGBA')
    for sub, size in SIZES:
        d = os.path.join(MOD, 'gfx', 'flags', sub)
        os.makedirs(d, exist_ok=True)
        out = img.resize(size, Image.LANCZOS)
        for v in VARIANTS:
            out.save(os.path.join(d, f'{tag}{v}.tga'))


def cover(img, w, h, top_bias=0.25):
    """Crop to w:h keeping the face, which sits in the upper part of a portrait."""
    img = img.convert('RGBA')
    sw, sh = img.size
    if sw / sh > w / h:
        nw = int(sh * w / h)
        x = (sw - nw) // 2
        img = img.crop((x, 0, x + nw, sh))
    else:
        nh = int(sw * h / w)
        y = int((sh - nh) * top_bias)
        img = img.crop((0, y, sw, y + nh))
    return img.resize((w, h), Image.LANCZOS)


def bar_frames():
    """55 frames: -100 to +170 in steps of 5. Left of zero is the SME's collapse,
    right of zero the Reichskommissariats'. The fill runs from zero to the score."""
    d = os.path.join(MOD, 'gfx', 'interface', 'wif_sme_war')
    os.makedirs(d, exist_ok=True)
    W, H = 340, 22
    lo, hi = -100, 170
    px = lambda v: 4 + round((v - lo) / (hi - lo) * (W - 8))
    zero = px(0)
    for i in range(55):
        score = lo + i * 5
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(im)
        g.rounded_rectangle((0, 0, W - 1, H - 1), 5, fill=(24, 22, 20, 235), outline=(150, 130, 90, 255))
        g.rectangle((4, 5, zero, H - 6), fill=(70, 30, 28, 255))
        g.rectangle((zero, 5, W - 5, H - 6), fill=(36, 52, 40, 255))
        x = px(score)
        if score < 0:
            g.rectangle((x, 5, zero, H - 6), fill=(190, 45, 35, 255))
        elif score > 0:
            g.rectangle((zero, 5, x, H - 6), fill=(70, 165, 80, 255))
        for t in range(-100, 171, 50):
            tx = px(t)
            g.line((tx, H - 6, tx, H - 3), fill=(150, 130, 90, 255))
        g.line((zero, 2, zero, H - 3), fill=(230, 220, 190, 255), width=1)
        g.polygon([(x - 5, 0), (x + 5, 0), (x, 7)], fill=(250, 235, 160, 255))
        g.rectangle((x - 1, 6, x + 1, H - 4), fill=(250, 235, 160, 255))
        im.save(os.path.join(d, f'bar_{i:02d}.png'))


def main():
    for tag, src in FLAGS.items():
        write_flags(tag, Image.open(src))
    for sub, _ in SIZES:
        d = os.path.join(MOD, 'gfx', 'flags', sub)
        for v in VARIANTS:
            s = os.path.join(d, f'{EMERGENCY_FROM}{v}.tga')
            if os.path.exists(s):
                shutil.copyfile(s, os.path.join(d, f'ZWF_EMERGENCY{v}.tga'))
    d = os.path.join(MOD, 'gfx', 'leaders', 'SME')
    os.makedirs(d, exist_ok=True)
    for name, src in PORTRAITS.items():
        im = Image.open(src)
        cover(im, 156, 210).save(os.path.join(d, f'Portrait_wif_{name}.png'))
        cover(im, 67, 67, 0.15).save(os.path.join(d, f'Portrait_wif_{name}_small.png'))
    bar_frames()
    print('ok')


if __name__ == '__main__':
    main()
