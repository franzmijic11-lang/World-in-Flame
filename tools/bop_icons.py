# Build the two SME balance-of-power side icons as HoI4-format DDS files.
#
# Format copied byte-for-byte from vanilla's own bop icons (PRC_bop_left_side.dds):
# 72x88, uncompressed 32-bit BGRA, one mip level, header flags 0x100F, pixel
# format flags 0x41. Pillow's DDS writer is not used - the header is written by
# hand so it matches vanilla exactly.
import os
import struct

from PIL import Image

OUT = os.path.join(
    r"C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen",
    "gfx", "interface", "bop")
os.makedirs(OUT, exist_ok=True)

W, H = 72, 88


def write_dds(im, path):
    """im: RGBA Image at exactly W x H."""
    assert im.size == (W, H), im.size
    hdr = bytearray(128)
    hdr[0:4] = b"DDS "
    struct.pack_into("<7I", hdr, 4,
                     124,        # dwSize
                     0x100F,     # CAPS | HEIGHT | WIDTH | PITCH | PIXELFORMAT
                     H, W,
                     W * 4,      # pitch
                     0,          # depth
                     1)          # mipmap count
    struct.pack_into("<8I", hdr, 76,
                     32, 0x41, 0, 32,
                     0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    struct.pack_into("<I", hdr, 108, 0x1000)   # DDSCAPS_TEXTURE
    # DDS with these masks is BGRA in memory
    b, g, r, a = im.split()[2], im.split()[1], im.split()[0], im.split()[3]
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()
    with open(path, "wb") as fh:
        fh.write(bytes(hdr))
        fh.write(data)
    print("wrote %s  (%d bytes)" % (os.path.basename(path), 128 + len(data)))


def key_out(im, key, t_hard=45, t_soft=115):
    """Magenta key with a soft edge and despill, so the cutout has no pink fringe."""
    im = im.convert("RGBA")
    px = im.load()
    kr, kg, kb = key
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, a = px[x, y]
            d = ((r - kr) ** 2 + (g - kg) ** 2 + (b - kb) ** 2) ** 0.5
            if d <= t_hard:
                px[x, y] = (0, 0, 0, 0)
            elif d < t_soft:
                alpha = int(255 * (d - t_hard) / (t_soft - t_hard))
                # despill: magenta pushes red and blue above green on edge pixels
                r2 = min(r, max(g, b if b < r else g))
                b2 = min(b, max(g, r2))
                px[x, y] = (r2, g, b2, alpha)
    return im


def contain(im, w, h):
    """Whole image inside the frame, centred, transparent padding."""
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(im, ((w - im.size[0]) // 2, (h - im.size[1]) // 2), im)
    return canvas


def cover(im, w, h):
    """Fill the frame, centre-cropping the overflow."""
    src_w, src_h = im.size
    scale = max(w / src_w, h / src_h)
    im = im.resize((max(1, round(src_w * scale)), max(1, round(src_h * scale))), Image.LANCZOS)
    left = (im.size[0] - w) // 2
    top = (im.size[1] - h) // 2
    return im.crop((left, top, left + w, top + h))


# --- Zhukov: cut the pink out, keep the whole portrait -----------------------
z = Image.open(r"C:\Users\franz\OneDrive\Bilder\Zhukov.png").convert("RGBA")
z = key_out(z, (253, 114, 255))
opaque = sum(1 for p in z.getdata() if p[3] > 0)
print("Zhukov: %d of %d pixels kept" % (opaque, z.size[0] * z.size[1]))
write_dds(contain(z, W, H), os.path.join(OUT, "wif_bop_sme_zhukov.dds"))

# --- The council chamber: a scene, so fill the frame ------------------------
c = Image.open(r"C:\Users\franz\OneDrive\Bilder\Portrait_SOV_supreme_soviet.png").convert("RGBA")
write_dds(cover(c, W, H), os.path.join(OUT, "wif_bop_sme_council.dds"))
