"""Block52 luxury chip — ray-traced hero render (Blender 4.5, Cycles).

Usage:
  Blender -b --factory-startup --python hero.py -- \
      --body Marble016 --insert Marble021 --value 5K --plate black --metal gold --out renders/hero.png

Everything is real geometry: stepped bevelled edge, coin-milled gold band, recessed
inlays in gold-walled pockets, a recessed guilloché enamel plate, and embossed
bevelled lettering. Materials are the CC0 ambientCG scans in ../materials.
"""
import argparse
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MATS = os.path.join(ROOT, "materials")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--body", default="Marble016")
ap.add_argument("--insert", default="Marble021")
ap.add_argument("--value", default="5K")
ap.add_argument("--value-color", default=None, help="hex: render the value in a bright, non-metallic colour instead of satin metal (legibility at table size)")
ap.add_argument("--value-glow", type=float, default=0.0, help="emission strength for --value-color, so the numbers read evenly whatever the lighting")
ap.add_argument("--value-scale", type=float, default=1.0, help="multiplier on the value's size on the plate")
ap.add_argument("--value-font", default="/System/Library/Fonts/Supplemental/Arial Black.ttf", help="font file for the value (Arial Black is the original; Arial Bold is lighter)")
ap.add_argument("--plate-r", type=float, default=0.6, help="centre plate radius (0.6 original); a bigger plate pushes the edge inlays out into a thinner rim")
ap.add_argument("--no-value", action="store_true", help="leave the centre plate blank (the UI draws the value as live text)")
ap.add_argument("--no-wordmark", action="store_true", help="leave the block52 wordmark off the plate; the value is centred and enlarged to fill it")
ap.add_argument("--plate", default="black", choices=["black", "ivory"])
ap.add_argument("--metal", default="gold", choices=["gold", "platinum"])
ap.add_argument("--out", default=os.path.join(ROOT, "renders", "hero.png"))
ap.add_argument("--samples", type=int, default=128)
ap.add_argument("--res", type=int, default=1600)
ap.add_argument("--tint", default=None, help="hex colour multiplied over the body scan (use with white marble)")
ap.add_argument("--vein", default=None, help="hex vein colour for a dyed body (default: a pale tint of the dye)")
ap.add_argument("--vein2", default=None, help="hex second vein colour (a second, offset vein network)")
ap.add_argument("--vein-metal", action="store_true", help="veins are metallic (lapis-style gold streaks)")
ap.add_argument("--insert-solid", default=None, help="hex: plain polished inlays with no marbling")
ap.add_argument("--insert-tint", default=None, help="hex colour multiplied over the inlay scan")
ap.add_argument("--tilt", type=float, default=90.0, help="topdown camera elevation in degrees (90 = straight down)")
ap.add_argument("--thick", type=float, default=1.0, help="chip thickness multiplier (table sprites show the edge for stacking)")
ap.add_argument("--inlays", type=int, default=8, help="number of edge inlays (0 = dealer button: plain stone ring with gold pinstripes)")
ap.add_argument("--topdown", action="store_true", help="square, straight-down, transparent: the table's chip sprite")
args = ap.parse_args(argv)

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.denoising_prefilter = "ACCURATE"
scene.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
scene.render.resolution_x = args.res
scene.render.resolution_y = int(args.res * 0.7)
scene.render.film_transparent = False
scene.view_settings.view_transform = "Khronos PBR Neutral"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0.0

# Chip dimensions (1 unit = 20 mm radius chip).
R, T = 1.0, 0.2 * args.thick
TOP = T / 2


def link(obj):
    scene.collection.objects.link(obj)
    return obj


def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return link(bpy.data.objects.new(name, me))


def sector_prism(name, r_in, r_out, a0, a1, z0, z1, segs=48):
    """Annular sector extruded between z0 and z1."""
    bm = bmesh.new()
    pts = [(r_out * math.cos(a0 + (a1 - a0) * i / segs), r_out * math.sin(a0 + (a1 - a0) * i / segs)) for i in range(segs + 1)]
    pts += [(r_in * math.cos(a1 - (a1 - a0) * i / segs), r_in * math.sin(a1 - (a1 - a0) * i / segs)) for i in range(segs + 1)]
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    top = [bm.verts.new((x, y, z1)) for x, y in pts]
    n = len(pts)
    bm.faces.new(list(reversed(bot)))
    bm.faces.new(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj(name, bm)


def cylinder(name, r, z0, z1, verts=256):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(0, 0, (z0 + z1) / 2))
    o = bpy.context.active_object
    o.name = name
    return o


def boolean_cut(target, cutter):
    m = target.modifiers.new("cut", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    apply_all(target)
    bpy.data.objects.remove(cutter, do_unlink=True)


def smooth(obj, angle=30):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    obj.select_set(False)


# ---------------------------------------------------------------- materials
def node(nt, kind, loc, **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def hex_linear(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)


def scan_material(name, asset, polish=True, scale=0.55, rotation=0.0, tint=None, vein_hex=None, vein2_hex=None, vein_metal=False):
    """Principled material from an ambientCG scan, box-projected in object space so edges wrap cleanly."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    out = nt.nodes["Material Output"]
    coord = node(nt, "ShaderNodeTexCoord", (-1200, 0))
    mapping = node(nt, "ShaderNodeMapping", (-1000, 0))
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    mapping.inputs["Rotation"].default_value = (0, 0, rotation)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    def img(kind, colorspace, y):
        n = node(nt, "ShaderNodeTexImage", (-750, y))
        n.image = bpy.data.images.load(os.path.join(MATS, asset, f"{asset}_2K-JPG_{kind}.jpg"), check_existing=True)
        n.image.colorspace_settings.name = colorspace
        n.projection = "BOX"
        n.projection_blend = 0.25
        nt.links.new(mapping.outputs["Vector"], n.inputs["Vector"])
        return n

    col = img("Color", "sRGB", 300)
    rough = img("Roughness", "Non-Color", 0)
    nrm = img("NormalGL", "Non-Color", -300)
    if tint:
        # Dyed stone: the scan's veining (light on dark) becomes pale veins running through the
        # denomination colour, so every chip keeps real marble character in its colour.
        bw = node(nt, "ShaderNodeRGBToBW", (-600, 450))
        nt.links.new(col.outputs["Color"], bw.inputs["Color"])
        vein = node(nt, "ShaderNodeMapRange", (-450, 450))
        vein.inputs["From Min"].default_value = 0.04
        vein.inputs["From Max"].default_value = 0.25 if vein_hex else 0.55  # dark veins on white need a bolder mask
        nt.links.new(bw.outputs["Val"], vein.inputs["Value"])
        mix = node(nt, "ShaderNodeMix", (-300, 300), data_type="RGBA")
        base = hex_linear(tint)
        # Darker than the swatch: the polish and studio light lift it back, deep colour reads as rich.
        if vein_hex:  # stone with its own vein colour (black on white, brown on yellow, gold on lapis...)
            lum = 0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]
            k = 1.0 if lum > 0.75 else 0.6  # deepen coloured bodies, keep white/near-white as given
            mix.inputs["A"].default_value = tuple(c * k for c in base[:3]) + (1.0,)
            mix.inputs["B"].default_value = hex_linear(vein_hex)
        else:
            mix.inputs["A"].default_value = tuple(c * 0.5 for c in base[:3]) + (1.0,)
            mix.inputs["B"].default_value = tuple(c + (1 - c) * 0.6 for c in base[:3]) + (1.0,)
        nt.links.new(vein.outputs["Result"], mix.inputs["Factor"])
        result = mix.outputs["Result"]
        if vein_metal:
            nt.links.new(vein.outputs["Result"], bsdf.inputs["Metallic"])
        if vein2_hex:
            # A second vein network: the same scan sampled at another scale and angle.
            map2 = node(nt, "ShaderNodeMapping", (-1000, 700))
            map2.inputs["Scale"].default_value = (scale * 1.9,) * 3
            map2.inputs["Rotation"].default_value = (0, 0, rotation + 1.9)
            map2.inputs["Location"].default_value = (0.37, 0.61, 0)
            nt.links.new(coord.outputs["Object"], map2.inputs["Vector"])
            col2 = node(nt, "ShaderNodeTexImage", (-750, 700))
            col2.image = col.image
            col2.projection = "BOX"
            col2.projection_blend = 0.25
            nt.links.new(map2.outputs["Vector"], col2.inputs["Vector"])
            bw2 = node(nt, "ShaderNodeRGBToBW", (-600, 700))
            nt.links.new(col2.outputs["Color"], bw2.inputs["Color"])
            v2 = node(nt, "ShaderNodeMapRange", (-450, 700))
            v2.inputs["From Min"].default_value = 0.06
            v2.inputs["From Max"].default_value = 0.3
            nt.links.new(bw2.outputs["Val"], v2.inputs["Value"])
            mix2 = node(nt, "ShaderNodeMix", (-200, 450), data_type="RGBA")
            nt.links.new(v2.outputs["Result"], mix2.inputs["Factor"])
            nt.links.new(result, mix2.inputs["A"])
            mix2.inputs["B"].default_value = hex_linear(vein2_hex)
            result = mix2.outputs["Result"]
        nt.links.new(result, bsdf.inputs["Base Color"])
    else:
        nt.links.new(col.outputs["Color"], bsdf.inputs["Base Color"])
    # Polished: compress the scan's roughness into a glossy range.
    rmap = node(nt, "ShaderNodeMapRange", (-450, 0))
    rmap.inputs["To Min"].default_value = 0.12 if polish else 0.25
    rmap.inputs["To Max"].default_value = 0.32 if polish else 0.55
    nt.links.new(rough.outputs["Color"], rmap.inputs["Value"])
    nt.links.new(rmap.outputs["Result"], bsdf.inputs["Roughness"])
    nmap = node(nt, "ShaderNodeNormalMap", (-450, -300))
    nmap.inputs["Strength"].default_value = 0.35
    nt.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Coat Weight"].default_value = 0.6
    bsdf.inputs["Coat Roughness"].default_value = 0.09
    if asset.startswith(("Marble", "Onyx")):
        bsdf.inputs["Subsurface Weight"].default_value = 0.06
        bsdf.inputs["Subsurface Scale"].default_value = 0.02
    return mat


def metal_material(name, kind, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (1.0, 0.76, 0.40, 1) if kind == "gold" else (0.86, 0.88, 0.9, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = roughness
    return mat


def enamel_plate_material(name, color):
    """Glossy enamel over a guilloché sunburst (fine radial engraving via bump)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = 0.4
    b.inputs["Coat Weight"].default_value = 0.35
    b.inputs["Coat Roughness"].default_value = 0.12
    coord = node(nt, "ShaderNodeTexCoord", (-1100, -200))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-900, -200))
    nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    atan = node(nt, "ShaderNodeMath", (-700, -200), operation="ARCTAN2")
    nt.links.new(sep.outputs["Y"], atan.inputs[0])
    nt.links.new(sep.outputs["X"], atan.inputs[1])
    rays = node(nt, "ShaderNodeMath", (-520, -200), operation="MULTIPLY")
    rays.inputs[1].default_value = 360.0
    nt.links.new(atan.outputs[0], rays.inputs[0])
    wave = node(nt, "ShaderNodeMath", (-340, -200), operation="SINE")
    nt.links.new(rays.outputs[0], wave.inputs[0])
    bump = node(nt, "ShaderNodeBump", (-160, -200))
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.002
    nt.links.new(wave.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Coat Normal"])
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


body_mat = scan_material("body", args.body, scale=0.3, tint=args.tint, vein_hex=args.vein, vein2_hex=args.vein2, vein_metal=args.vein_metal)
insert_mat = scan_material("insert", args.insert, scale=0.9, rotation=0.7, tint=args.insert_tint)
if args.insert_solid:
    # Plain polished inlays (jet black enamel look), no stone pattern.
    insert_mat = bpy.data.materials.new("insert_solid")
    insert_mat.use_nodes = True
    ib = insert_mat.node_tree.nodes["Principled BSDF"]
    ib.inputs["Base Color"].default_value = hex_linear(args.insert_solid)
    ib.inputs["Roughness"].default_value = 0.2
    ib.inputs["Coat Weight"].default_value = 0.8
    ib.inputs["Coat Roughness"].default_value = 0.06
metal = metal_material("metal", args.metal, 0.16)
metal_polished = metal_material("metal_polished", args.metal, 0.05)
metal_satin = metal_material("metal_satin", args.metal, 0.32)
plate_mat = enamel_plate_material("plate", (0.012, 0.012, 0.014, 1) if args.plate == "black" else (0.86, 0.83, 0.77, 1))

# ---------------------------------------------------------------- body: stepped bevel
body = cylinder("body", R * 0.992, -TOP, TOP)
bev = body.modifiers.new("bevel", "BEVEL")
bev.width = 0.035
bev.segments = 2
bev.profile = 0.15  # flat steps: a stepped chamfer rather than a round
bev.limit_method = "ANGLE"
apply_all(body)

# recessed pockets for the 8 inlays and the centre plate
N, SPAN = args.inlays, 0.34
POCKET_IN, POCKET_OUT, POCKET_D = 0.70, 0.90, 0.016
if args.plate_r > 0.6:  # bigger face: inlays move out into a thinner rim, just inside the edge
    POCKET_IN, POCKET_OUT, SPAN = args.plate_r + 0.07, 0.935, 0.30
for i in range(N):
    a = i * 2 * math.pi / N
    boolean_cut(body, sector_prism(f"cut{i}", POCKET_IN, POCKET_OUT, a - SPAN / 2, a + SPAN / 2, TOP - POCKET_D, TOP + 0.05))
PLATE_R = args.plate_r
boolean_cut(body, cylinder("platecut", PLATE_R, TOP - 0.02, TOP + 0.05))
smooth(body, 35)
assign(body, body_mat)

# ---------------------------------------------------------------- inlays in gold-walled pockets
for i in range(N):
    a = i * 2 * math.pi / N
    wall = sector_prism(f"wall{i}", POCKET_IN, POCKET_OUT, a - SPAN / 2, a + SPAN / 2, TOP - POCKET_D, TOP - 0.008)
    assign(wall, metal)
    m = 0.009
    ins = sector_prism(f"inlay{i}", POCKET_IN + m, POCKET_OUT - m, a - SPAN / 2 + m * 1.25, a + SPAN / 2 - m * 1.25, TOP - POCKET_D, TOP - 0.0025)
    assign(ins, insert_mat)
    smooth(ins, 30)

if N == 0:
    # Dealer button: no inlays, so two fine inlaid gold pinstripes dress the stone ring instead.
    for i, r in enumerate((0.82,)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.010, major_segments=256, minor_segments=16, location=(0, 0, TOP - 0.003))
        pin = bpy.context.active_object
        pin.name = f"pinstripe{i}"
        smooth(pin, 60)
        assign(pin, metal_polished)

# ---------------------------------------------------------------- poker-chip edge
# A coloured edge band in the body stone, with evenly-spaced contrasting edge spots
# (matching the face inlays) and thin gold pinstripes top and bottom to keep it premium.
band = cylinder("band", R * 1.0, -T * 0.24, T * 0.24)
assign(band, body_mat)
smooth(band, 35)

# Edge spots only belong on chips; the dealer button (inlays == 0) keeps a plain band.
if args.inlays > 0:
    EDGE_SPOTS = 12
    SPOT_W = (2 * math.pi / EDGE_SPOTS) * 0.42
    for i in range(EDGE_SPOTS):
        a = i * 2 * math.pi / EDGE_SPOTS
        spot = sector_prism(f"edgespot{i}", R * 0.985, R * 1.012, a - SPOT_W / 2, a + SPOT_W / 2, -T * 0.16, T * 0.16)
        assign(spot, insert_mat)
        smooth(spot, 60)

# Thin gold pinstripe rings top and bottom, framing the edge.
for k, zc in enumerate((T * 0.22, -T * 0.22)):
    ring = cylinder(f"edgetrim{k}", R * 1.004, zc - T * 0.02, zc + T * 0.02)
    assign(ring, metal_polished)
    smooth(ring, 60)

# ---------------------------------------------------------------- recessed guilloché plate + bezel
plate = cylinder("plate", PLATE_R - 0.004, TOP - 0.02, TOP - 0.006)
assign(plate, plate_mat)
bpy.ops.mesh.primitive_torus_add(major_radius=PLATE_R + 0.004, minor_radius=0.014, major_segments=256, minor_segments=24, location=(0, 0, TOP - 0.004))
bezel = bpy.context.active_object
assign(bezel, metal_polished)
bpy.ops.mesh.primitive_torus_add(major_radius=PLATE_R + 0.035, minor_radius=0.005, major_segments=256, minor_segments=16, location=(0, 0, TOP - 0.0015))
assign(bpy.context.active_object, metal)

# ---------------------------------------------------------------- embossed lettering (raised, bevelled gold)
PLATE_TOP = TOP - 0.006


def emboss_curve(obj, width, y, max_h=None, mat=None):
    w = max(obj.dimensions.x, 1e-6)
    obj.data.extrude = w * 0.01
    obj.data.bevel_depth = w * 0.004
    obj.data.bevel_resolution = 3
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.active_object
    obj.select_set(False)
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    s = width / (max(xs) - min(xs))
    if max_h:  # narrow values like "1" would otherwise scale up into the wordmark
        s = min(s, max_h / (max(ys) - min(ys)))
    cx, cy, zmin, zspan = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, min(zs), (max(zs) - min(zs)) or 1
    EMBOSS = 0.007  # raised height of the lettering
    for v in obj.data.vertices:
        v.co.x = (v.co.x - cx) * s
        v.co.y = (v.co.y - cy) * s + y
        v.co.z = (v.co.z - zmin) / zspan * EMBOSS + PLATE_TOP - 0.0005
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    smooth(obj, 40)
    assign(obj, mat or metal_satin)
    return obj


def bright_value_material(name, hex_color, glow):
    """Non-metallic, lightly emissive lettering: reads the same on the dark plate from any light."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    col = hex_linear(hex_color)
    b.inputs["Base Color"].default_value = col
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Emission Color"].default_value = col
    b.inputs["Emission Strength"].default_value = glow
    return m


# Value: Arial Black, big.
font = bpy.data.fonts.load(args.value_font)
tc = bpy.data.curves.new("value", "FONT")
tc.body = args.value
tc.font = font
tc.align_x = "CENTER"
tc.align_y = "CENTER"
val = link(bpy.data.objects.new("value", tc))
if args.no_value:
    tc.body = "0"  # placeholder geometry, removed below
value_mat = bright_value_material("value_bright", args.value_color, args.value_glow) if args.value_color else None
if args.no_wordmark:
    # The whole plate is the value's: centred, as wide as fits inside the bezel.
    grow = PLATE_R / 0.6  # the value grows with the plate
    v_width = min(1.0 * grow, {1: 0.5, 2: 0.78, 3: 0.92, 4: 0.98}.get(len(args.value), 1.0) * args.value_scale * grow)
    emboss_curve(val, v_width, 0.0, max_h=0.6 * args.value_scale * grow, mat=value_mat)
else:
    emboss_curve(val, min(0.9, {1: 0.42, 2: 0.6, 3: 0.72, 4: 0.8}.get(len(args.value), 0.82) * args.value_scale), -0.13, max_h=0.4 * args.value_scale, mat=value_mat)

# Wordmark: block52 in the brand gradient (magenta -> violet -> blue) enamel, set in gold
# cloisonne walls. The SVG's overlapping rects are rasterised to a 1-unit grid so the letters
# become one clean solid shape (curve import showed every rect's outline as a ridge).
import xml.etree.ElementTree as ET  # noqa: E402

SVG_W, SVG_H = 520, 120
fill_cells = set()
svg = ET.parse(os.path.join(ROOT, "b52-wordmark.svg")).getroot()
for el in svg.iter():
    if not el.tag.endswith("rect"):
        continue
    x, y, w, h = (float(el.get(k)) for k in ("x", "y", "width", "height"))
    if el.get("transform"):  # the two rotated diamond accents
        parent_shift = {12.0: (498, 8), 8.0: (505, 20)}[w]
        cx, cy, rad = parent_shift[0] + w / 2, parent_shift[1] + w / 2, w / math.sqrt(2)
        for i in range(int(cx - rad) - 1, int(cx + rad) + 2):
            for j in range(int(cy - rad) - 1, int(cy + rad) + 2):
                if abs(i + 0.5 - cx) + abs(j + 0.5 - cy) <= rad:
                    fill_cells.add((i, j))
        continue
    for i in range(int(x), int(x + w)):
        for j in range(int(y), int(y + h)):
            fill_cells.add((i, j))

RIM = 4.5  # gold wall thickness in SVG units
reach = int(math.ceil(RIM))
rim_cells = set()
for (i, j) in fill_cells:
    for di in range(-reach, reach + 1):
        for dj in range(-reach, reach + 1):
            if di * di + dj * dj <= RIM * RIM and (i + di, j + dj) not in fill_cells:
                rim_cells.add((i + di, j + dj))

WM_WIDTH, WM_Y = 0.86, 0.205
UNIT = WM_WIDTH / (SVG_W + 2 * RIM)


def to_world(i, j):
    return ((i - SVG_W / 2) * UNIT, WM_Y - (j - SVG_H / 2) * UNIT)


def grid_prism(name, cells, z0, z1):
    bm = bmesh.new()
    for (i, j) in cells:
        x0, y0 = to_world(i, j)
        x1, y1 = to_world(i + 1, j + 1)
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        bm.faces.new([bm.verts.new((cx, cy, z1)) for cx, cy in corners])
        for (di, dj), (a, b) in (((0, -1), (0, 1)), ((1, 0), (1, 2)), ((0, 1), (2, 3)), ((-1, 0), (3, 0))):
            if (i + di, j + dj) not in cells:
                (ax, ay), (bx, by) = corners[a], corners[b]
                bm.faces.new([bm.verts.new(v) for v in ((bx, by, z0), (ax, ay, z0), (ax, ay, z1), (bx, by, z1))])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=UNIT * 0.01)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # (no dissolve: merged n-gons with letter holes triangulate badly and leave slashes)
    obj = mesh_obj(name, bm)
    bev = obj.modifiers.new("bevel", "BEVEL")
    bev.width = UNIT * 0.6
    bev.segments = 2
    bev.limit_method = "ANGLE"
    apply_all(obj)
    return obj


def brand_enamel():
    mat = bpy.data.materials.new("brand_enamel")
    mat.use_nodes = True
    nt = mat.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.45
    b.inputs["Coat Weight"].default_value = 0.35
    b.inputs["Coat Roughness"].default_value = 0.2
    coord = node(nt, "ShaderNodeTexCoord", (-1000, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-800, 0))
    nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    rng = node(nt, "ShaderNodeMapRange", (-600, 0))
    rng.inputs["From Min"].default_value = -WM_WIDTH / 2
    rng.inputs["From Max"].default_value = WM_WIDTH / 2
    nt.links.new(sep.outputs["X"], rng.inputs["Value"])
    ramp = node(nt, "ShaderNodeValToRGB", (-400, 0))
    els = ramp.color_ramp.elements
    els[0].color = (0.75, 0.0, 0.85, 1)  # #c026d3
    els[1].position = 1.0
    els[1].color = (0.0, 0.28, 1.0, 1)  # #3b82f6
    mid = els.new(0.5)
    mid.color = (0.3, 0.0, 1.0, 1)  # #7c3aed
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    # Self-lit enamel so the brand colours stay vivid under the dark studio (no bloom, so no halo).
    nt.links.new(ramp.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.3
    return mat


WM_BASE = PLATE_TOP - 0.0005
wm_rim = grid_prism("wordmark_rim", rim_cells, WM_BASE, PLATE_TOP + 0.007)
smooth(wm_rim, 40)
assign(wm_rim, metal_polished)
wm_fill = grid_prism("wordmark_fill", fill_cells, WM_BASE, PLATE_TOP + 0.0058)
smooth(wm_fill, 40)
assign(wm_fill, brand_enamel())
if args.no_value:
    v = bpy.data.objects.get("value")
    if v:
        bpy.data.objects.remove(v, do_unlink=True)
if args.no_wordmark:
    for o in (wm_rim, wm_fill):
        bpy.data.objects.remove(o, do_unlink=True)

# ---------------------------------------------------------------- set, lights, camera
world = bpy.data.worlds.new("world")
scene.world = world
world.use_nodes = True
wn = world.node_tree
env = wn.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load(os.path.join(MATS, "hdri", "studio_small_09_2k.hdr"))
wn.links.new(env.outputs["Color"], wn.nodes["Background"].inputs["Color"])
wn.nodes["Background"].inputs["Strength"].default_value = 0.15

# Dark seamless backdrop (the chip rests on it).
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -TOP - 0.0005))
floor = bpy.context.active_object
fm = bpy.data.materials.new("floor")
fm.use_nodes = True
fb = fm.node_tree.nodes["Principled BSDF"]
fb.inputs["Base Color"].default_value = (0.012, 0.012, 0.014, 1)
fb.inputs["Roughness"].default_value = 0.45
assign(floor, fm)
# Hide the world from camera rays so the background stays a clean, dark gradient.
world.cycles_visibility.camera = False


def area(name, loc, rot, size, size_y, power, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = size_y
    ld.energy = power
    ld.color = color
    o = link(bpy.data.objects.new(name, ld))
    o.location = loc
    o.rotation_euler = [math.radians(a) for a in rot]
    return o


area("key", (-3.2, -3.0, 5.5), (35, 0, -45), 4.0, 4.0, 650)
area("rim_l", (-4.5, 3.5, 1.6), (75, 0, -130), 0.5, 6.0, 700, (1.0, 0.95, 0.88))
area("rim_r", (4.5, 3.0, 1.6), (75, 0, 125), 0.5, 6.0, 600, (0.9, 0.95, 1.0))


cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 100
cam_data.dof.use_dof = False
cam_data.dof.aperture_fstop = 6.3
cam = link(bpy.data.objects.new("cam", cam_data))
dist = 8.6
elev = math.radians(52)
cam.location = (0.6, -dist * math.cos(elev), dist * math.sin(elev))
target = (0, 0.05, 0)
direction = [target[i] - cam.location[i] for i in range(3)]
import mathutils  # noqa: E402

cam.rotation_euler = mathutils.Vector(direction).to_track_quat("-Z", "Y").to_euler()
cam_data.dof.focus_distance = mathutils.Vector(direction).length
scene.camera = cam

if args.topdown:
    # Straight down, orthographic, transparent background: what the table draws at 28-32px.
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2 * R * 1.03
    # A slight tilt shows the milled edge below the face, so 4px-offset stacks read as piles.
    e = math.radians(args.tilt)
    cam.location = (0, -10 * math.cos(e), 10 * math.sin(e) - 0.5 * T * math.cos(e))
    cam.rotation_euler = (math.pi / 2 - e, 0, 0)
    scene.render.resolution_y = args.res
    scene.render.film_transparent = True
    floor.hide_render = True

# Turn the whole chip a little so the inlays and milled edge catch the light.
for o in scene.objects:
    if o.type == "MESH" and o.name != floor.name and not args.topdown:
        o.rotation_euler.z += math.radians(14)

os.makedirs(os.path.dirname(args.out), exist_ok=True)
scene.render.filepath = args.out
bpy.ops.render.render(write_still=True)
print("WROTE", args.out)
