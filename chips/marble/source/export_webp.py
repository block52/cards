"""Downscale the table sprites to small transparent WebPs for the cards CDN.

Usage:
  Blender -b --factory-startup --python blender/export_webp.py -- <src_dir> <out_dir> [size]  (size 0 = keep full size)
"""
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
size = int(argv[2]) if len(argv) > 2 else 128
os.makedirs(out, exist_ok=True)

scene = bpy.context.scene
settings = scene.render.image_settings
settings.file_format = "WEBP"
settings.color_mode = "RGBA"
settings.quality = 90
scene.view_settings.view_transform = "Standard"  # pixels are already display-ready

for name in sorted(os.listdir(src)):
    if not name.endswith(".png"):
        continue
    img = bpy.data.images.load(os.path.join(src, name))
    # Halve in steps so the small sprite stays crisp instead of aliased.
    w = img.size[0]
    while size and w // 2 >= size:
        w //= 2
        img.scale(w, w)
    if size and w != size:
        img.scale(size, size)
    dest = os.path.join(out, name[:-4] + ".webp")
    img.save_render(dest, scene=scene)
    print("WEBP", dest, os.path.getsize(dest))
