import sys
src = open(sys.argv[3]).read().split("V = {}")[0]
OUTDIR = sys.argv[1]; sys.argv = [sys.argv[0], OUTDIR, sys.argv[2]]
exec(src)

def highway(dashed=False):
    s = 112; m = base_mark(s=s)
    if dashed:
        cl = stroke(center(), 22, "round", "round", [38, 34])
    else:
        cl = flat_valley(stroke(center(), 22), 22)
    cl = op(op(cl, circ(XR, YB, 64), D), circ(XL, YB, 64), D)
    return m[:1] + [(cl, OR2)] + m[1:]

def tile(inset=132, rx=190, outline=True, field=DEEP):
    t = f'<rect x="{inset}" y="{inset}" width="{1024-2*inset}" height="{1024-2*inset}" rx="{rx}" fill="{CY}"/>'
    if outline: t += f'<rect x="{inset}" y="{inset}" width="{1024-2*inset}" height="{1024-2*inset}" rx="{rx}" fill="none" stroke="{OR}" stroke-width="12"/>'
    return solid(field), t

F = {}
bg, t = tile()
F["A"] = svg(bg, fit(highway(), w=500, cy=508)[0], under=t)                       # straight merge of 7 + 17
bg, t = tile()
F["B"] = svg(bg, fit(highway(dashed=True), w=500, cy=508)[0], under=t)            # lane-marking centre line
bg, t = tile(inset=72, rx=230)
F["C"] = svg(bg, fit(highway(), w=560, cy=508)[0], under=t)                       # bigger tile, bigger mark (survives circle crop)
import os; os.makedirs(OUTDIR, exist_ok=True)
for k, s in F.items(): open(f"{OUTDIR}/final-{k}.svg", "w").write(s)

# ---- locked: B kit ----
K = {}
bg, t = tile(); K["mapzimus-logo"] = svg(bg, fit(highway(dashed=True), w=500, cy=508)[0], under=t)
bg, t = tile(field=CREAM); K["mapzimus-logo-light"] = svg(bg, fit(highway(dashed=True), w=500, cy=508)[0], under=t)
bg, t = tile(field="#141618"); K["mapzimus-logo-dark"] = svg(bg, fit(highway(dashed=True), w=500, cy=508)[0], under=t)
# icon: tile is the whole canvas (app icon / favicon); solid centre line for small sizes
icon_bg = f'<rect width="1024" height="1024" rx="230" fill="{CY}"/>'
K["mapzimus-icon"] = svg("", fit(highway(dashed=True), w=660, cy=508)[0], under=icon_bg)
K["mapzimus-favicon"] = svg("", fit(highway(dashed=False), w=720, cy=508)[0], under=icon_bg)
for k, s in K.items(): open(f"{OUTDIR}/{k}.svg", "w").write(s)
