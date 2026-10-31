import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytoshop
from pytoshop.user import nested_layers
from pytoshop.enums import ColorMode, Compression

# ==============================================================================
# 1. SETUP CANVAS & SCALE CONSTANTS
# ==============================================================================
WIDTH = 2400
HEIGHT = 3800
SCALE = 72.0 # 72 px per meter
WALL_THICK = int(0.15 * SCALE) # 15cm wall = 11 px

# Fonts
FONT_HELVETICA = '/System/Library/Fonts/HelveticaNeue.ttc'
FONT_ARIAL = '/System/Library/Fonts/Supplemental/Arial.ttf'

font_sheet_title = ImageFont.truetype(FONT_HELVETICA, 36)
font_sec_title   = ImageFont.truetype(FONT_HELVETICA, 26)
font_room_title  = ImageFont.truetype(FONT_HELVETICA, 20)
font_room_sub    = ImageFont.truetype(FONT_HELVETICA, 15)
font_dim         = ImageFont.truetype(FONT_HELVETICA, 16)
font_dim_bold    = ImageFont.truetype(FONT_HELVETICA, 18)
font_kop_title   = ImageFont.truetype(FONT_HELVETICA, 22)
font_kop_body    = ImageFont.truetype(FONT_HELVETICA, 14)
font_kop_sm      = ImageFont.truetype(FONT_HELVETICA, 12)

# Coordinate Anchors
PLAN_X0 = 400.0   # Property X = 0.00 m
PLAN_X_MAX = PLAN_X0 + 22.20 * SCALE # 1998.4 px

PLAN_Y_BACK = 1500.0                           # Z = 12.60 m (North boundary)
PLAN_Y_GUDANG_SOUTH = PLAN_Y_BACK + 3.00 * SCALE # 1716.0 (Z = 9.60 m)
PLAN_Y_DIR_SOUTH = PLAN_Y_GUDANG_SOUTH + 2.76 * SCALE # 1914.7 (Z = 6.84 m)
PLAN_Y_HALL_DIV = PLAN_Y_BACK + (12.60 - 5.80) * SCALE # 1989.6 (Z = 5.80 m)
PLAN_Y_FACADE = PLAN_Y_BACK + 12.60 * SCALE     # 2407.2 (Z = 0.00 m)
PLAN_Y_FRONT_GATE = PLAN_Y_FACADE + 9.30 * SCALE # 3076.8 (Z = -9.30 m)

def m2px_x(xm):
    return PLAN_X0 + xm * SCALE

def m2px_y(zm_from_front):
    return PLAN_Y_FACADE - zm_from_front * SCALE

# Initialize Layers as RGBA Image objects
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

print("Canvas layers successfully allocated.")
