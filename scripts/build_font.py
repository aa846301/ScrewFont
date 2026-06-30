from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FONT_PATH = OUTPUT / "ScrewLabelIcons.ttf"
PREVIEW_PATH = OUTPUT / "preview.html"

UNITS_PER_EM = 1000
ASCENT = 1000
DESCENT = -100

Point = tuple[float, float]
DrawFunc = Callable[[TTGlyphPen], None]
SIDE_BEARING = 20
SCREW_MAX_WIDTH = 540
SCREW_SHANK_WIDTH = 230
SCREW_HEAD_BASE = 620
SCREW_MACHINE_BOTTOM = 150
SCREW_TAPPING_TIP = 70
SCREW_SHANK_LENGTH = SCREW_HEAD_BASE - SCREW_MACHINE_BOTTOM
SCREW_TAPPING_LENGTH = SCREW_HEAD_BASE - SCREW_TAPPING_TIP
ROUND_HEAD_DEPTH = 235
CUP_HEAD_DEPTH = 340
FLAT_HEAD_DEPTH = 230
CUP_CHAMFER = 30
FLAT_NECK_WIDTH = 270
LOW_HEAD_DEPTH = 85
LOW_HEAD_CHAMFER = 16
SET_SCREW_MAX_WIDTH = 360
SET_SCREW_TOOTH = 28
SET_SCREW_CORE_WIDTH = SET_SCREW_MAX_WIDTH - SET_SCREW_TOOTH * 2
LONG_SHANK_LENGTH = 1470


GLYPHS: dict[str, tuple[str, int, DrawFunc, str]] = {}


def area(points: list[Point]) -> float:
    return sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1])
    ) / 2


def contour(pen: TTGlyphPen, points: list[Point], *, hole: bool = False) -> None:
    if not points:
        return

    # TrueType convention: clockwise outer contours, counter-clockwise holes.
    points = [(round(x), round(y)) for x, y in points]
    signed = area(points)
    if hole and signed < 0:
        points.reverse()
    if not hole and signed > 0:
        points.reverse()

    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()


def rect(pen: TTGlyphPen, x: float, y: float, w: float, h: float, *, hole: bool = False) -> None:
    contour(pen, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)], hole=hole)


def polygon(pen: TTGlyphPen, points: list[Point], *, hole: bool = False) -> None:
    contour(pen, points, hole=hole)


def regular_polygon(cx: float, cy: float, r: float, sides: int, rotation: float = 0) -> list[Point]:
    return [
        (
            cx + math.cos(rotation + math.tau * i / sides) * r,
            cy + math.sin(rotation + math.tau * i / sides) * r,
        )
        for i in range(sides)
    ]


def ellipse_points(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    *,
    start: float = 0,
    end: float = math.tau,
    steps: int = 40,
) -> list[Point]:
    return [
        (
            cx + math.cos(start + (end - start) * i / steps) * rx,
            cy + math.sin(start + (end - start) * i / steps) * ry,
        )
        for i in range(steps + 1)
    ]


def circle(pen: TTGlyphPen, cx: float, cy: float, r: float, *, hole: bool = False) -> None:
    contour(pen, ellipse_points(cx, cy, r, r, steps=48), hole=hole)


def ring(pen: TTGlyphPen, cx: float, cy: float, outer: float, inner: float) -> None:
    circle(pen, cx, cy, outer)
    circle(pen, cx, cy, inner, hole=True)


def rounded_rect(
    pen: TTGlyphPen,
    x: float,
    y: float,
    w: float,
    h: float,
    r: float,
    *,
    hole: bool = False,
) -> None:
    r = min(r, w / 2, h / 2)
    pts: list[Point] = []
    pts += ellipse_points(x + r, y + r, r, r, start=math.pi, end=math.pi * 1.5, steps=6)
    pts += ellipse_points(x + w - r, y + r, r, r, start=math.pi * 1.5, end=math.tau, steps=6)
    pts += ellipse_points(x + w - r, y + h - r, r, r, start=0, end=math.pi / 2, steps=6)
    pts += ellipse_points(x + r, y + h - r, r, r, start=math.pi / 2, end=math.pi, steps=6)
    contour(pen, pts, hole=hole)


def rotated_rect(
    pen: TTGlyphPen,
    cx: float,
    cy: float,
    length: float,
    width: float,
    angle: float,
    *,
    hole: bool = False,
) -> None:
    ux, uy = math.cos(angle), math.sin(angle)
    vx, vy = -uy, ux
    hl, hw = length / 2, width / 2
    pts = [
        (cx - ux * hl - vx * hw, cy - uy * hl - vy * hw),
        (cx + ux * hl - vx * hw, cy + uy * hl - vy * hw),
        (cx + ux * hl + vx * hw, cy + uy * hl + vy * hw),
        (cx - ux * hl + vx * hw, cy - uy * hl + vy * hw),
    ]
    contour(pen, pts, hole=hole)


def register(char: str, name: str, advance: int, description: str) -> Callable[[DrawFunc], DrawFunc]:
    def decorator(func: DrawFunc) -> DrawFunc:
        GLYPHS[char] = (name, advance, func, description)
        return func

    return decorator


def normalized_glyph(draw: DrawFunc) -> tuple[object, int, int]:
    pen = TTGlyphPen(None)
    draw(pen)
    glyph = pen.glyph()
    glyph.recalcBounds({})
    if glyph.numberOfContours <= 0:
        return glyph, SIDE_BEARING * 2, SIDE_BEARING

    width = glyph.xMax - glyph.xMin
    glyph.coordinates.translate((SIDE_BEARING - glyph.xMin, 0))
    glyph.recalcBounds({})
    return glyph, width + SIDE_BEARING * 2, SIDE_BEARING


def measured_advance(draw: DrawFunc) -> int:
    _glyph, advance, _lsb = normalized_glyph(draw)
    return advance


@register("H", "tool_hex_socket", 1000, "內六角工具孔")
def glyph_hex_socket(pen: TTGlyphPen) -> None:
    circle(pen, 500, 500, 360)
    polygon(pen, regular_polygon(500, 500, 205, 6, math.radians(30)), hole=True)


def cross_drive_points(cx: float, cy: float, length: float, width: float) -> list[Point]:
    half_len = length / 2
    half_w = width / 2
    return [
        (cx - half_w, cy - half_len),
        (cx + half_w, cy - half_len),
        (cx + half_w, cy - half_w),
        (cx + half_len, cy - half_w),
        (cx + half_len, cy + half_w),
        (cx + half_w, cy + half_w),
        (cx + half_w, cy + half_len),
        (cx - half_w, cy + half_len),
        (cx - half_w, cy + half_w),
        (cx - half_len, cy + half_w),
        (cx - half_len, cy - half_w),
        (cx - half_w, cy - half_w),
    ]


@register("P", "tool_phillips", 1000, "十字起子孔")
def glyph_phillips(pen: TTGlyphPen) -> None:
    circle(pen, 500, 500, 360)
    polygon(pen, cross_drive_points(500, 500, 560, 155), hole=True)


@register("L", "tool_slotted", 1000, "一字起子孔")
def glyph_slotted(pen: TTGlyphPen) -> None:
    circle(pen, 500, 500, 360)
    rounded_rect(pen, 220, 420, 560, 160, 55, hole=True)


@register("T", "tool_torx", 1000, "Torx 星型孔")
def glyph_torx(pen: TTGlyphPen) -> None:
    circle(pen, 500, 500, 360)
    pts = []
    for i in range(24):
        radius = 255 if i % 4 in (0, 3) else 155
        angle = math.radians(-90) + math.tau * i / 24
        pts.append((500 + math.cos(angle) * radius, 500 + math.sin(angle) * radius))
    polygon(pen, pts, hole=True)


@register("W", "tool_outer_hex", 1000, "外六角扳手/套筒")
def glyph_outer_hex(pen: TTGlyphPen) -> None:
    polygon(pen, regular_polygon(500, 500, 360, 6, math.radians(30)))


def vertical_shank_body(
    pen: TTGlyphPen,
    *,
    x: float = 500,
    top: float = SCREW_HEAD_BASE,
    bottom: float = SCREW_MACHINE_BOTTOM,
    width: float = SCREW_SHANK_WIDTH,
    pointed: bool = False,
) -> None:
    half = width / 2
    if pointed:
        polygon(pen, [(x - half, top), (x + half, top), (x, SCREW_TAPPING_TIP)])
    else:
        rect(pen, x - half, bottom, width, top - bottom)


def vertical_head(pen: TTGlyphPen, kind: str) -> None:
    half = SCREW_MAX_WIDTH / 2
    if kind == "round":
        pts = [(500 - half, SCREW_HEAD_BASE), (500 + half, SCREW_HEAD_BASE)]
        pts += ellipse_points(500, SCREW_HEAD_BASE, half, ROUND_HEAD_DEPTH, start=0, end=math.pi, steps=24)
        polygon(pen, pts)
    elif kind == "cup":
        y0 = SCREW_HEAD_BASE
        y1 = SCREW_HEAD_BASE + CUP_HEAD_DEPTH
        polygon(
            pen,
            [
                (500 - half, y0 + CUP_CHAMFER),
                (500 - half + CUP_CHAMFER, y0),
                (500 + half - CUP_CHAMFER, y0),
                (500 + half, y0 + CUP_CHAMFER),
                (500 + half, y1 - CUP_CHAMFER),
                (500 + half - CUP_CHAMFER, y1),
                (500 - half + CUP_CHAMFER, y1),
                (500 - half, y1 - CUP_CHAMFER),
            ],
        )
    elif kind == "flat":
        neck = FLAT_NECK_WIDTH / 2
        polygon(
            pen,
            [
                (500 - half, SCREW_HEAD_BASE + FLAT_HEAD_DEPTH),
                (500 + half, SCREW_HEAD_BASE + FLAT_HEAD_DEPTH),
                (500 + neck, SCREW_HEAD_BASE),
                (500 - neck, SCREW_HEAD_BASE),
            ],
        )
    elif kind == "low":
        y0 = SCREW_HEAD_BASE
        y1 = SCREW_HEAD_BASE + LOW_HEAD_DEPTH
        c = LOW_HEAD_CHAMFER
        polygon(
            pen,
            [
                (500 - half, y0 + c),
                (500 - half + c, y0),
                (500 + half - c, y0),
                (500 + half, y0 + c),
                (500 + half, y1 - c),
                (500 + half - c, y1),
                (500 - half + c, y1),
                (500 - half, y1 - c),
            ],
        )


def screw_body_vertical(pen: TTGlyphPen, *, head: str, pointed: bool) -> None:
    vertical_shank_body(pen, pointed=pointed)
    vertical_head(pen, head)


@register("S", "vertical_round_machine", 1000, "直式圓頭機械牙螺絲")
def glyph_vertical_round_machine(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="round", pointed=False)


@register("B", "vertical_cup_machine", 1000, "直式杯頭機械牙螺絲")
def glyph_vertical_cup_machine(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="cup", pointed=False)


@register("F", "vertical_flat_machine", 1000, "直式沉頭機械牙螺絲")
def glyph_vertical_flat_machine(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="flat", pointed=False)


@register("I", "vertical_low_machine", 1000, "直式薄平頭機械牙螺絲")
def glyph_vertical_low_machine(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="low", pointed=False)


@register("s", "vertical_round_tapping", 1000, "直式圓頭自攻螺絲")
def glyph_vertical_round_tapping(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="round", pointed=True)


@register("b", "vertical_cup_tapping", 1000, "直式杯頭自攻螺絲")
def glyph_vertical_cup_tapping(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="cup", pointed=True)


@register("f", "vertical_flat_tapping", 1000, "直式沉頭自攻螺絲")
def glyph_vertical_flat_tapping(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="flat", pointed=True)


@register("i", "vertical_low_tapping", 1000, "直式薄平頭自攻螺絲")
def glyph_vertical_low_tapping(pen: TTGlyphPen) -> None:
    screw_body_vertical(pen, head="low", pointed=True)


def horizontal_shank_body(
    pen: TTGlyphPen,
    *,
    x0: float,
    length: float,
    y: float = 500,
    width: float = SCREW_SHANK_WIDTH,
    pointed: bool = False,
) -> None:
    half = width / 2
    if pointed:
        polygon(pen, [(x0, y + half), (x0 + length, y), (x0, y - half)])
    else:
        rect(pen, x0, y - half, length, width)


def horizontal_head_width(kind: str, scale: float = 1) -> float:
    if kind == "round":
        return ROUND_HEAD_DEPTH * scale
    if kind == "cup":
        return CUP_HEAD_DEPTH * scale
    if kind == "flat":
        return FLAT_HEAD_DEPTH * scale
    if kind == "low":
        return LOW_HEAD_DEPTH * scale
    return 0


def horizontal_head(pen: TTGlyphPen, kind: str, *, x: float, y: float = 500, scale: float = 1) -> None:
    half = SCREW_MAX_WIDTH * scale / 2
    if kind == "round":
        depth = ROUND_HEAD_DEPTH * scale
        pts = [(x + depth, y - half), (x + depth, y + half)]
        pts += ellipse_points(x + depth, y, depth, half, start=math.pi / 2, end=math.pi * 1.5, steps=24)
        polygon(pen, pts)
    elif kind == "cup":
        depth, c = CUP_HEAD_DEPTH * scale, CUP_CHAMFER * scale
        polygon(
            pen,
            [
                (x, y - half + c),
                (x + c, y - half),
                (x + depth - c, y - half),
                (x + depth, y - half + c),
                (x + depth, y + half - c),
                (x + depth - c, y + half),
                (x + c, y + half),
                (x, y + half - c),
            ],
        )
    elif kind == "flat":
        depth = FLAT_HEAD_DEPTH * scale
        neck = FLAT_NECK_WIDTH * scale / 2
        polygon(
            pen,
            [
                (x, y - half),
                (x + depth, y - neck),
                (x + depth, y + neck),
                (x, y + half),
            ],
        )
    elif kind == "low":
        depth, c = LOW_HEAD_DEPTH * scale, LOW_HEAD_CHAMFER * scale
        polygon(
            pen,
            [
                (x, y - half + c),
                (x + c, y - half),
                (x + depth - c, y - half),
                (x + depth, y - half + c),
                (x + depth, y + half - c),
                (x + depth - c, y + half),
                (x + c, y + half),
                (x, y + half - c),
            ],
        )


def screw_body_horizontal(
    pen: TTGlyphPen,
    *,
    head: str,
    pointed: bool,
    long: bool = False,
) -> None:
    head_x = 100
    shaft_length = LONG_SHANK_LENGTH if long else (SCREW_TAPPING_LENGTH if pointed else SCREW_SHANK_LENGTH)
    shaft_x0 = head_x + horizontal_head_width(head)
    horizontal_shank_body(pen, x0=shaft_x0, length=shaft_length, pointed=pointed)
    horizontal_head(pen, head, x=head_x)


for char, name, head, pointed, desc in [
    ("A", "horizontal_short_round_machine", "round", False, "橫式短版圓頭機械牙螺絲"),
    ("C", "horizontal_short_cup_machine", "cup", False, "橫式短版杯頭機械牙螺絲"),
    ("E", "horizontal_short_flat_machine", "flat", False, "橫式短版沉頭機械牙螺絲"),
    ("K", "horizontal_short_low_machine", "low", False, "橫式短版薄平頭機械牙螺絲"),
    ("a", "horizontal_short_round_tapping", "round", True, "橫式短版圓頭自攻螺絲"),
    ("c", "horizontal_short_cup_tapping", "cup", True, "橫式短版杯頭自攻螺絲"),
    ("e", "horizontal_short_flat_tapping", "flat", True, "橫式短版沉頭自攻螺絲"),
    ("k", "horizontal_short_low_tapping", "low", True, "橫式短版薄平頭自攻螺絲"),
]:

    def make_short(pen: TTGlyphPen, head: str = head, pointed: bool = pointed) -> None:
        screw_body_horizontal(pen, head=head, pointed=pointed, long=False)

    register(char, name, 1000, desc)(make_short)


for char, name, head, pointed, desc in [
    ("Q", "horizontal_long_round_machine", "round", False, "橫式長版圓頭機械牙螺絲"),
    ("G", "horizontal_long_cup_machine", "cup", False, "橫式長版杯頭機械牙螺絲"),
    ("J", "horizontal_long_flat_machine", "flat", False, "橫式長版沉頭機械牙螺絲"),
    ("Y", "horizontal_long_low_machine", "low", False, "橫式長版薄平頭機械牙螺絲"),
    ("q", "horizontal_long_round_tapping", "round", True, "橫式長版圓頭自攻螺絲"),
    ("g", "horizontal_long_cup_tapping", "cup", True, "橫式長版杯頭自攻螺絲"),
    ("j", "horizontal_long_flat_tapping", "flat", True, "橫式長版沉頭自攻螺絲"),
    ("y", "horizontal_long_low_tapping", "low", True, "橫式長版薄平頭自攻螺絲"),
]:

    def make_long(pen: TTGlyphPen, head: str = head, pointed: bool = pointed) -> None:
        screw_body_horizontal(pen, head=head, pointed=pointed, long=True)

    register(char, name, 2000, desc)(make_long)


def vertical_threaded_rod(pen: TTGlyphPen, *, x: float, top: float, bottom: float, width: float) -> None:
    half = width / 2
    tooth = SET_SCREW_TOOTH
    pitch = 82
    left: list[Point] = []
    y = top
    i = 0
    while y > bottom:
        left.append((x - half - (tooth if i % 2 else 0), y))
        y -= pitch / 2
        i += 1
    left.append((x - half, bottom))
    right = [(2 * x - px, py) for px, py in reversed(left)]
    polygon(pen, left + right)


def horizontal_threaded_rod(pen: TTGlyphPen, *, x0: float, x1: float, y: float, width: float) -> None:
    half = width / 2
    tooth = SET_SCREW_TOOTH
    pitch = 82
    top: list[Point] = []
    x = x0
    i = 0
    while x < x1:
        top.append((x, y + half + (tooth if i % 2 else 0)))
        x += pitch / 2
        i += 1
    top.append((x1, y + half))
    bottom = [(px, 2 * y - py) for px, py in reversed(top)]
    polygon(pen, top + bottom)


@register("Z", "vertical_set_screw", 1000, "直式止付螺絲")
def glyph_vertical_set_screw(pen: TTGlyphPen) -> None:
    vertical_threaded_rod(pen, x=500, bottom=SCREW_MACHINE_BOTTOM, top=SCREW_MACHINE_BOTTOM + SCREW_SHANK_LENGTH, width=SET_SCREW_CORE_WIDTH)


@register("z", "horizontal_set_screw", 1000, "橫式止付螺絲")
def glyph_horizontal_set_screw(pen: TTGlyphPen) -> None:
    horizontal_threaded_rod(pen, x0=100, x1=100 + SCREW_SHANK_LENGTH, y=500, width=SET_SCREW_CORE_WIDTH)


@register("N", "part_hex_nut", 1000, "六角螺母")
def glyph_hex_nut(pen: TTGlyphPen) -> None:
    polygon(pen, regular_polygon(500, 500, 360, 6, math.radians(30)))
    circle(pen, 500, 500, 170, hole=True)


@register("R", "part_washer", 1000, "墊片")
def glyph_washer(pen: TTGlyphPen) -> None:
    ring(pen, 500, 500, 340, 170)


@register("D", "part_round_magnet", 1000, "圓形磁鐵")
def glyph_magnet(pen: TTGlyphPen) -> None:
    circle(pen, 500, 500, 345)
    polygon(
        pen,
        [
            (320, 280),
            (320, 720),
            (405, 720),
            (595, 430),
            (595, 720),
            (680, 720),
            (680, 280),
            (595, 280),
            (595, 335),
            (405, 625),
            (405, 280),
        ],
        hole=True,
    )


def build_font() -> None:
    glyph_order = [".notdef"] + [data[0] for data in GLYPHS.values()]
    cmap = {ord(char): data[0] for char, data in GLYPHS.items()}
    glyphs = {}
    metrics = {}

    pen = TTGlyphPen(None)
    rect(pen, 80, 0, 600, 700)
    rect(pen, 200, 120, 360, 460, hole=True)
    glyphs[".notdef"] = pen.glyph()
    metrics[".notdef"] = (800, 80)

    for _char, (glyph_name, _advance, draw, _description) in GLYPHS.items():
        glyph, advance, lsb = normalized_glyph(draw)
        glyphs[glyph_name] = glyph
        metrics[glyph_name] = (advance, lsb)

    fb = FontBuilder(UNITS_PER_EM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=DESCENT)
    fb.setupNameTable(
        {
            "familyName": "ScrewLabelIcons",
            "styleName": "Regular",
            "uniqueFontIdentifier": "ScrewLabelIcons Regular 0.1.0",
            "fullName": "ScrewLabelIcons Regular",
            "psName": "ScrewLabelIcons-Regular",
            "version": "Version 0.1.0",
            "manufacturer": "screwfont",
            "designer": "screwfont geometry generator",
            "description": "3D-printing-friendly screw label icon font.",
        }
    )
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=abs(DESCENT),
    )
    fb.setupPost()
    fb.save(FONT_PATH)


def glyph_rows() -> str:
    rows = []
    for char, (_name, _advance, draw, description) in GLYPHS.items():
        code = f"U+{ord(char):04X}"
        advance = measured_advance(draw)
        rows.append(
            f"<tr><td class=\"glyph\">{char}</td><td><code>{char}</code></td>"
            f"<td><code>{code}</code></td><td>{advance}</td><td>{description}</td></tr>"
        )
    return "\n".join(rows)


def sample_rows() -> str:
    samples = [
        ("H S", "M4×16", "內六角 + 直式圓頭機械牙螺絲 M4×16"),
        ("H B", "M3×6", "內六角 + 直式杯頭機械牙螺絲 M3×6"),
        ("H F", "M3×6", "內六角 + 直式沉頭機械牙螺絲 M3×6"),
        ("P I", "M3×6", "十字 + 直式薄平頭機械牙螺絲 M3×6"),
        ("P b", "M2×10", "十字 + 直式杯頭自攻螺絲 M2×10"),
        ("P f", "M2×10", "十字 + 直式沉頭自攻螺絲 M2×10"),
        ("H A", "M5×20", "內六角 + 橫式短版圓頭機械牙螺絲 M5×20"),
        ("P K", "M3×8", "十字 + 橫式短版薄平頭機械牙螺絲 M3×8"),
        ("H Q", "M6×45", "內六角 + 橫式長版圓頭機械牙螺絲 M6×45"),
        ("H z", "M4×8", "內六角 + 橫式止付螺絲 M4×8"),
        ("N", "M4", "六角螺母 M4"),
        ("R", "M3", "墊片 M3"),
        ("D", "D6×3", "圓形磁鐵 D6×3"),
    ]
    rows = []
    for icons, text, description in samples:
        icon_text = "".join(f"<span>{ch}</span>" if ch in GLYPHS else ch for ch in icons)
        rows.append(
            f"<div class=\"sample\"><div class=\"label\">{icon_text}"
            f"<strong>{text}</strong></div><div>{description}</div></div>"
        )
    return "\n".join(rows)


def build_preview() -> None:
    html = f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ScrewLabelIcons Preview</title>
  <style>
    @font-face {{
      font-family: "ScrewLabelIcons";
      src: url("./ScrewLabelIcons.ttf") format("truetype");
    }}
    :root {{
      color-scheme: light;
      font-family: "Segoe UI", "Noto Sans TC", Arial, sans-serif;
      color: #202124;
      background: #f6f7f8;
    }}
    body {{
      margin: 0;
      padding: 32px;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
    }}
    h1, h2 {{
      margin: 0 0 16px;
      letter-spacing: 0;
    }}
    section {{
      margin: 0 0 32px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid #d7dce0;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #e4e7ea;
      text-align: left;
      vertical-align: middle;
    }}
    th {{
      background: #eef1f3;
      font-size: 14px;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 14px;
    }}
    .glyph {{
      width: 92px;
      height: 72px;
      font-family: "ScrewLabelIcons";
      font-size: 56px;
      line-height: 1;
      text-align: center;
    }}
    .samples {{
      display: grid;
      gap: 12px;
    }}
    .sample {{
      display: grid;
      grid-template-columns: minmax(260px, 1fr) 1.4fr;
      align-items: center;
      gap: 18px;
      padding: 14px 16px;
      background: white;
      border: 1px solid #d7dce0;
      border-radius: 6px;
    }}
    .label {{
      min-height: 72px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 34px;
      white-space: nowrap;
    }}
    .label span {{
      font-family: "ScrewLabelIcons";
      font-size: 62px;
      line-height: 1;
    }}
    @media (max-width: 760px) {{
      body {{
        padding: 18px;
      }}
      .sample {{
        grid-template-columns: 1fr;
      }}
      .label {{
        font-size: 28px;
        overflow-x: auto;
      }}
      .label span {{
        font-size: 52px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <section>
      <h1>ScrewLabelIcons</h1>
    </section>
    <section>
      <h2>Glyph 對照表</h2>
      <table>
        <thead>
          <tr><th>圖示</th><th>字元</th><th>Unicode</th><th>Advance Width</th><th>說明</th></tr>
        </thead>
        <tbody>
          {glyph_rows()}
        </tbody>
      </table>
    </section>
    <section>
      <h2>標籤範例</h2>
      <div class="samples">
        {sample_rows()}
      </div>
    </section>
  </main>
</body>
</html>
"""
    PREVIEW_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    build_font()
    build_preview()
    print(f"Wrote {FONT_PATH}")
    print(f"Wrote {PREVIEW_PATH}")


if __name__ == "__main__":
    main()

