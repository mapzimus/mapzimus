import skia, math, sys, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
OUT, FONT = sys.argv[1], sys.argv[2]

CY, CY2, CY3, DEEP = "#0a5c6e", "#0f6a7d", "#147a8e", "#073f4c"
OR, OR2, CREAM, INK = "#e4690c", "#f28a2e", "#f4efe3", "#0b1d22"
U = skia.PathOp.kUnion_PathOp; D = skia.PathOp.kDifference_PathOp; I = skia.PathOp.kIntersect_PathOp

def d(p):
    V = skia.Path.Verb; it = skia.Path.Iter(p, False); out = []
    f = lambda q: f"{q.x():.2f} {q.y():.2f}"
    while True:
        verb, pts = it.next()
        if verb == V.kDone_Verb: break
        if verb == V.kMove_Verb: out.append("M" + f(pts[0]))
        elif verb == V.kLine_Verb: out.append("L" + f(pts[1]))
        elif verb == V.kQuad_Verb: out.append("Q" + f(pts[1]) + " " + f(pts[2]))
        elif verb == V.kConic_Verb:
            q = skia.Path.ConvertConicToQuads(pts[0], pts[1], pts[2], it.conicWeight(), 2)
            for i in range(1, len(q), 2): out.append("Q" + f(q[i]) + " " + f(q[i+1]))
        elif verb == V.kCubic_Verb: out.append("C" + f(pts[1]) + " " + f(pts[2]) + " " + f(pts[3]))
        elif verb == V.kClose_Verb: out.append("Z")
    return "".join(out)

def op(a, b, o): return skia.Op(a, b, o)
def circ(x, y, r): p = skia.Path(); p.addCircle(x, y, r); return p
def rect(x, y, w, h): p = skia.Path(); p.addRect(x, y, x + w, y + h); return p

XL, XR, YT, YB = 272, 752, 300, 760
def center(depth=344, cr=52, sharp=False, yb=YB, xl=XL, xr=XR, valley_r=0):
    ya = YT + depth; p = skia.Path(); p.moveTo(xl, yb)
    if sharp: p.lineTo(xl, YT); p.lineTo((xl+xr)/2, ya); p.lineTo(xr, YT)
    else:
        p.arcTo(xl, YT, (xl+xr)/2, ya, cr)
        if valley_r: p.arcTo((xl+xr)/2, ya, xr, YT, valley_r)
        else: p.lineTo((xl+xr)/2, ya)
        p.arcTo(xr, YT, xr, yb, cr)
    p.lineTo(xr, yb); return p

def stroke(path, w, join="miter", cap="butt", dash=None):
    J = {"miter": skia.Paint.kMiter_Join, "round": skia.Paint.kRound_Join, "bevel": skia.Paint.kBevel_Join}[join]
    C = {"butt": skia.Paint.kButt_Cap, "round": skia.Paint.kRound_Cap, "square": skia.Paint.kSquare_Cap}[cap]
    paint = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeMiter=6, StrokeJoin=J, StrokeCap=C)
    if dash: paint.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    o = skia.Path(); paint.getFillPath(path, o); return op(o, o, U)

def flat_valley(line, s, depth=344, flat=14):
    half = math.atan2(depth, (XR - XL) / 2)
    tip = YT + depth + (s / 2) / math.cos(half)
    cut = tip - flat / math.tan(math.pi / 2 - half)
    return op(line, rect(0, 0, 1024, cut), I)

def nodes(s, R=None, hole=None, inset=None, xl=XL, xr=XR, yb=YB):
    R = R or s * .81; hole = hole if hole is not None else R * .43; inset = inset or R * .29
    o_ring = op(circ(xl, yb, R), circ(xl, yb, hole), D)
    d_ring = op(circ(xr, yb, R), circ(xr, yb, R - inset), D)
    return o_ring, d_ring, circ(xr, yb, R - inset), circ(xl, yb, hole)

def fit(paths, cx=512, cy=500, w=None, h=None):
    """translate (and optionally scale) all paths so their union is optically centred."""
    u = skia.Path()
    for p, _ in paths: u = op(u, p, U)
    b = u.computeTightBounds()
    sc = 1.0
    if w: sc = w / b.width()
    if h: sc = min(sc, h / b.height())
    m = skia.Matrix(); m.setScaleTranslate(sc, sc, cx - sc*(b.left()+b.right())/2, cy - sc*(b.top()+b.bottom())/2)
    out = []
    for p, c in paths: q = skia.Path(p); q.transform(m); out.append((q, c))
    return out, m

def svg(bg, paths, overlay="", under="", clip_circle=False):
    body = "".join(f'<path d="{d(p)}" fill="{c}" fill-rule="evenodd"/>' for p, c in paths)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">{bg}{under}<g id="mark">{body}</g>{overlay}</svg>'''

def solid(c): return f'<rect width="1024" height="1024" fill="{c}"/>'

def base_mark(s=104, depth=344, cr=52, sharp=False, join="miter", flat=True, valley_r=0, R=None, hole=None, inset=None,
              mark=CREAM, dest=OR, xl=XL, xr=XR):
    line = stroke(center(depth, cr, sharp, xl=xl, xr=xr, valley_r=valley_r), s, join)
    if flat and join == "miter": line = flat_valley(line, s, depth)
    o_ring, d_ring, d_dot, hole_p = nodes(s, R, hole, inset, xl, xr)
    trunk = op(op(op(line, o_ring, U), d_ring, U), hole_p, D); trunk = op(trunk, d_dot, D)
    return [(trunk, mark), (d_dot, dest)]

# Archivo outlined wordmark
_f = None
def word(text, size, x, y, wght=800, wdth=112, anchor="middle", track=0):
    global _f
    if _f is None:
        _f = instancer.instantiateVariableFont(TTFont(FONT), {"wght": wght, "wdth": wdth})
    gs = _f.getGlyphSet(); cmap = _f.getBestCmap(); upm = _f["head"].unitsPerEm; sc = size / upm
    names = [cmap[ord(ch)] for ch in text]
    total = sum(gs[n].width for n in names) * sc + track * (len(names) - 1)
    x0 = x - total / 2 if anchor == "middle" else x
    out = []; cx = x0
    for n in names:
        pen = SVGPathPen(gs); gs[n].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, y)))
        out.append(pen.getCommands()); cx += gs[n].width * sc + track
    return "".join(out)

V = {}
# 1 baseline refined
V[1] = svg(solid(CY), fit(base_mark())[0])
# 2 light & elegant: thin stroke, big open nodes
V[2] = svg(solid(CY), fit(base_mark(s=72, R=70, hole=38, inset=18))[0])
# 3 heavy: bold stroke, compact nodes
V[3] = svg(solid(CY), fit(base_mark(s=136, R=100, hole=40, inset=30))[0])
# 4 technical: fully sharp corners
V[4] = svg(solid(CY), fit(base_mark(sharp=True))[0])
# 5 transit: round joins, consistent radius, rounded valley
V[5] = svg(solid(CY), fit(base_mark(join="round", cr=80, valley_r=40))[0])
# 6 ferry crossing: legs solid, V dashed orange
def ferry():
    s = 104; legs = op(stroke(center(), s, "miter"), rect(0, 0, 1024, YT + 60), D)
    legs = op(legs, stroke(center(), s), U); legs = op(legs, rect(0,0,0,0), U)
    full = flat_valley(stroke(center(), s), s)
    vpart = op(full, op(rect(XL + s/2 + 4, YT + 40, XR - XL - s - 8, 600), rect(0,0,1024,1024), I), I)
    solid_part = op(full, vpart, D)
    dash_c = skia.Path(); dash_c.moveTo(XL + 40, YT + 56); dash_c.lineTo(512, YT + 300); dash_c.lineTo(XR - 40, YT + 56)
    dashes = stroke(dash_c, 40, "round", "round", [1, 74])
    o_ring, d_ring, d_dot, hole_p = nodes(s)
    trunk = op(op(op(solid_part, o_ring, U), d_ring, U), hole_p, D); trunk = op(trunk, d_dot, D)
    ghost = op(vpart, vpart, U)
    return [(ghost, CY2), (trunk, CREAM), (dashes, OR2), (d_dot, OR)]
V[6] = svg(solid(CY), fit(ferry())[0])
# 7 highway casing: cream road with orange centre line
def casing():
    s = 112; m = base_mark(s=s)
    cl = op(flat_valley(stroke(center(), 22), 22), circ(XR, YB, 60), D)
    cl = op(cl, circ(XL, YB, 60), D)
    return m[:1] + [(cl, OR2)] + m[1:]
V[7] = svg(solid(CY), fit(casing())[0])
# 8 inverted: orange field, deep cyan mark, cream destination
V[8] = svg(solid(OR), fit(base_mark(mark=DEEP, dest=CREAM))[0])
# 9 destination halo: big orange sun behind, mark in front
p9, m9 = fit(base_mark(dest=CY))
V[9] = svg(solid(CY), p9, under=f'<circle cx="{m9.mapXY(XR, YB).x():.1f}" cy="{m9.mapXY(XR, YB).y():.1f}" r="190" fill="{OR}" opacity=".9"/><circle cx="{m9.mapXY(XR, YB).x():.1f}" cy="{m9.mapXY(XR, YB).y():.1f}" r="130" fill="{OR2}"/>')
# 10 isochrones: drive-time bands radiating from the destination
p10, m10 = fit(base_mark())
dx, dy = m10.mapXY(XR, YB).x(), m10.mapXY(XR, YB).y()
bands = "".join(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="{r}" fill="{c}"/>' for r, c in [(900, CY), (680, "#0c6377"), (480, CY2), (300, CY3)])
V[10] = svg(solid(CY), p10, under=bands)
# 11 graticule: survey grid with orange tick crosses
grid = "".join(f'<path d="M{i} 0V1024M0 {i}H1024" stroke="{CY3}" stroke-width="4"/>' for i in range(128, 1024, 128)) + "".join(f'<path d="M{x-16} {y}h32M{x} {y-16}v32" stroke="{OR2}" stroke-width="5"/>' for x in (128, 896) for y in (128, 896))
V[11] = svg(solid(CY), fit(base_mark())[0], under=grid)
# 12 quad sheet: neatline frame + orange corner ticks
p12 = fit(base_mark(), w=440)[0]
frame = f'<rect x="232" y="232" width="560" height="560" fill="none" stroke="{CREAM}" stroke-width="14"/><path d="M512 190v58M512 776v58M190 512h58M776 512h58" stroke="{OR2}" stroke-width="14"/>'
V[12] = svg(solid(CY), fit(base_mark(), w=420, cy=512)[0], overlay=frame)
# 13 knockout coin: cream disc, mark punched out in cyan
V[13] = svg(solid(CY), fit(base_mark(mark=CY, dest=OR))[0], under=f'<circle cx="512" cy="500" r="430" fill="{CREAM}"/>')
# 14 dual carriageway: M as two parallel lines
def dual():
    s = 112; outer = flat_valley(stroke(center(), s), s); inner = stroke(center(), 34, "miter")
    road = op(outer, inner, D)
    o_ring, d_ring, d_dot, hole_p = nodes(s)
    trunk = op(op(op(road, o_ring, U), d_ring, U), hole_p, D); trunk = op(trunk, d_dot, D)
    return [(trunk, CREAM), (d_dot, OR)]
V[14] = svg(solid(CY), fit(dual())[0])
# 15 directional: no destination dot, route ends in an orange arrowhead
def arrow():
    s = 104; line = flat_valley(stroke(center(yb=YB - 40), s), s)
    o_ring, _, _, hole_p = nodes(s); trunk = op(op(line, o_ring, U), hole_p, D)
    a = skia.Path(); a.moveTo(XR - 96, YB - 60); a.lineTo(XR + 96, YB - 60); a.lineTo(XR, YB + 70); a.close()
    return [(trunk, CREAM), (a, OR)]
V[15] = svg(solid(CY), fit(arrow())[0])
# 16 GPS trail: dotted approach into a solid route
def trail():
    s = 104; m = base_mark()
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{CREAM}" opacity="{o}"/>' for x, y, r, o in [(60, 930, 14, .35), (120, 890, 17, .55), (180, 850, 20, .8)])
    return m, dots
p16, m16 = fit(trail()[0], cx=560, cy=470, w=540)
ox, oy = m16.mapXY(XL, YB).x(), m16.mapXY(XL, YB).y()
dots16 = "".join(f'<circle cx="{ox - 60*i:.1f}" cy="{oy + 52*i:.1f}" r="{22 - 4*i}" fill="{CREAM}" opacity="{1 - .22*i:.2f}"/>' for i in range(1, 4))
V[16] = svg(solid(CY), p16, under=dots16)
# 17 app-tile: rounded square badge on deep field
V[17] = svg(solid(DEEP), fit(base_mark(), w=520, cy=512)[0], under=f'<rect x="132" y="132" width="760" height="760" rx="190" fill="{CY}"/><rect x="132" y="132" width="760" height="760" rx="190" fill="none" stroke="{OR}" stroke-width="10"/>')
# 18 stacked lockup: mark + outlined Archivo wordmark
p18 = fit(base_mark(), w=430, cy=420)[0]
V[18] = svg(solid(CY), p18, overlay=f'<path d="{word("MAPZIMUS", 92, 512, 790, track=6)}" fill="{CREAM}"/>')
# 19 soft depth: radial-lit field
V[19] = svg('<defs><radialGradient id="g" cx="35%" cy="30%" r="80%"><stop offset="0" stop-color="#14869c"/><stop offset="1" stop-color="#063845"/></radialGradient></defs><rect width="1024" height="1024" fill="url(#g)"/>', fit(base_mark())[0])
# 20 orange terrain: route offsets drawn as thin orange contours
p20, m20 = fit(base_mark())
cont = ""
for k in range(2, 9):
    o = stroke(center(yb=1500), 104 + 80 * k, "round"); o.transform(m20)
    cont += f'<path d="{d(stroke(o, 5, "round"))}" fill="{OR}" opacity="{.75 - k*.06:.2f}"/>'
V[20] = svg(solid(CY), p20, under=cont)

os.makedirs(OUT, exist_ok=True)
for k, s in V.items(): open(f"{OUT}/{k:02d}.svg", "w").write(s)
print(len(V), "options")
