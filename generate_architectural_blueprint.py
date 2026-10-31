import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

print("Generating Master Architectural Blueprint for PT Maziya Medical Global...")

# ==============================================================================
# 1. SETUP CANVAS & SCALE CONSTANTS
# ==============================================================================
WIDTH = 2400
HEIGHT = 3800
SCALE = 72.0 # 72 px per meter
WALL_THICK = int(0.15 * SCALE) # 11 pixels

# Fonts
FONT_HELVETICA = '/System/Library/Fonts/HelveticaNeue.ttc'
FONT_ARIAL = '/System/Library/Fonts/Supplemental/Arial.ttf'

font_sheet_title = ImageFont.truetype(FONT_HELVETICA, 34)
font_sec_title   = ImageFont.truetype(FONT_HELVETICA, 24)
font_room_title  = ImageFont.truetype(FONT_HELVETICA, 19)
font_room_sub    = ImageFont.truetype(FONT_HELVETICA, 14)
font_dim         = ImageFont.truetype(FONT_HELVETICA, 15)
font_dim_bold    = ImageFont.truetype(FONT_HELVETICA, 17)
font_kop_title   = ImageFont.truetype(FONT_HELVETICA, 20)
font_kop_body    = ImageFont.truetype(FONT_HELVETICA, 13)
font_kop_sm      = ImageFont.truetype(FONT_HELVETICA, 11)

# Coordinate Anchors for Floor Plan
PLAN_X0 = 400.0   # Property X = 0.00 m
PLAN_X_MAX = PLAN_X0 + 22.20 * SCALE # 1998.4 px

PLAN_Y_BACK = 1500.0                             # Z = 12.60 m (North boundary)
PLAN_Y_GUDANG_SOUTH = PLAN_Y_BACK + 3.00 * SCALE # 1716.0 (Z = 9.60 m)
PLAN_Y_DIR_SOUTH = PLAN_Y_GUDANG_SOUTH + 2.76 * SCALE # 1914.7 (Z = 6.84 m)
PLAN_Y_HALL_DIV = PLAN_Y_BACK + (12.60 - 5.80) * SCALE # 1989.6 (Z = 5.80 m)
PLAN_Y_FACADE = PLAN_Y_BACK + 12.60 * SCALE     # 2407.2 (Z = 0.00 m)
PLAN_Y_FRONT_GATE = PLAN_Y_FACADE + 9.30 * SCALE # 3076.8 (Z = -9.30 m)

def m2px_x(xm):
    return PLAN_X0 + xm * SCALE

def m2px_y(zm_from_front):
    return PLAN_Y_FACADE - zm_from_front * SCALE

# Initialize Layers
layers_dict = {
    "00_Background": Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255)),
    "01_Tampak_Depan_Fasad": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "02_Lantai_&_Hatches": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "03_Dinding_Solid_Hitam": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "04_Pintu_Jendela_Bukaan": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "05_Furnitur_&_Peralatan_2D": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "06_Label_Ruangan_Elevasi": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "07_Dimensi_CAD_Notasi": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
    "08_Kop_Gambar_&_Border": Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)),
}

draw_bg      = ImageDraw.Draw(layers_dict["00_Background"])
draw_elev    = ImageDraw.Draw(layers_dict["01_Tampak_Depan_Fasad"])
draw_floor   = ImageDraw.Draw(layers_dict["02_Lantai_&_Hatches"])
draw_wall    = ImageDraw.Draw(layers_dict["03_Dinding_Solid_Hitam"])
draw_opening = ImageDraw.Draw(layers_dict["04_Pintu_Jendela_Bukaan"])
draw_furn    = ImageDraw.Draw(layers_dict["05_Furnitur_&_Peralatan_2D"])
draw_label   = ImageDraw.Draw(layers_dict["06_Label_Ruangan_Elevasi"])
draw_dim     = ImageDraw.Draw(layers_dict["07_Dimensi_CAD_Notasi"])
draw_kop     = ImageDraw.Draw(layers_dict["08_Kop_Gambar_&_Border"])

# Helper: Dimension Lines
def draw_dim_line(draw, p1, p2, text, offset=0, is_vertical=False, layer_img=None):
    tick_len = 8
    if is_vertical:
        dim_x = p1[0] + offset
        y_min = min(p1[1], p2[1])
        y_max = max(p1[1], p2[1])
        draw.line([(p1[0], p1[1]), (dim_x + (6 if offset > 0 else -6), p1[1])], fill=(148, 163, 184, 255), width=1)
        draw.line([(p2[0], p2[1]), (dim_x + (6 if offset > 0 else -6), p2[1])], fill=(148, 163, 184, 255), width=1)
        draw.line([(dim_x, y_min), (dim_x, y_max)], fill=(30, 41, 59, 255), width=2)
        draw.line([(dim_x - tick_len, y_min + tick_len), (dim_x + tick_len, y_min - tick_len)], fill=(15, 23, 42, 255), width=2)
        draw.line([(dim_x - tick_len, y_max + tick_len), (dim_x + tick_len, y_max - tick_len)], fill=(15, 23, 42, 255), width=2)
        
        # Rotated vertical text along dimension line
        bbox = font_dim_bold.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        txt_img = Image.new("RGBA", (tw + 16, th + 8), (255, 255, 255, 240))
        td = ImageDraw.Draw(txt_img)
        td.text((8, 4), text, fill=(15, 23, 42, 255), font=font_dim_bold)
        txt_rot = txt_img.rotate(90, expand=True)
        rw, rh = txt_rot.size
        px = int(dim_x - rw / 2)
        py = int((y_min + y_max) / 2 - rh / 2)
        if layer_img:
            layer_img.paste(txt_rot, (px, py), txt_rot)
        else:
            draw.text((dim_x - tw/2, (y_min+y_max)/2 - th/2), text, fill=(15, 23, 42, 255), font=font_dim_bold)
    else:
        dim_y = p1[1] + offset
        x_min = min(p1[0], p2[0])
        x_max = max(p1[0], p2[0])
        draw.line([(p1[0], p1[1]), (p1[0], dim_y + (6 if offset > 0 else -6))], fill=(148, 163, 184, 255), width=1)
        draw.line([(p2[0], p2[1]), (p2[0], dim_y + (6 if offset > 0 else -6))], fill=(148, 163, 184, 255), width=1)
        draw.line([(x_min, dim_y), (x_max, dim_y)], fill=(30, 41, 59, 255), width=2)
        draw.line([(x_min - tick_len, dim_y + tick_len), (x_min + tick_len, dim_y - tick_len)], fill=(15, 23, 42, 255), width=2)
        draw.line([(x_max - tick_len, dim_y + tick_len), (x_max + tick_len, dim_y - tick_len)], fill=(15, 23, 42, 255), width=2)
        bbox = font_dim_bold.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (x_min + x_max) / 2 - tw / 2
        ty = dim_y + (8 if offset > 0 else -th - 8)
        draw.rectangle([tx - 2, ty - 2, tx + tw + 2, ty + th + 2], fill=(255, 255, 255, 230))
        draw.text((tx, ty), text, fill=(15, 23, 42, 255), font=font_dim_bold)

def draw_wall_rect(draw, x1, y1, x2, y2):
    draw.rectangle([x1, y1, x2, y2], fill=(15, 23, 42, 255))

def draw_door(draw, x_hinge, y_hinge, width_px, direction="SE"):
    leaf_thick = 4
    if direction == "SE":
        draw.line([(x_hinge, y_hinge), (x_hinge, y_hinge + width_px)], fill=(15, 23, 42, 255), width=leaf_thick)
        draw.arc([x_hinge - width_px, y_hinge - width_px, x_hinge + width_px, y_hinge + width_px], 0, 90, fill=(100, 116, 139, 255), width=2)
    elif direction == "SW":
        draw.line([(x_hinge, y_hinge), (x_hinge, y_hinge + width_px)], fill=(15, 23, 42, 255), width=leaf_thick)
        draw.arc([x_hinge - width_px, y_hinge - width_px, x_hinge + width_px, y_hinge + width_px], 90, 180, fill=(100, 116, 139, 255), width=2)
    elif direction == "NE":
        draw.line([(x_hinge, y_hinge), (x_hinge, y_hinge - width_px)], fill=(15, 23, 42, 255), width=leaf_thick)
        draw.arc([x_hinge - width_px, y_hinge - width_px, x_hinge + width_px, y_hinge + width_px], 270, 360, fill=(100, 116, 139, 255), width=2)
    elif direction == "NW":
        draw.line([(x_hinge, y_hinge), (x_hinge, y_hinge - width_px)], fill=(15, 23, 42, 255), width=leaf_thick)
        draw.arc([x_hinge - width_px, y_hinge - width_px, x_hinge + width_px, y_hinge + width_px], 180, 270, fill=(100, 116, 139, 255), width=2)

def draw_window(draw, x1, y1, x2, y2, is_vertical=False):
    draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
    if is_vertical:
        xm = (x1 + x2) / 2
        draw.line([(xm, y1), (xm, y2)], fill=(56, 189, 248, 255), width=2)
    else:
        ym = (y1 + y2) / 2
        draw.line([(x1, ym), (x2, ym)], fill=(56, 189, 248, 255), width=2)

# ==============================================================================
# LAYER 01: TAMPAK DEPAN ARSITEKTUR (ELEVATION VIEW)
# ==============================================================================
print("Drawing Layer 01: Tampak Depan Fasad...")
ELEV_Y_GROUND = 1180.0
ELEV_X0 = 400.0
ELEV_X_MAX = 2000.0

# Ground Line
draw_elev.line([(250, ELEV_Y_GROUND), (2150, ELEV_Y_GROUND)], fill=(15, 23, 42, 255), width=5)
# Ground hatch
for gx in range(250, 2150, 40):
    draw_elev.line([(gx, ELEV_Y_GROUND), (gx - 25, ELEV_Y_GROUND + 25)], fill=(203, 213, 225, 255), width=2)

# --- 1. Left Wing (Apotek / Retail): X = 400 to 940 (width 7.5m) ---
# Ground floor wall
draw_elev.rectangle([400, 880, 940, ELEV_Y_GROUND], fill=(248, 250, 252, 255), outline=(15, 23, 42, 255), width=3)
# Apotek windows and doors
draw_elev.rectangle([430, 940, 680, ELEV_Y_GROUND - 10], fill=(224, 242, 254, 255), outline=(30, 41, 59, 255), width=2)
draw_elev.line([(555, 940), (555, ELEV_Y_GROUND - 10)], fill=(30, 41, 59, 255), width=2)
# Terracotta pitched canopy (IMG_9176_02.jpg)
canopy_poly = [(380, 890), (950, 890), (960, 915), (370, 915)]
draw_elev.polygon(canopy_poly, fill=(194, 65, 12, 255), outline=(15, 23, 42, 255))
# Tile texture on canopy
for tx in range(380, 950, 18):
    draw_elev.line([(tx, 890), (tx - 5, 915)], fill=(154, 52, 18, 255), width=2)

# Second floor wall
draw_elev.rectangle([420, 580, 930, 890], fill=(241, 245, 249, 255), outline=(15, 23, 42, 255), width=3)
# Classical Arch Moldings on 2nd floor (IMG_9176_02.jpg)
draw_elev.arc([520, 620, 680, 780], 180, 360, fill=(100, 116, 139, 255), width=4)
draw_elev.line([(520, 700), (520, 800)], fill=(100, 116, 139, 255), width=3)
draw_elev.line([(680, 700), (680, 800)], fill=(100, 116, 139, 255), width=3)
draw_elev.rectangle([540, 680, 660, 800], fill=(224, 242, 254, 255), outline=(15, 23, 42, 255), width=2)
# Clay tile Hip Roof on top
roof_poly = [(390, 580), (960, 580), (675, 420)]
draw_elev.polygon(roof_poly, fill=(180, 83, 9, 255), outline=(15, 23, 42, 255))
for ry in range(430, 580, 14):
    w_at_y = (ry - 420) / (580 - 420) * (960 - 390) / 2
    draw_elev.line([(675 - w_at_y, ry), (675 + w_at_y, ry)], fill=(146, 64, 14, 255), width=1)

# --- 2. Center Entrance & Canopy: X = 940 to 1264 (width 4.5m) ---
draw_elev.rectangle([940, 860, 1264, ELEV_Y_GROUND], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=3)
# Canopy slab
draw_elev.rectangle([930, 850, 1274, 875], fill=(51, 65, 85, 255), outline=(15, 23, 42, 255), width=2)
# Corporate Signage Board
draw_elev.rectangle([950, 770, 1254, 840], fill=(255, 255, 255, 255), outline=(4, 120, 87, 255), width=3)
# Green Cross Logo
draw_elev.rectangle([965, 785, 995, 825], fill=(4, 120, 87, 255))
draw_elev.rectangle([955, 795, 1005, 815], fill=(4, 120, 87, 255))
draw_elev.text((1015, 782), "PT MAZIYA MEDICAL GLOBAL", fill=(4, 120, 87, 255), font=font_room_title)
draw_elev.text((1015, 810), "DISTRIBUTOR ALKES RESMI (CDAKB)", fill=(30, 41, 59, 255), font=font_room_sub)
# Main glass entrance double doors
draw_elev.rectangle([990, 920, 1214, ELEV_Y_GROUND], fill=(224, 242, 254, 255), outline=(15, 23, 42, 255), width=2)
draw_elev.line([(1102, 920), (1102, ELEV_Y_GROUND)], fill=(15, 23, 42, 255), width=2)
# Handles
draw_elev.line([(1095, 1020), (1095, 1080)], fill=(71, 85, 105, 255), width=4)
draw_elev.line([(1109, 1020), (1109, 1080)], fill=(71, 85, 105, 255), width=4)

# --- 3. Right Wing & Steel Truss Canopy & Staircase: X = 1264 to 2000 (width 10.2m) ---
draw_elev.rectangle([1264, 860, 1588, ELEV_Y_GROUND], fill=(248, 250, 252, 255), outline=(15, 23, 42, 255), width=3)
# Ruang Konseling front window with green curtains (IMG_9189_62s.jpg)
draw_elev.rectangle([1290, 920, 1560, ELEV_Y_GROUND - 20], fill=(224, 242, 254, 255), outline=(15, 23, 42, 255), width=2)
draw_elev.rectangle([1295, 925, 1340, ELEV_Y_GROUND - 25], fill=(5, 150, 105, 200)) # green curtain left
draw_elev.rectangle([1510, 925, 1555, ELEV_Y_GROUND - 25], fill=(5, 150, 105, 200)) # green curtain right

# Steel Frame Structure (IMG_9189_5s.jpg, IMG_9184.JPG)
# Upper metal canopy roof
steel_roof_poly = [(1580, 480), (2020, 430), (2020, 460), (1580, 510)]
draw_elev.polygon(steel_roof_poly, fill=(71, 85, 105, 255), outline=(15, 23, 42, 255))
# Steel Posts
for px in [1600, 1800, 2000]:
    draw_elev.rectangle([px - 5, 490, px + 5, ELEV_Y_GROUND], fill=(30, 41, 59, 255))
# Mezzanine floor steel beam
draw_elev.rectangle([1600, 780, 2000, 800], fill=(51, 65, 85, 255), outline=(15, 23, 42, 255), width=2)
# Mezzanine steel railing
draw_elev.line([(1600, 740), (2000, 740)], fill=(15, 23, 42, 255), width=3)
for rx in range(1610, 2000, 30):
    draw_elev.line([(rx, 740), (rx, 780)], fill=(71, 85, 105, 255), width=2)

# Exterior Black Steel Staircase (IMG_9189_5s.jpg, IMG_9185.JPG)
# Flight 1 ascending from ground X=1860 to X=1720 at landing Y=780
draw_elev.line([(1860, ELEV_Y_GROUND), (1720, 780)], fill=(15, 23, 42, 255), width=5) # lower stringer
draw_elev.line([(1860, ELEV_Y_GROUND - 60), (1720, 720)], fill=(15, 23, 42, 255), width=3) # handrail
# Steps
num_steps = 14
for s in range(num_steps):
    t = s / num_steps
    sx = 1860 - t * (1860 - 1720)
    sy = ELEV_Y_GROUND - t * (ELEV_Y_GROUND - 780)
    draw_elev.line([(sx, sy), (sx - 15, sy)], fill=(15, 23, 42, 255), width=3)
    draw_elev.line([(sx, sy), (sx, sy - 60)], fill=(100, 116, 139, 255), width=1)

# Parked Black Wuling Almaz SUV (B 2528 UOM, IMG_9184.JPG, IMG_9176_02.jpg)
# Positioned in carport: X = 1750 to 1980
car_x1, car_x2 = 1750, 1980
car_y_bot = ELEV_Y_GROUND - 10
# Wheels
draw_elev.rectangle([car_x1 + 15, car_y_bot - 45, car_x1 + 45, car_y_bot], fill=(15, 23, 42, 255))
draw_elev.rectangle([car_x2 - 45, car_y_bot - 45, car_x2 - 15, car_y_bot], fill=(15, 23, 42, 255))
# Body lower
draw_elev.rectangle([car_x1, car_y_bot - 110, car_x2, car_y_bot - 20], fill=(24, 24, 27, 255), outline=(9, 9, 11, 255), width=2)
# Grille & Headlights
draw_elev.rectangle([car_x1 + 25, car_y_bot - 85, car_x2 - 25, car_y_bot - 45], fill=(39, 39, 42, 255))
# Headlights
draw_elev.polygon([(car_x1 + 5, car_y_bot - 95), (car_x1 + 35, car_y_bot - 95), (car_x1 + 25, car_y_bot - 70)], fill=(224, 242, 254, 255), outline=(15, 23, 42, 255))
draw_elev.polygon([(car_x2 - 5, car_y_bot - 95), (car_x2 - 35, car_y_bot - 95), (car_x2 - 25, car_y_bot - 70)], fill=(224, 242, 254, 255), outline=(15, 23, 42, 255))
# License plate
draw_elev.rectangle([car_x1 + 80, car_y_bot - 55, car_x2 - 80, car_y_bot - 35], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=1)
draw_elev.text((car_x1 + 85, car_y_bot - 53), "B 2528 UOM", fill=(0, 0, 0, 255), font=font_kop_sm)
# Windshield & Roof cabin
draw_elev.polygon([(car_x1 + 25, car_y_bot - 110), (car_x1 + 45, car_y_bot - 175), (car_x2 - 45, car_y_bot - 175), (car_x2 - 25, car_y_bot - 110)], fill=(56, 189, 248, 180), outline=(24, 24, 27, 255), width=2)
draw_elev.line([(car_x1 + 45, car_y_bot - 178), (car_x2 - 45, car_y_bot - 178)], fill=(161, 161, 170, 255), width=3) # roof rails

# Red motorcycle parked under staircase (IMG_9184.JPG)
draw_elev.rectangle([1650, car_y_bot - 65, 1710, car_y_bot - 10], fill=(220, 38, 38, 255), outline=(153, 27, 27, 255), width=2)
draw_elev.ellipse([1645, car_y_bot - 35, 1665, car_y_bot], fill=(15, 23, 42, 255))
draw_elev.ellipse([1695, car_y_bot - 35, 1715, car_y_bot], fill=(15, 23, 42, 255))

# Right boundary wall with circular decorative vent (IMG_9184.JPG)
draw_elev.rectangle([2000, 850, 2060, ELEV_Y_GROUND], fill=(226, 232, 240, 255), outline=(15, 23, 42, 255), width=2)
draw_elev.ellipse([2015, 910, 2045, 940], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)

# Scale human figure (1.75m = 126 px)
hx = 330
hy = ELEV_Y_GROUND
draw_elev.ellipse([hx - 7, hy - 126, hx + 7, hy - 108], fill=(100, 116, 139, 255)) # head
draw_elev.line([(hx, hy - 108), (hx, hy - 50)], fill=(100, 116, 139, 255), width=4) # torso
draw_elev.line([(hx, hy - 50), (hx - 10, hy)], fill=(100, 116, 139, 255), width=3) # left leg
draw_elev.line([(hx, hy - 50), (hx + 10, hy)], fill=(100, 116, 139, 255), width=3) # right leg
draw_elev.line([(hx, hy - 95), (hx - 18, hy - 60)], fill=(100, 116, 139, 255), width=3) # arms
draw_elev.line([(hx, hy - 95), (hx + 18, hy - 60)], fill=(100, 116, 139, 255), width=3)
draw_elev.text((hx - 25, hy - 145), "SKALA 1:100", fill=(100, 116, 139, 255), font=font_kop_sm)

# Title for Elevation
draw_elev.text((WIDTH/2 - 250, 360), "TAMPAK DEPAN ARSITEKTUR (ELEVASI UTARA) - SKALA 1:100", fill=(15, 23, 42, 255), font=font_sec_title)
# Elevation Dimension Line 22.20 m
draw_dim_line(draw_elev, (400, ELEV_Y_GROUND), (2000, ELEV_Y_GROUND), "LEBAR FASAD = 22.20 M", offset=45)

# ==============================================================================
# LAYER 02: LANTAI & HATCHES (FLOOR TEXTURES & GRIDS)
# ==============================================================================
print("Drawing Layer 02: Lantai & Hatches...")

# 1. Gudang Utama (15m x 3m): White 40x40cm ceramic tile grid
gudang_x1, gudang_x2 = m2px_x(3.00), m2px_x(18.00)
gudang_y1, gudang_y2 = PLAN_Y_BACK, PLAN_Y_GUDANG_SOUTH
draw_floor.rectangle([gudang_x1, gudang_y1, gudang_x2, gudang_y2], fill=(255, 255, 255, 255))
tile_step = int(0.40 * SCALE) # ~29 px
for x in range(int(gudang_x1), int(gudang_x2), tile_step):
    draw_floor.line([(x, gudang_y1), (x, gudang_y2)], fill=(241, 245, 249, 255), width=1)
for y in range(int(gudang_y1), int(gudang_y2), tile_step):
    draw_floor.line([(gudang_x1, y), (gudang_x2, y)], fill=(241, 245, 249, 255), width=1)

# 2. Zona D Lantai Coklat: Warm wood plank pattern (IMG_9189_78s.jpg)
zd_x1, zd_x2 = m2px_x(7.10), m2px_x(14.00)
zd_y1, zd_y2 = PLAN_Y_GUDANG_SOUTH, PLAN_Y_HALL_DIV
draw_floor.rectangle([zd_x1, zd_y1, zd_x2, zd_y2], fill=(247, 240, 233, 255))
plank_step = int(0.20 * SCALE) # ~14 px
for y in range(int(zd_y1), int(zd_y2), plank_step):
    draw_floor.line([(zd_x1, y), (zd_x2, y)], fill=(212, 163, 115, 120), width=1)
for x in range(int(zd_x1), int(zd_x2), int(1.2 * SCALE)):
    draw_floor.line([(x, zd_y1), (x, zd_y2)], fill=(212, 163, 115, 60), width=1)

# 3. Ruang Direktur & Wadir (1.79m x 2.76m): Parquet texture
dir_x1, dir_x2 = m2px_x(5.31), m2px_x(7.10)
dir_y1, dir_y2 = PLAN_Y_GUDANG_SOUTH, PLAN_Y_DIR_SOUTH
draw_floor.rectangle([dir_x1, dir_y1, dir_x2, dir_y2], fill=(254, 243, 199, 255))
for y in range(int(dir_y1), int(dir_y2), 12):
    draw_floor.line([(dir_x1, y), (dir_x2, y)], fill=(217, 119, 6, 80), width=1)

# 4. Kamar Mandi (2.31m x 2.76m): 20x20cm tile grid
km_x1, km_x2 = m2px_x(3.00), m2px_x(5.31)
km_y1, km_y2 = PLAN_Y_GUDANG_SOUTH, PLAN_Y_DIR_SOUTH
draw_floor.rectangle([km_x1, km_y1, km_x2, km_y2], fill=(240, 249, 255, 255))
km_tile = int(0.20 * SCALE)
for x in range(int(km_x1), int(km_x2), km_tile):
    draw_floor.line([(x, km_y1), (x, km_y2)], fill=(186, 230, 253, 255), width=1)
for y in range(int(km_y1), int(km_y2), km_tile):
    draw_floor.line([(km_x1, y), (km_x2, y)], fill=(186, 230, 253, 255), width=1)

# 5. Ruang PJT & Buffer Alkes (Eks Konseling): Clean Vinyl
pjt_x1, pjt_x2 = m2px_x(10.00), m2px_x(16.50)
pjt_y1, pjt_y2 = PLAN_Y_HALL_DIV, PLAN_Y_FACADE
draw_floor.rectangle([pjt_x1, pjt_y1, pjt_x2, pjt_y2], fill=(248, 250, 252, 255))

# 6. Lobby & Apotek Resepsi
lobby_x1, lobby_x2 = m2px_x(0.00), m2px_x(10.00)
lobby_y1, lobby_y2 = PLAN_Y_HALL_DIV, PLAN_Y_FACADE
draw_floor.rectangle([lobby_x1, lobby_y1, lobby_x2, lobby_y2], fill=(255, 255, 255, 255))
lobby_tile = int(0.60 * SCALE)
for x in range(int(lobby_x1), int(lobby_x2), lobby_tile):
    draw_floor.line([(x, lobby_y1), (x, lobby_y2)], fill=(226, 232, 240, 255), width=1)
for y in range(int(lobby_y1), int(lobby_y2), lobby_tile):
    draw_floor.line([(lobby_x1, y), (lobby_x2, y)], fill=(226, 232, 240, 255), width=1)

# 7. Carport Forecourt (9.30m depth): Concrete Paving Hatch
cp_x1, cp_x2 = m2px_x(0.00), m2px_x(22.20)
cp_y1, cp_y2 = PLAN_Y_FACADE, PLAN_Y_FRONT_GATE
draw_floor.rectangle([cp_x1, cp_y1, cp_x2, cp_y2], fill=(241, 245, 249, 255))
pave_step = int(0.80 * SCALE)
for x in range(int(cp_x1), int(cp_x2), pave_step):
    draw_floor.line([(x, cp_y1), (x, cp_y2)], fill=(203, 213, 225, 120), width=1)
for y in range(int(cp_y1), int(cp_y2), pave_step):
    draw_floor.line([(cp_x1, y), (cp_x2, y)], fill=(203, 213, 225, 120), width=1)

# ==============================================================================
# LAYER 03: DINDING SOLID HITAM (SOLID BLACK CAD WALLS)
# ==============================================================================
print("Drawing Layer 03: Dinding Solid Hitam...")
# Wall thickness = 11 px
WT = WALL_THICK

# 1. Outer North Boundary Wall of Gudang (15m span, X=3.0 to 18.0)
draw_wall_rect(draw_wall, m2px_x(3.00), PLAN_Y_BACK, m2px_x(18.00), PLAN_Y_BACK + WT)
# 2. West Wall of Gudang (X=3.00, Y=1500 to 1716)
draw_wall_rect(draw_wall, m2px_x(3.00), PLAN_Y_BACK, m2px_x(3.00) + WT, PLAN_Y_GUDANG_SOUTH + WT)
# 3. East Wall of Gudang (X=18.00, Y=1500 to 1716)
draw_wall_rect(draw_wall, m2px_x(18.00) - WT, PLAN_Y_BACK, m2px_x(18.00), PLAN_Y_GUDANG_SOUTH + WT)

# 4. Gudang South Wall (Y = 1716, X=3.0 to 18.0)
# Cutouts:
# Door: X = 7.10 to 8.10 (width 1.00m)
# Bukaan Pass-Through: X = 9.80 to 11.40 (width 1.60m)
draw_wall_rect(draw_wall, m2px_x(3.00), PLAN_Y_GUDANG_SOUTH, m2px_x(7.10), PLAN_Y_GUDANG_SOUTH + WT)
draw_wall_rect(draw_wall, m2px_x(8.10), PLAN_Y_GUDANG_SOUTH, m2px_x(9.80), PLAN_Y_GUDANG_SOUTH + WT)
draw_wall_rect(draw_wall, m2px_x(11.40), PLAN_Y_GUDANG_SOUTH, m2px_x(18.00), PLAN_Y_GUDANG_SOUTH + WT)

# 5. Restroom / KM Walls:
# West wall: X = 3.00, Y = 1716 to 1914.7
draw_wall_rect(draw_wall, m2px_x(3.00), PLAN_Y_GUDANG_SOUTH, m2px_x(3.00) + WT, PLAN_Y_DIR_SOUTH + WT)
# Dividing wall between KM and Direktur: X = 5.31, Y = 1716 to 1914.7
draw_wall_rect(draw_wall, m2px_x(5.31) - WT/2, PLAN_Y_GUDANG_SOUTH, m2px_x(5.31) + WT/2, PLAN_Y_DIR_SOUTH + WT)
# South wall of KM (with door cutout X=4.40 to 5.20)
draw_wall_rect(draw_wall, m2px_x(3.00), PLAN_Y_DIR_SOUTH, m2px_x(4.40), PLAN_Y_DIR_SOUTH + WT)

# 6. Director Office Walls (Exact: 1.79m x 2.76m):
# East wall separating Direktur from Hallway: X = 7.10, Y = 1716 to 1914.7
draw_wall_rect(draw_wall, m2px_x(7.10) - WT, PLAN_Y_GUDANG_SOUTH, m2px_x(7.10), PLAN_Y_DIR_SOUTH + WT)
# South wall of Direktur (with door cutout X=6.10 to 6.90)
draw_wall_rect(draw_wall, m2px_x(5.31), PLAN_Y_DIR_SOUTH, m2px_x(6.10), PLAN_Y_DIR_SOUTH + WT)

# 7. Hallway & Zona D Divider Wall (Y = 1989.6):
draw_wall_rect(draw_wall, m2px_x(0.00), PLAN_Y_HALL_DIV, m2px_x(7.50), PLAN_Y_HALL_DIV + WT)
draw_wall_rect(draw_wall, m2px_x(8.80), PLAN_Y_HALL_DIV, m2px_x(16.50), PLAN_Y_HALL_DIV + WT)

# 8. Ruang PJT (Eks Konseling) Walls:
# West wall: X = 10.00, Y = 1989.6 to 2407.2
draw_wall_rect(draw_wall, m2px_x(10.00) - WT, PLAN_Y_HALL_DIV, m2px_x(10.00), PLAN_Y_FACADE + WT)
# East wall: X = 16.50, Y = 1989.6 to 2407.2
draw_wall_rect(draw_wall, m2px_x(16.50) - WT, PLAN_Y_HALL_DIV, m2px_x(16.50), PLAN_Y_FACADE + WT)
# South wall (with door cutout X=10.00 to 11.00, window cutout X=11.60 to 16.00)
draw_wall_rect(draw_wall, m2px_x(11.00), PLAN_Y_FACADE, m2px_x(11.60), PLAN_Y_FACADE + WT)
draw_wall_rect(draw_wall, m2px_x(16.00), PLAN_Y_FACADE, m2px_x(16.50), PLAN_Y_FACADE + WT)

# 9. Main Front Facade Wall (Y = 2407.2):
# Left wing: X = 0.00 to 10.00 (with main double door cutout X=8.20 to 9.80, window cutout X=1.50 to 5.50)
draw_wall_rect(draw_wall, m2px_x(0.00), PLAN_Y_FACADE, m2px_x(1.50), PLAN_Y_FACADE + WT)
draw_wall_rect(draw_wall, m2px_x(5.50), PLAN_Y_FACADE, m2px_x(8.20), PLAN_Y_FACADE + WT)

# 10. Perimeter Carport Walls:
draw_wall_rect(draw_wall, m2px_x(0.00), PLAN_Y_FACADE, m2px_x(0.00) + WT, PLAN_Y_FRONT_GATE) # West property wall
draw_wall_rect(draw_wall, m2px_x(22.20) - WT, PLAN_Y_FACADE, m2px_x(22.20), PLAN_Y_FRONT_GATE) # East property wall with round vent

# ==============================================================================
# LAYER 04: PINTU & JENDELA BUKAAN (DOORS, WINDOWS, OPENINGS)
# ==============================================================================
print("Drawing Layer 04: Pintu & Jendela...")

# 1. Gudang Access Door (Wooden panel with loster, IMG_9189_85s.jpg)
# At X = 7.10, Y = 1716, width 1.00m (72px), swings NE into warehouse
draw_door(draw_opening, m2px_x(7.10), PLAN_Y_GUDANG_SOUTH, int(1.00 * SCALE), direction="NE")

# 2. Pass-Through Opening Counter (Bukaan dinding counter, IMG_9180.JPG)
# At X = 9.80 to 11.40 (1.60m)
draw_window(draw_opening, m2px_x(9.80), PLAN_Y_GUDANG_SOUTH - 2, m2px_x(11.40), PLAN_Y_GUDANG_SOUTH + WT + 2)
# Wooden credenza symbol inside opening
draw_opening.rectangle([m2px_x(9.85), PLAN_Y_GUDANG_SOUTH - 10, m2px_x(11.35), PLAN_Y_GUDANG_SOUTH + 20], fill=(217, 119, 6, 200), outline=(146, 64, 14, 255), width=2)
draw_opening.text((m2px_x(9.90), PLAN_Y_GUDANG_SOUTH - 8), "PASS-THROUGH", fill=(255, 255, 255, 255), font=font_kop_sm)

# 3. Director Office Door (X = 6.10, Y = 1914.7, swings NW into office)
draw_door(draw_opening, m2px_x(6.10), PLAN_Y_DIR_SOUTH, int(0.80 * SCALE), direction="NW")

# 4. Restroom Door (X = 4.40, Y = 1914.7, swings NW into bathroom)
draw_door(draw_opening, m2px_x(4.40), PLAN_Y_DIR_SOUTH, int(0.80 * SCALE), direction="NW")

# 5. Ruang PJT Front Glass Door (Frosted glass with sign, IMG_9189_53s.jpg)
# At X = 10.00, Y = 2407.2, swings NE into room
draw_door(draw_opening, m2px_x(10.00), PLAN_Y_FACADE, int(1.00 * SCALE), direction="NE")

# 6. Main Double Glass Entrance Doors
draw_door(draw_opening, m2px_x(8.20), PLAN_Y_FACADE, int(0.80 * SCALE), direction="NW")
draw_door(draw_opening, m2px_x(9.80), PLAN_Y_FACADE, int(0.80 * SCALE), direction="NE")

# 7. Windows:
# Apotek front window
draw_window(draw_opening, m2px_x(1.50), PLAN_Y_FACADE, m2px_x(5.50), PLAN_Y_FACADE + WT)
# Ruang PJT front window (with green privacy curtains, IMG_9189_62s.jpg)
draw_window(draw_opening, m2px_x(11.60), PLAN_Y_FACADE, m2px_x(16.00), PLAN_Y_FACADE + WT)
# Green curtain symbols
draw_opening.rectangle([m2px_x(11.70), PLAN_Y_FACADE - 15, m2px_x(12.40), PLAN_Y_FACADE], fill=(5, 150, 105, 220))
draw_opening.rectangle([m2px_x(15.20), PLAN_Y_FACADE - 15, m2px_x(15.90), PLAN_Y_FACADE], fill=(5, 150, 105, 220))

# ==============================================================================
# LAYER 05: FURNITUR & PERALATAN 2D (2D ARCHITECTURAL SYMBOLS)
# ==============================================================================
print("Drawing Layer 05: Furnitur & Peralatan 2D...")

# --- A. GUDANG UTAMA CDAKB (15.00m x 3.00m) ---
# 1. Double Stainless Sink Counter (West side, IMG_9179.JPG)
sink_x1, sink_x2 = m2px_x(3.80), m2px_x(5.40)
sink_y1, sink_y2 = PLAN_Y_GUDANG_SOUTH - 45, PLAN_Y_GUDANG_SOUTH - 5
draw_furn.rectangle([sink_x1, sink_y1, sink_x2, sink_y2], fill=(226, 232, 240, 255), outline=(15, 23, 42, 255), width=2)
# Two sink bowls
draw_furn.rectangle([sink_x1 + 10, sink_y1 + 8, sink_x1 + 50, sink_y2 - 8], fill=(203, 213, 225, 255), outline=(71, 85, 105, 255), width=1)
draw_furn.rectangle([sink_x1 + 60, sink_y1 + 8, sink_x1 + 100, sink_y2 - 8], fill=(203, 213, 225, 255), outline=(71, 85, 105, 255), width=1)
# Water gallon & Pink step bin
draw_furn.ellipse([sink_x2 + 10, sink_y1 + 10, sink_x2 + 35, sink_y2 - 10], fill=(56, 189, 248, 255), outline=(15, 23, 42, 255), width=1)
draw_furn.rectangle([sink_x2 + 40, sink_y1 + 10, sink_x2 + 65, sink_y2 - 10], fill=(244, 63, 94, 255), outline=(15, 23, 42, 255), width=1)

# 2. Red Locked Quarantine Cabinet (Karantina Alkes) in West Recess
karan_x1, karan_x2 = m2px_x(3.20), m2px_x(4.00)
karan_y1, karan_y2 = PLAN_Y_BACK + 15, PLAN_Y_BACK + 60
draw_furn.rectangle([karan_x1, karan_y1, karan_x2, karan_y2], fill=(254, 226, 226, 255), outline=(220, 38, 38, 255), width=2)
draw_furn.line([(karan_x1, karan_y1), (karan_x2, karan_y2)], fill=(220, 38, 38, 255), width=1)
draw_furn.line([(karan_x1, karan_y2), (karan_x2, karan_y1)], fill=(220, 38, 38, 255), width=1)
draw_furn.text((karan_x1 - 10, karan_y2 + 4), "KARANTINA", fill=(220, 38, 38, 255), font=font_kop_sm)

# 3. 5 Heavy-Duty Slotted Angle Racks (Rak Besi Siku, IMG_9189_95s.jpg)
# Spaced along north wall with 30cm clearance from wall
rack_xs = [6.20, 8.40, 10.60, 12.80, 15.00]
rack_w = int(1.20 * SCALE) # 86 px
rack_d = int(0.50 * SCALE) # 36 px
rack_y = PLAN_Y_BACK + int(0.25 * SCALE)
for rx in rack_xs:
    px = m2px_x(rx)
    draw_furn.rectangle([px, rack_y, px + rack_w, rack_y + rack_d], fill=(241, 245, 249, 255), outline=(30, 41, 59, 255), width=2)
    # Shelf divider and cross braces
    draw_furn.line([(px, rack_y + rack_d/2), (px + rack_w, rack_y + rack_d/2)], fill=(148, 163, 184, 255), width=1)
    # Corner posts
    for cpx in [px, px + rack_w - 6]:
        for cpy in [rack_y, rack_y + rack_d - 6]:
            draw_furn.rectangle([cpx, cpy, cpx + 6, cpy + 6], fill=(15, 23, 42, 255))
    draw_furn.text((px + 10, rack_y + 10), "RAK ALKES", fill=(71, 85, 105, 255), font=font_kop_sm)

# 4. Non-Porous Cargo Pallets on floor (1.2m x 1.0m)
pallet_xs = [7.20, 10.00, 12.50]
pallet_w = int(1.20 * SCALE)
pallet_h = int(1.00 * SCALE)
pallet_y = int(PLAN_Y_GUDANG_SOUTH - pallet_h - 20)
for px in pallet_xs:
    x = m2px_x(px)
    draw_furn.rectangle([x, pallet_y, x + pallet_w, pallet_y + pallet_h], fill=(254, 243, 199, 200), outline=(180, 83, 9, 255), width=2)
    # Pallet boards
    for by in range(int(pallet_y + 10), int(pallet_y + pallet_h), 15):
        draw_furn.line([(x, by), (x + pallet_w, by)], fill=(217, 119, 6, 255), width=1)
    draw_furn.text((x + 15, pallet_y + 25), "PALLET STAGING", fill=(146, 64, 14, 255), font=font_kop_sm)

# 5. Green 3-Seater Leather Sofa ("Mentok Sofa Hijau", IMG_9189_105s.jpg)
# Positioned at east end: X = 16.50 to 17.80, Y = 1530 to 1690
sofa_x1, sofa_x2 = m2px_x(16.50), m2px_x(17.80)
sofa_y1, sofa_y2 = PLAN_Y_BACK + 30, PLAN_Y_GUDANG_SOUTH - 30
draw_furn.rectangle([sofa_x1, sofa_y1, sofa_x2, sofa_y2], fill=(16, 185, 129, 220), outline=(4, 120, 87, 255), width=3)
# 3 Cushions
cush_h = (sofa_y2 - sofa_y1) / 3
for i in range(3):
    cy1 = sofa_y1 + i * cush_h
    cy2 = cy1 + cush_h
    draw_furn.rectangle([sofa_x1 + 15, cy1 + 4, sofa_x2 - 5, cy2 - 4], fill=(5, 150, 105, 255), outline=(4, 120, 87, 255), width=2)
# Backrest
draw_furn.rectangle([sofa_x1, sofa_y1, sofa_x1 + 15, sofa_y2], fill=(4, 120, 87, 255))
draw_furn.text((sofa_x1 - 5, sofa_y2 + 8), "SOFA HIJAU (REST AREA)", fill=(4, 120, 87, 255), font=font_kop_sm)

# 6. CDAKB Sensors & Maspion Exhaust Fan
# Exhaust fan on North wall (IMG_9181.JPG)
draw_furn.rectangle([m2px_x(11.00), PLAN_Y_BACK - 8, m2px_x(11.60), PLAN_Y_BACK + WT + 4], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.ellipse([m2px_x(11.10), PLAN_Y_BACK - 4, m2px_x(11.50), PLAN_Y_BACK + WT], fill=(56, 189, 248, 255))
draw_furn.text((m2px_x(11.00) - 20, PLAN_Y_BACK - 26), "EXHAUST FAN", fill=(15, 23, 42, 255), font=font_kop_sm)
# AC Split on back wall
draw_furn.rectangle([m2px_x(7.50), PLAN_Y_BACK, m2px_x(8.70), PLAN_Y_BACK + 15], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.text((m2px_x(7.50), PLAN_Y_BACK - 20), "AC SPLIT 2 PK", fill=(15, 23, 42, 255), font=font_kop_sm)
# Digital Thermo-Hygrometer & APAR
draw_furn.ellipse([m2px_x(8.20), PLAN_Y_GUDANG_SOUTH - 25, m2px_x(8.20) + 18, PLAN_Y_GUDANG_SOUTH - 7], fill=(220, 38, 38, 255))
draw_furn.text((m2px_x(8.20) + 24, PLAN_Y_GUDANG_SOUTH - 22), "APAR 6KG", fill=(220, 38, 38, 255), font=font_kop_sm)
draw_furn.rectangle([m2px_x(13.50), PLAN_Y_BACK + 2, m2px_x(13.80), PLAN_Y_BACK + 14], fill=(59, 130, 246, 255))
draw_furn.text((m2px_x(13.40), PLAN_Y_BACK - 20), "THERMOHYGROMETER", fill=(37, 99, 235, 255), font=font_kop_sm)

# --- B. RUANG DIREKTUR & WAKIL DIREKTUR (1.79m x 2.76m) ---
# Executive L-Desk and Chairs
desk_x1, desk_x2 = m2px_x(5.45), m2px_x(6.85)
desk_y1, desk_y2 = PLAN_Y_GUDANG_SOUTH + 20, PLAN_Y_GUDANG_SOUTH + 75
draw_furn.rectangle([desk_x1, desk_y1, desk_x2, desk_y2], fill=(217, 119, 6, 220), outline=(146, 64, 14, 255), width=2)
# Executive Swivel Chairs (Direktur & Wadir)
for cx in [desk_x1 + 25, desk_x2 - 25]:
    draw_furn.ellipse([cx - 15, desk_y1 - 25, cx + 15, desk_y1 + 5], fill=(30, 41, 59, 255))
    draw_furn.arc([cx - 20, desk_y1 - 30, cx + 20, desk_y1 + 10], 180, 360, fill=(15, 23, 42, 255), width=3)
# Visitor chair
draw_furn.ellipse([(desk_x1 + desk_x2)/2 - 12, desk_y2 + 10, (desk_x1 + desk_x2)/2 + 12, desk_y2 + 34], fill=(71, 85, 105, 255))
# Jati Carved Calligraphy Art symbol on North wall (IMG_9191_06.jpg)
draw_furn.rectangle([desk_x1 + 20, PLAN_Y_GUDANG_SOUTH + 2, desk_x2 - 20, PLAN_Y_GUDANG_SOUTH + 8], fill=(180, 83, 9, 255))
draw_furn.text((desk_x1 + 10, PLAN_Y_DIR_SOUTH - 40), "MEJA DIREKSI", fill=(146, 64, 14, 255), font=font_kop_sm)

# --- C. KAMAR MANDI / RESTROOM ---
# Seated flush toilet (IMG_9191_02.jpg)
wc_x = m2px_x(3.80)
wc_y = PLAN_Y_GUDANG_SOUTH + 20
draw_furn.rectangle([wc_x - 18, wc_y, wc_x + 18, wc_y + 18], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2) # tank
draw_furn.ellipse([wc_x - 15, wc_y + 12, wc_x + 15, wc_y + 52], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2) # bowl
# Washbasin
draw_furn.rectangle([m2px_x(4.70), PLAN_Y_GUDANG_SOUTH + 15, m2px_x(5.20), PLAN_Y_GUDANG_SOUTH + 45], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.ellipse([m2px_x(4.80), PLAN_Y_GUDANG_SOUTH + 20, m2px_x(5.10), PLAN_Y_GUDANG_SOUTH + 40], fill=(224, 242, 254, 255), outline=(71, 85, 105, 255), width=1)

# --- D. ZONA D: QC & AKL STAGING (LANTAI COKLAT) ---
# QC Inspection table (1.50m x 0.80m) placed cleanly on left
qc_x1, qc_x2 = m2px_x(7.50), m2px_x(9.30)
qc_y1, qc_y2 = PLAN_Y_GUDANG_SOUTH + 110, PLAN_Y_GUDANG_SOUTH + 175
draw_furn.rectangle([qc_x1, qc_y1, qc_x2, qc_y2], fill=(241, 245, 249, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.text((qc_x1 + 15, qc_y1 + 22), "MEJA QC & SAMPLING", fill=(30, 41, 59, 255), font=font_kop_sm)
# Barcode printer station placed on right
draw_furn.rectangle([m2px_x(12.00), PLAN_Y_GUDANG_SOUTH + 110, m2px_x(13.40), PLAN_Y_GUDANG_SOUTH + 170], fill=(226, 232, 240, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.text((m2px_x(12.10), PLAN_Y_GUDANG_SOUTH + 130), "PRINTER AKL", fill=(30, 41, 59, 255), font=font_kop_sm)

# --- E. RUANG PJT & BUFFER ALKES (EKS KONSELING) ---
# Consultation workstation
pjt_w_x1, pjt_w_x2 = m2px_x(10.50), m2px_x(12.20)
pjt_w_y1, pjt_w_y2 = PLAN_Y_HALL_DIV + 40, PLAN_Y_HALL_DIV + 95
draw_furn.rectangle([pjt_w_x1, pjt_w_y1, pjt_w_x2, pjt_w_y2], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.ellipse([(pjt_w_x1 + pjt_w_x2)/2 - 15, pjt_w_y1 - 25, (pjt_w_x1 + pjt_w_x2)/2 + 15, pjt_w_y1 + 5], fill=(30, 41, 59, 255))
draw_furn.text((pjt_w_x1 + 10, pjt_w_y1 + 20), "WORKSTATION PJT", fill=(15, 23, 42, 255), font=font_kop_sm)

# Medical Examination Bed (Ranjang Periksa, IMG_9192_02.jpg)
bed_x1, bed_x2 = m2px_x(14.00), m2px_x(16.20)
bed_y1, bed_y2 = PLAN_Y_HALL_DIV + 30, PLAN_Y_HALL_DIV + 100
draw_furn.rectangle([bed_x1, bed_y1, bed_x2, bed_y2], fill=(248, 250, 252, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.rectangle([bed_x1 + 5, bed_y1 + 5, bed_x1 + 35, bed_y2 - 5], fill=(226, 232, 240, 255), outline=(100, 116, 139, 255), width=1) # pillow
draw_furn.text((bed_x1 + 45, bed_y1 + 25), "RANJANG PERIKSA", fill=(71, 85, 105, 255), font=font_kop_sm)

# Cold-Chain Pharmaceutical Refrigerator (IMG_9192_12.jpg)
fridge_x1, fridge_x2 = m2px_x(14.80), m2px_x(15.80)
fridge_y1, fridge_y2 = PLAN_Y_FACADE - 70, PLAN_Y_FACADE - 15
draw_furn.rectangle([fridge_x1, fridge_y1, fridge_x2, fridge_y2], fill=(136, 19, 55, 220), outline=(76, 5, 25, 255), width=2)
draw_furn.text((fridge_x1 - 10, fridge_y1 - 16), "KULKAS 2-8°C", fill=(136, 19, 55, 255), font=font_kop_sm)

# Locked Medicine Cabinet (IMG_9192_22.jpg)
draw_furn.rectangle([m2px_x(10.20), PLAN_Y_FACADE - 55, m2px_x(10.80), PLAN_Y_FACADE - 15], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.text((m2px_x(10.10), PLAN_Y_FACADE - 70), "LEMARI OBAT", fill=(15, 23, 42, 255), font=font_kop_sm)

# --- F. LOBBY & APOTEK RESEPSI ---
# Pharmacy wall storage cabinets on West wall
for cab_y in [PLAN_Y_HALL_DIV + 50, PLAN_Y_HALL_DIV + 160, PLAN_Y_HALL_DIV + 270]:
    draw_furn.rectangle([m2px_x(0.30), cab_y, m2px_x(1.20), cab_y + 80], fill=(241, 245, 249, 255), outline=(71, 85, 105, 255), width=2)
    draw_furn.line([(m2px_x(0.75), cab_y), (m2px_x(0.75), cab_y + 80)], fill=(148, 163, 184, 255), width=1)
    draw_furn.text((m2px_x(0.35), cab_y + 30), "RAK OBAT", fill=(100, 116, 139, 255), font=font_kop_sm)

# L-Shaped Service & Pharmacy Display Counter
draw_furn.rectangle([m2px_x(2.00), PLAN_Y_HALL_DIV + 60, m2px_x(6.50), PLAN_Y_HALL_DIV + 105], fill=(241, 245, 249, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.rectangle([m2px_x(5.50), PLAN_Y_HALL_DIV + 105, m2px_x(6.50), PLAN_Y_FACADE - 80], fill=(241, 245, 249, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.text((m2px_x(2.20), PLAN_Y_HALL_DIV + 75), "COUNTER VITRINE APOTEK", fill=(15, 23, 42, 255), font=font_kop_sm)
# Visitor waiting chairs
for wx in [m2px_x(1.80), m2px_x(2.80), m2px_x(3.80)]:
    draw_furn.rectangle([wx, PLAN_Y_FACADE - 60, wx + 30, PLAN_Y_FACADE - 25], fill=(226, 232, 240, 255), outline=(15, 23, 42, 255), width=1)

# Canopy roof projection lines (dashed) in Carport
canopy_y_left = PLAN_Y_FACADE + int(1.50 * SCALE)
for cx in range(int(m2px_x(0.00)), int(m2px_x(7.50)), 16):
    draw_opening.line([(cx, canopy_y_left), (cx + 10, canopy_y_left)], fill=(148, 163, 184, 255), width=2)
draw_opening.text((m2px_x(1.00), canopy_y_left + 4), "TRITISAN KANOPI GENTENG 1.5M", fill=(100, 116, 139, 255), font=font_kop_sm)

canopy_y_right = PLAN_Y_FACADE + int(4.00 * SCALE)
for cx in range(int(m2px_x(16.50)), int(m2px_x(22.20)), 16):
    draw_opening.line([(cx, canopy_y_right), (cx + 10, canopy_y_right)], fill=(148, 163, 184, 255), width=2)
draw_opening.text((m2px_x(16.80), canopy_y_right + 4), "TRITISAN KANOPI BAJA 4.0M", fill=(100, 116, 139, 255), font=font_kop_sm)

# --- G. CARPORT & EXTERIOR STEEL STAIRCASE (9.30m Depth) ---
# Exterior Black Steel Staircase (IMG_9189_5s.jpg, IMG_9184.JPG)
# Flight from X=17.50 to 19.50, Y = 2420 to 2700
stair_x1, stair_x2 = m2px_x(17.50), m2px_x(19.80)
stair_y1, stair_y2 = PLAN_Y_FACADE + 20, PLAN_Y_FACADE + int(3.50 * SCALE)
draw_furn.rectangle([stair_x1, stair_y1, stair_x2, stair_y2], fill=(248, 250, 252, 255), outline=(15, 23, 42, 255), width=2)
# Stair treads
num_treads = 10
stair_step = (stair_y2 - stair_y1) / num_treads
for i in range(num_treads):
    sy = stair_y1 + i * stair_step
    draw_furn.line([(stair_x1, sy), (stair_x2, sy)], fill=(30, 41, 59, 255), width=2)
# Direction Arrow "UP"
arr_x = (stair_x1 + stair_x2) / 2
draw_furn.line([(arr_x, stair_y2 - 20), (arr_x, stair_y1 + 25)], fill=(220, 38, 38, 255), width=3)
draw_furn.line([(arr_x - 8, stair_y1 + 40), (arr_x, stair_y1 + 25)], fill=(220, 38, 38, 255), width=3)
draw_furn.line([(arr_x + 8, stair_y1 + 40), (arr_x, stair_y1 + 25)], fill=(220, 38, 38, 255), width=3)
draw_furn.text((arr_x - 12, stair_y2 - 15), "NAIK", fill=(220, 38, 38, 255), font=font_kop_sm)

# 2D Top-View Silhouette of Black Wuling Almaz SUV (IMG_9184.JPG, B 2528 UOM)
# Car length = ~4.65m (335 px), width = ~1.85m (133 px)
car_w = int(1.85 * SCALE)
car_l = int(4.65 * SCALE)
cx1 = m2px_x(11.50)
cy1 = PLAN_Y_FACADE + int(2.50 * SCALE)
cx2 = cx1 + car_w
cy2 = cy1 + car_l

# Outer car body
draw_furn.rectangle([cx1, cy1, cx2, cy2], fill=(24, 24, 27, 255), outline=(9, 9, 11, 255), width=2)
# Tires
tire_w, tire_l = 14, 45
draw_furn.rectangle([cx1 - 6, cy1 + 40, cx1 + 8, cy1 + 40 + tire_l], fill=(0, 0, 0, 255))
draw_furn.rectangle([cx2 - 8, cy1 + 40, cx2 + 6, cy1 + 40 + tire_l], fill=(0, 0, 0, 255))
draw_furn.rectangle([cx1 - 6, cy2 - 85, cx1 + 8, cy2 - 85 + tire_l], fill=(0, 0, 0, 255))
draw_furn.rectangle([cx2 - 8, cy2 - 85, cx2 + 6, cy2 - 85 + tire_l], fill=(0, 0, 0, 255))
# Windshield front
draw_furn.polygon([(cx1 + 15, cy1 + 90), (cx2 - 15, cy1 + 90), (cx2 - 25, cy1 + 135), (cx1 + 25, cy1 + 135)], fill=(56, 189, 248, 220), outline=(15, 23, 42, 255), width=1)
# Rear windshield
draw_furn.polygon([(cx1 + 20, cy2 - 50), (cx2 - 20, cy2 - 50), (cx2 - 25, cy2 - 85), (cx1 + 25, cy2 - 85)], fill=(56, 189, 248, 220), outline=(15, 23, 42, 255), width=1)
# Sunroof
draw_furn.rectangle([cx1 + 35, cy1 + 150, cx2 - 35, cy1 + 215], fill=(39, 39, 42, 255), outline=(113, 113, 122, 255), width=1)
# Text label on car roof
draw_furn.text((cx1 + 22, cy1 + 230), "WULING ALMAZ", fill=(255, 255, 255, 255), font=font_kop_sm)
draw_furn.text((cx1 + 25, cy1 + 250), "B 2528 UOM", fill=(255, 255, 255, 255), font=font_kop_sm)

# Motorcycle top-view
mc_x = m2px_x(17.80)
mc_y = PLAN_Y_FACADE + int(5.50 * SCALE)
draw_furn.ellipse([mc_x, mc_y, mc_x + 22, mc_y + 80], fill=(220, 38, 38, 255), outline=(15, 23, 42, 255), width=2)
draw_furn.line([(mc_x - 10, mc_y + 20), (mc_x + 32, mc_y + 20)], fill=(15, 23, 42, 255), width=3) # handlebars
draw_furn.text((mc_x - 10, mc_y + 90), "MOTOR", fill=(71, 85, 105, 255), font=font_kop_sm)

# ==============================================================================
# LAYER 06: LABEL RUANGAN & ELEVASI
# ==============================================================================
print("Drawing Layer 06: Label Ruangan & Elevasi...")

def add_room_label(draw, text_title, text_elev, text_dim, cx, cy):
    b1 = font_room_title.getbbox(text_title)
    w1, h1 = b1[2] - b1[0], b1[3] - b1[1]
    b2 = font_room_sub.getbbox(text_elev)
    w2, h2 = b2[2] - b2[0], b2[3] - b2[1]
    b3 = font_kop_sm.getbbox(text_dim)
    w3, h3 = b3[2] - b3[0], b3[3] - b3[1]
    
    max_w = max(w1, w2, w3) + 24
    total_h = h1 + h2 + h3 + 24
    # background plate
    draw.rectangle([cx - max_w/2, cy - total_h/2, cx + max_w/2, cy + total_h/2], fill=(255, 255, 255, 240), outline=(203, 213, 225, 255), width=1)
    draw.text((cx - w1/2, cy - total_h/2 + 4), text_title, fill=(15, 23, 42, 255), font=font_room_title)
    draw.text((cx - w2/2, cy - total_h/2 + 8 + h1), text_elev, fill=(4, 120, 87, 255), font=font_room_sub)
    draw.text((cx - w3/2, cy - total_h/2 + 12 + h1 + h2), text_dim, fill=(71, 85, 105, 255), font=font_kop_sm)

# 1. Gudang Utama CDAKB
add_room_label(draw_label, "GUDANG UTAMA CDAKB", "ELEVASI ±0.00", "15.00 M × 3.00 M | TINGGI: 3.00 M", m2px_x(10.50), PLAN_Y_BACK + 140)
# 2. Ruang Direktur & Wadir
add_room_label(draw_label, "RUANG DIREKSI", "ELEVASI ±0.00", "1.79 M × 2.76 M", m2px_x(6.20), (PLAN_Y_GUDANG_SOUTH + PLAN_Y_DIR_SOUTH)/2 + 25)
# 3. Kamar Mandi / Toilet
add_room_label(draw_label, "KM / TOILET", "ELEVASI -0.05", "2.31 M × 2.76 M", m2px_x(4.15), (PLAN_Y_GUDANG_SOUTH + PLAN_Y_DIR_SOUTH)/2 + 25)
# 4. Zona D: QC & AKL Staging
add_room_label(draw_label, "ZONA D: QC & STAGING AKL", "ELEVASI ±0.00", "LANTAI COKLAT | VERIFIKASI BARCODE", m2px_x(10.80), PLAN_Y_GUDANG_SOUTH + 55)
# 5. Ruang PJT & Buffer Alkes
add_room_label(draw_label, "RUANG PJT & BUFFER ALKES", "ELEVASI ±0.00", "EKS KONSELING | SAMPLING & COLD CHAIN", m2px_x(13.25), (PLAN_Y_HALL_DIV + PLAN_Y_FACADE)/2)
# 6. Lobby & Apotek Resepsi
add_room_label(draw_label, "LOBBY & RESEPSI APOTEK", "ELEVASI ±0.00", "PELAYANAN & PENERIMAAN TAMU", m2px_x(5.00), (PLAN_Y_HALL_DIV + PLAN_Y_FACADE)/2)
# 7. Carport Forecourt
add_room_label(draw_label, "CARPORT FORECOURT & STAGING", "ELEVASI -0.10", "KEDALAMAN 9.30 M | PARKIR OPERASIONAL", m2px_x(5.50), PLAN_Y_FACADE + int(4.50 * SCALE))

# ==============================================================================
# LAYER 07: DIMENSI CAD & NOTASI (4 SIDES & NORTH ARROW)
# ==============================================================================
print("Drawing Layer 07: Dimensi CAD & Notasi...")

# --- LEFT DIMENSION STRING (Depth segments) ---
# Witness reference: X = m2px_x(3.00) = 616
# Offset 1: Sub-dimensions (offset = -120)
draw_dim_line(draw_dim, (m2px_x(3.00), PLAN_Y_BACK), (m2px_x(3.00), PLAN_Y_GUDANG_SOUTH), "3.00 m", offset=-100, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])
draw_dim_line(draw_dim, (m2px_x(3.00), PLAN_Y_GUDANG_SOUTH), (m2px_x(3.00), PLAN_Y_DIR_SOUTH), "2.76 m", offset=-100, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])
draw_dim_line(draw_dim, (m2px_x(3.00), PLAN_Y_DIR_SOUTH), (m2px_x(3.00), PLAN_Y_FACADE), "6.84 m", offset=-100, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])
draw_dim_line(draw_dim, (m2px_x(0.00), PLAN_Y_FACADE), (m2px_x(0.00), PLAN_Y_FRONT_GATE), "9.30 m", offset=-100, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])
# Offset 2: Total Plot Depth (offset = -200)
draw_dim_line(draw_dim, (m2px_x(0.00), PLAN_Y_BACK), (m2px_x(0.00), PLAN_Y_FRONT_GATE), "TOTAL KEDALAMAN = 21.90 m", offset=-190, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])

# --- TOP DIMENSION STRING (Gudang 15m & building width) ---
# Offset 1: Sub-segments (offset = -60)
draw_dim_line(draw_dim, (m2px_x(3.00), PLAN_Y_BACK), (m2px_x(5.31), PLAN_Y_BACK), "2.31 m", offset=-50)
draw_dim_line(draw_dim, (m2px_x(5.31), PLAN_Y_BACK), (m2px_x(7.10), PLAN_Y_BACK), "1.79 m", offset=-50)
draw_dim_line(draw_dim, (m2px_x(7.10), PLAN_Y_BACK), (m2px_x(18.00), PLAN_Y_BACK), "10.90 m", offset=-50)
# Offset 2: Gudang Total Span 15.00m (offset = -110)
draw_dim_line(draw_dim, (m2px_x(3.00), PLAN_Y_BACK), (m2px_x(18.00), PLAN_Y_BACK), "PANJANG GUDANG = 15.00 m", offset=-100)

# --- BOTTOM DIMENSION STRING (Front Property Width 22.20m) ---
# Offset 1: Sub-segments (offset = 50)
draw_dim_line(draw_dim, (m2px_x(0.00), PLAN_Y_FRONT_GATE), (m2px_x(7.50), PLAN_Y_FRONT_GATE), "7.50 m", offset=50)
draw_dim_line(draw_dim, (m2px_x(7.50), PLAN_Y_FRONT_GATE), (m2px_x(12.00), PLAN_Y_FRONT_GATE), "4.50 m", offset=50)
draw_dim_line(draw_dim, (m2px_x(12.00), PLAN_Y_FRONT_GATE), (m2px_x(22.20), PLAN_Y_FRONT_GATE), "10.20 m", offset=50)
# Offset 2: Total Frontage 22.20m (offset = 110)
draw_dim_line(draw_dim, (m2px_x(0.00), PLAN_Y_FRONT_GATE), (m2px_x(22.20), PLAN_Y_FRONT_GATE), "TOTAL LEBAR PROPERTY = 22.20 m", offset=110)

# --- RIGHT DIMENSION STRING (Staircase & Carport Yard) ---
draw_dim_line(draw_dim, (m2px_x(22.20), PLAN_Y_FACADE), (m2px_x(22.20), PLAN_Y_FRONT_GATE), "CARPORT YARD = 9.30 m", offset=60, is_vertical=True, layer_img=layers_dict["07_Dimensi_CAD_Notasi"])

# North Arrow Symbol (Compass Rose)
na_x, na_y = 2150, 1600
draw_dim.ellipse([na_x - 35, na_y - 35, na_x + 35, na_y + 35], outline=(15, 23, 42, 255), width=2)
draw_dim.polygon([(na_x, na_y - 45), (na_x - 12, na_y), (na_x, na_y - 8)], fill=(15, 23, 42, 255))
draw_dim.polygon([(na_x, na_y - 45), (na_x + 12, na_y), (na_x, na_y - 8)], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255))
draw_dim.polygon([(na_x, na_y + 45), (na_x - 12, na_y), (na_x, na_y + 8)], fill=(203, 213, 225, 255), outline=(15, 23, 42, 255))
draw_dim.polygon([(na_x, na_y + 45), (na_x + 12, na_y), (na_x, na_y + 8)], fill=(15, 23, 42, 255))
draw_dim.text((na_x - 7, na_y - 70), "U", fill=(15, 23, 42, 255), font=font_sec_title)

# Graphic Scale Bar (1:100)
sb_x, sb_y = 2050, 1750
bar_len_10m = int(10.0 * SCALE) # 720 px -> let's make a 5m bar = 360 px
draw_dim.rectangle([sb_x - 200, sb_y, sb_x - 200 + 72, sb_y + 8], fill=(15, 23, 42, 255))
draw_dim.rectangle([sb_x - 200 + 72, sb_y, sb_x - 200 + 144, sb_y + 8], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255))
draw_dim.rectangle([sb_x - 200 + 144, sb_y, sb_x - 200 + 216, sb_y + 8], fill=(15, 23, 42, 255))
draw_dim.rectangle([sb_x - 200 + 216, sb_y, sb_x - 200 + 360, sb_y + 8], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255))
draw_dim.text((sb_x - 205, sb_y - 18), "0m", fill=(15, 23, 42, 255), font=font_kop_sm)
draw_dim.text((sb_x - 200 + 65, sb_y - 18), "1m", fill=(15, 23, 42, 255), font=font_kop_sm)
draw_dim.text((sb_x - 200 + 135, sb_y - 18), "2m", fill=(15, 23, 42, 255), font=font_kop_sm)
draw_dim.text((sb_x - 200 + 205, sb_y - 18), "3m", fill=(15, 23, 42, 255), font=font_kop_sm)
draw_dim.text((sb_x - 200 + 350, sb_y - 18), "5m", fill=(15, 23, 42, 255), font=font_kop_sm)
draw_dim.text((sb_x - 170, sb_y + 14), "SKALA GRAFIS 1:100", fill=(71, 85, 105, 255), font=font_kop_sm)

# ==============================================================================
# LAYER 08: KOP GAMBAR & BORDER (TITLE BLOCK & SHEET MARGINS)
# ==============================================================================
print("Drawing Layer 08: Kop Gambar & Border...")

# Outer Sheet Border
draw_kop.rectangle([60, 60, WIDTH - 60, HEIGHT - 60], outline=(15, 23, 42, 255), width=5)
draw_kop.rectangle([72, 72, WIDTH - 72, HEIGHT - 72], outline=(15, 23, 42, 255), width=1)

# Divider Banner between Elevation and Floor Plan
draw_kop.line([(72, 1330), (WIDTH - 72, 1330)], fill=(15, 23, 42, 255), width=3)
draw_kop.rectangle([WIDTH/2 - 320, 1315, WIDTH/2 + 320, 1345], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=2)
draw_kop.text((WIDTH/2 - 305, 1320), "DENAH TATA RUANG LT. 1 & GUDANG UTAMA CDAKB - SKALA 1:100", fill=(15, 23, 42, 255), font=font_room_title)

# Title Block at Bottom (Kop Gambar Standar IAI)
kop_y1, kop_y2 = 3450, 3720
kop_x1, kop_x2 = 72, WIDTH - 72
draw_kop.rectangle([kop_x1, kop_y1, kop_x2, kop_y2], fill=(255, 255, 255, 255), outline=(15, 23, 42, 255), width=3)

# Column Dividers
# Col 1: Logo & Company (x1 to 650)
draw_kop.line([(650, kop_y1), (650, kop_y2)], fill=(15, 23, 42, 255), width=2)
# Col 2: Project & Client (650 to 1450)
draw_kop.line([(1450, kop_y1), (1450, kop_y2)], fill=(15, 23, 42, 255), width=2)
# Col 3: Drawing Title & Scale (1450 to 1950)
draw_kop.line([(1950, kop_y1), (1950, kop_y2)], fill=(15, 23, 42, 255), width=2)
# Col 4: Sheet Code & Approval (1950 to x2)

# Col 1 Content: Corporate Identity
draw_kop.rectangle([100, kop_y1 + 35, 140, kop_y1 + 85], fill=(4, 120, 87, 255))
draw_kop.rectangle([85, kop_y1 + 50, 155, kop_y1 + 70], fill=(4, 120, 87, 255))
draw_kop.text((175, kop_y1 + 35), "PT MAZIYA MEDICAL GLOBAL", fill=(4, 120, 87, 255), font=font_kop_title)
draw_kop.text((175, kop_y1 + 65), "DISTRIBUTOR ALAT KESEHATAN (CDAKB)", fill=(30, 41, 59, 255), font=font_kop_body)
draw_kop.text((175, kop_y1 + 90), "Kantor & Gudang Distribusi Resmi Alkes Farmasi", fill=(100, 116, 139, 255), font=font_kop_sm)
draw_kop.text((175, kop_y1 + 110), "Sertifikasi Standar Permenkes No. 14/2021", fill=(100, 116, 139, 255), font=font_kop_sm)

# Col 2 Content: Project & Scope
draw_kop.text((670, kop_y1 + 25), "NAMA PROYEK:", fill=(100, 116, 139, 255), font=font_kop_sm)
draw_kop.text((670, kop_y1 + 45), "AS-BUILT & USULAN TATA RUANG KANTOR & GUDANG CDAKB", fill=(15, 23, 42, 255), font=font_room_title)
draw_kop.text((670, kop_y1 + 75), "KLIEN / PEMILIK: PT MAZIYA MEDICAL GLOBAL (PT MMG)", fill=(30, 41, 59, 255), font=font_kop_body)
draw_kop.text((670, kop_y1 + 98), "LOKASI: Depok / Jakarta, Jawa Barat, Indonesia", fill=(71, 85, 105, 255), font=font_kop_body)
draw_kop.text((670, kop_y1 + 120), "CATATAN: Forensik Lekuk Bangunan 100% Sesuai Bukti Lapangan", fill=(4, 120, 87, 255), font=font_kop_sm)

# Col 3 Content: Drawing Title & Scale
draw_kop.text((1470, kop_y1 + 25), "JUDUL GAMBAR:", fill=(100, 116, 139, 255), font=font_kop_sm)
draw_kop.text((1470, kop_y1 + 45), "DENAH TATA RUANG & TAMPAK DEPAN", fill=(15, 23, 42, 255), font=font_room_title)
draw_kop.text((1470, kop_y1 + 75), "SKALA: 1 : 100 @ FORMAT A2/A3 (300 DPI)", fill=(30, 41, 59, 255), font=font_kop_body)
draw_kop.text((1470, kop_y1 + 98), "TANGGAL: OKTOBER 2026", fill=(71, 85, 105, 255), font=font_kop_body)
draw_kop.text((1470, kop_y1 + 120), "DIGAMBAR: Tim Arsitektur & Cyber-Operator", fill=(100, 116, 139, 255), font=font_kop_sm)

# Col 4 Content: Sheet Number & Stamp
draw_kop.text((1970, kop_y1 + 25), "NO. LEMBAR:", fill=(100, 116, 139, 255), font=font_kop_sm)
draw_kop.text((1970, kop_y1 + 45), "ARS - MMG - 01", fill=(15, 23, 42, 255), font=font_sheet_title)
draw_kop.rectangle([1970, kop_y1 + 90, 2240, kop_y1 + 135], outline=(4, 120, 87, 255), width=2)
draw_kop.text((1980, kop_y1 + 98), "STATUS: VERIFIED CDAKB", fill=(4, 120, 87, 255), font=font_kop_body)
draw_kop.text((1980, kop_y1 + 116), "DISETUJUI: DIREKSI PT MMG", fill=(4, 120, 87, 255), font=font_kop_sm)

# ==============================================================================
# COMPOSITE ALL LAYERS TO HIGH-RES MASTER IMAGE
# ==============================================================================
print("Compositing all layers into master presentation drawing...")
composite_img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
for name in [
    "00_Background",
    "01_Tampak_Depan_Fasad",
    "02_Lantai_&_Hatches",
    "03_Dinding_Solid_Hitam",
    "04_Pintu_Jendela_Bukaan",
    "05_Furnitur_&_Peralatan_2D",
    "06_Label_Ruangan_Elevasi",
    "07_Dimensi_CAD_Notasi",
    "08_Kop_Gambar_&_Border"
]:
    composite_img = Image.alpha_composite(composite_img, layers_dict[name])

# Save PNG and JPG
png_path = "/Users/user/Downloads/maziya-3d-office/sketsa_denah_arsitektur_pt_mmg.png"
jpg_path = "/Users/user/Downloads/maziya-3d-office/sketsa_denah_arsitektur_pt_mmg.jpg"
composite_img.save(png_path, "PNG", dpi=(300, 300))
composite_img.convert("RGB").save(jpg_path, "JPEG", quality=95, dpi=(300, 300))
print(f"Saved High-Res PNG: {png_path} ({os.path.getsize(png_path)/1024/1024:.2f} MB)")
print(f"Saved High-Res JPG: {jpg_path} ({os.path.getsize(jpg_path)/1024/1024:.2f} MB)")

# Copy to PT MMG folder
folder_mmg = "/Users/user/Downloads/PT Maziya Medical Global/09 Denah 3D Kantor dan Gudang (maziya-3d-office)"
if os.path.exists(folder_mmg):
    composite_img.save(os.path.join(folder_mmg, "sketsa_denah_arsitektur_pt_mmg.png"), "PNG", dpi=(300, 300))
    composite_img.convert("RGB").save(os.path.join(folder_mmg, "sketsa_denah_arsitektur_pt_mmg.jpg"), "JPEG", quality=95, dpi=(300, 300))
    print("Copied PNG and JPG to PT Maziya Medical Global folder.")

# ==============================================================================
# CREATE MULTI-LAYER ADOBE PHOTOSHOP (.PSD) DOCUMENT VIA PYTOSHOP
# ==============================================================================
print("Creating Multi-Layer Adobe Photoshop (.PSD) document...")
psd_layers = []

# List of layers in reverse order (bottom to top)
layer_order = [
    ("Background_Kertas", layers_dict["00_Background"]),
    ("Tampak_Depan_Fasad_22.2M", layers_dict["01_Tampak_Depan_Fasad"]),
    ("Lantai_&_Tile_Hatches", layers_dict["02_Lantai_&_Hatches"]),
    ("Dinding_Solid_Hitam", layers_dict["03_Dinding_Solid_Hitam"]),
    ("Pintu_Jendela_Bukaan", layers_dict["04_Pintu_Jendela_Bukaan"]),
    ("Furnitur_&_Peralatan_2D", layers_dict["05_Furnitur_&_Peralatan_2D"]),
    ("Label_Ruangan_&_Elevasi", layers_dict["06_Label_Ruangan_Elevasi"]),
    ("Dimensi_CAD_&_Notasi", layers_dict["07_Dimensi_CAD_Notasi"]),
    ("Kop_Gambar_&_Border", layers_dict["08_Kop_Gambar_&_Border"]),
]

for name, im in layer_order:
    arr = np.array(im, dtype=np.uint8)
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    a = arr[:, :, 3]
    
    # Check bounding box of non-zero alpha
    y_indices, x_indices = np.where(a > 0)
    if len(y_indices) == 0:
        top, bottom, left, right = 0, 10, 0, 10
        r_crop = np.zeros((10, 10), dtype=np.uint8)
        g_crop = np.zeros((10, 10), dtype=np.uint8)
        b_crop = np.zeros((10, 10), dtype=np.uint8)
        a_crop = np.zeros((10, 10), dtype=np.uint8)
    else:
        top = int(np.min(y_indices))
        bottom = int(np.max(y_indices)) + 1
        left = int(np.min(x_indices))
        right = int(np.max(x_indices)) + 1
        r_crop = r[top:bottom, left:right]
        g_crop = g[top:bottom, left:right]
        b_crop = b[top:bottom, left:right]
        a_crop = a[top:bottom, left:right]
        
    psd_layer = nested_layers.Image(
        name=name,
        visible=True,
        opacity=255,
        top=top,
        left=left,
        bottom=bottom,
        right=right,
        channels={
            -1: a_crop,
            0: r_crop,
            1: g_crop,
            2: b_crop
        }
    )
    psd_layers.append(psd_layer)

psd_doc = nested_layers.nested_layers_to_psd(
    psd_layers,
    color_mode=ColorMode.rgb,
    compression=Compression.raw
)

psd_path = "/Users/user/Downloads/maziya-3d-office/sketsa_denah_arsitektur_pt_mmg.psd"
with open(psd_path, "wb") as f:
    psd_doc.write(f)
print(f"Saved Multi-Layer PSD: {psd_path} ({os.path.getsize(psd_path)/1024/1024:.2f} MB)")

if os.path.exists(folder_mmg):
    with open(os.path.join(folder_mmg, "sketsa_denah_arsitektur_pt_mmg.psd"), "wb") as f:
        psd_doc.write(f)
    print("Copied PSD to PT Maziya Medical Global folder.")

print("All architectural sketch assets successfully created!")
