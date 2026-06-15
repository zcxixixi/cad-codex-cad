from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.enums import TextEntityAlignment


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
DXF_PATH = OUT / "04_信息网络_综合布线_有线电视_公共广播系统图_T3.dxf"

doc = ezdxf.new("R2000", setup=True)
doc.header["$INSUNITS"] = 4  # millimetres
doc.styles.new("CHS", dxfattribs={"font": "simsun.ttf"})

for name, color in [
    ("FRAME", 7),
    ("TITLE", 7),
    ("NETWORK", 5),
    ("CABLING", 3),
    ("CATV", 1),
    ("PA", 6),
    ("NOTE", 8),
]:
    if name not in doc.layers:
        doc.layers.add(name, color=color)

msp = doc.modelspace()


def text(value, x, y, height=250, layer="NOTE", align=TextEntityAlignment.MIDDLE_CENTER):
    entity = msp.add_text(value, dxfattribs={"height": height, "layer": layer, "style": "CHS"})
    entity.set_placement((x, y), align=align)
    return entity


def box(x, y, width, height, label, layer, text_height=220):
    msp.add_lwpolyline(
        [(x, y), (x + width, y), (x + width, y + height), (x, y + height)],
        close=True,
        dxfattribs={"layer": layer},
    )
    lines = label.split("\n")
    start_y = y + height / 2 + (len(lines) - 1) * text_height * 0.65
    for index, line in enumerate(lines):
        text(line, x + width / 2, start_y - index * text_height * 1.3, text_height, layer)


def line(points, layer, width=0):
    msp.add_lwpolyline(points, dxfattribs={"layer": layer, "const_width": width})


def arrow(x1, y1, x2, y2, layer, label=None):
    line([(x1, y1), (x2, y2)], layer)
    size = 160
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 > x1 else -1
        line([(x2, y2), (x2 - sign * size, y2 + size / 2), (x2 - sign * size, y2 - size / 2), (x2, y2)], layer)
    else:
        sign = 1 if y2 > y1 else -1
        line([(x2, y2), (x2 + size / 2, y2 - sign * size), (x2 - size / 2, y2 - sign * size), (x2, y2)], layer)
    if label:
        text(label, (x1 + x2) / 2, (y1 + y2) / 2 + 180, 160, layer)


def frame(origin_x, origin_y, title, number):
    width, height = 11890, 8410
    msp.add_lwpolyline(
        [
            (origin_x, origin_y),
            (origin_x + width, origin_y),
            (origin_x + width, origin_y + height),
            (origin_x, origin_y + height),
        ],
        close=True,
        dxfattribs={"layer": "FRAME"},
    )
    msp.add_lwpolyline(
        [
            (origin_x + width - 3800, origin_y),
            (origin_x + width, origin_y),
            (origin_x + width, origin_y + 900),
            (origin_x + width - 3800, origin_y + 900),
        ],
        close=True,
        dxfattribs={"layer": "FRAME"},
    )
    text(title, origin_x + width / 2, origin_y + height - 450, 360, "TITLE")
    text("某中学建筑物信息设施系统课程设计", origin_x + width - 1900, origin_y + 600, 210, "TITLE")
    text(f"图号：XX-{number:02d}", origin_x + width - 1900, origin_y + 250, 180, "TITLE")
    return width, height


def draw_network(ox, oy):
    frame(ox, oy, "信息网络系统图", 1)
    layer = "NETWORK"
    box(ox + 500, oy + 6100, 1500, 650, "Internet\n教育网", layer)
    box(ox + 2600, oy + 6100, 1600, 650, "出口路由器\n下一代防火墙", layer)
    box(ox + 5000, oy + 5950, 2200, 950, "双核心交换机\n2×10Gbps互联\n行政综合楼网络机房", layer)
    arrow(ox + 2000, oy + 6425, ox + 2600, oy + 6425, layer, "双链路")
    arrow(ox + 4200, oy + 6425, ox + 5000, oy + 6425, layer, "2×10Gbps")

    buildings = [
        (ox + 800, "1#教学楼\n15个FD\n15条12芯OS2"),
        (ox + 4300, "2#教学楼\n10个FD\n10条12芯OS2"),
        (ox + 7800, "行政综合楼\n4个FD\n4条12芯OS2"),
    ]
    for x, label in buildings:
        box(x, oy + 3500, 2500, 1000, label, layer)
        arrow(ox + 6100, oy + 5950, x + 1250, oy + 4500, layer, "10Gbps")
        box(x + 250, oy + 1600, 2000, 800, "24口PoE+接入交换机\n千兆到桌面", layer, 190)
        arrow(x + 1250, oy + 3500, x + 1250, oy + 2400, layer, "万兆上联")
    text("VLAN：教学 / 办公 / 无线 / 访客 / 管理；核心与关键链路冗余", ox + 5950, oy + 1100, 220, layer)


def draw_cabling(ox, oy):
    frame(ox, oy, "综合布线系统图", 2)
    layer = "CABLING"
    box(ox + 4400, oy + 6200, 3000, 850, "BD 主配线设备\n行政综合楼网络机房\n核心交换机 + IP-PBX", layer)
    buildings = [
        (ox + 400, "1#教学楼", 15, 7, 218),
        (ox + 4300, "2#教学楼", 10, 20, 152),
        (ox + 8200, "行政综合楼", 4, 11, 90),
    ]
    for x, name, fd_count, voice_count, data_count in buildings:
        box(x, oy + 3900, 2900, 900, f"{name}\nFD×{fd_count}", layer)
        arrow(ox + 5900, oy + 6200, x + 1450, oy + 4800, layer, "12芯OS2 + 25对UTP")
        box(x + 150, oy + 2100, 2600, 900, f"管理子系统\n光纤配线架 + Cat6A配线架\n数据{data_count}点 / 语音{voice_count}点", layer, 185)
        arrow(x + 1450, oy + 3900, x + 1450, oy + 3000, layer, "垂直主干")
        box(x + 350, oy + 700, 2200, 700, "工作区\nTD + TP + AP", layer)
        arrow(x + 1450, oy + 2100, x + 1450, oy + 1400, layer, "Cat6A U/UTP")
    text("永久链路≤90m；信道≤100m；水平电缆总计23.377km（93箱）", ox + 5950, oy + 5400, 220, layer)


def draw_catv(ox, oy):
    frame(ox, oy, "有线电视系统图", 3)
    layer = "CATV"
    box(ox + 450, oy + 6100, 1800, 700, "市有线电视\n光纤信号", layer)
    box(ox + 2900, oy + 5950, 2200, 1000, "行政综合楼前端\n光接收机\n双向放大器", layer)
    arrow(ox + 2250, oy + 6450, ox + 2900, oy + 6450, layer, "光纤")
    buildings = [
        (ox + 500, "1#教学楼\n67个TV终端"),
        (ox + 4500, "2#教学楼\n55个TV终端"),
        (ox + 8500, "行政综合楼\n20个TV终端"),
    ]
    for x, label in buildings:
        box(x, oy + 3800, 2400, 800, label, layer)
        arrow(ox + 4000, oy + 5950, x + 1200, oy + 4600, layer, "SYWV-75-9")
        box(x + 150, oy + 2200, 2100, 700, "楼层分支/分配器\n5-1000MHz", layer)
        arrow(x + 1200, oy + 3800, x + 1200, oy + 2900, layer)
        box(x + 300, oy + 800, 1800, 650, "TV终端插座\n60~80dBμV", layer)
        arrow(x + 1200, oy + 2200, x + 1200, oy + 1450, layer, "SYWV-75-5")
    text("最不利终端电平校核：106 - 4.8 - 12 - 8 - 7 - 1 = 73.2 dBμV", ox + 5950, oy + 5350, 210, layer)


def draw_pa(ox, oy):
    frame(ox, oy, "公共广播系统图", 4)
    layer = "PA"
    box(ox + 4300, oy + 6100, 3200, 900, "行政综合楼广播控制中心\nIP广播控制主机 + 话筒 + 音源\n主交换机", layer)
    buildings = [
        (ox + 500, "1#教学楼\nIP功放15台\n壁挂音箱20只\n吸顶扬声器168只"),
        (ox + 4500, "2#教学楼\nIP功放10台\n壁挂音箱18只\n吸顶扬声器120只"),
        (ox + 8500, "行政综合楼\nIP功放4台\n吸顶扬声器60只"),
    ]
    for x, label in buildings:
        box(x, oy + 3700, 2400, 1100, label, layer, 175)
        arrow(ox + 5900, oy + 6100, x + 1200, oy + 4800, layer, "校园IP网络")
        box(x + 180, oy + 2100, 2040, 700, "楼层IP网络功放\n100V定压输出", layer)
        arrow(x + 1200, oy + 3700, x + 1200, oy + 2800, layer)
        box(x + 300, oy + 750, 1800, 650, "壁挂/吸顶扬声器\nZR-RVV 2×1.5", layer)
        arrow(x + 1200, oy + 2100, x + 1200, oy + 1400, layer, "100V")
    text("扬声器总功率1272W；功放配置容量2460W，满足不少于1.3倍负荷要求", ox + 5950, oy + 5350, 210, layer)


draw_network(0, 0)
draw_cabling(13000, 0)
draw_catv(0, -9500)
draw_pa(13000, -9500)

doc.saveas(DXF_PATH)
print(DXF_PATH)
