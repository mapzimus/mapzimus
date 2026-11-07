# Mapzimus route mark

An M drawn as one OSRM-style route: open **origin ring** → ruby **destination stop**.
Colors and type come from the mapzimus.com Quadrangle system.

| Use | File |
|---|---|
| Avatars (GitHub, LinkedIn, Bluesky…) | `png/mapzimus-mark-blue-400.png` (or `-1024`) |
| Large / banners / about page | `png/mapzimus-mark-*-terrain-1024.png` |
| Illustrator / print | `print/*.pdf` (open directly; fully outlined, no fonts) or `print/*.eps` |
| Web / editable vector | `mapzimus-mark-*.svg` (layers: background, terrain, mark) |
| Specs | `png/construction.png`, `board.png` |

**Construction (1024 artboard, u = 8px):** stroke 13u · outer shoulder radius 13u, inner corners sharp · ~55° diagonals ·
mitred valley with 3.5u flat · nodes R 10.5u, origin hole 4.5u, destination ring 3u · optical centre 12px above middle ·
terrain = route offsets every 5u, tone-on-tone.

**Palette:** Heritage Blue `#1e4a63` · Paper `#f4efe3` · Ruby `#b8323f` (on blue) / `#c03a46` (on paper) / `#c24a58` (night) · Night `#141618` / `#eceeed`.

**Don't:** stretch it, outline it, add drop shadows, or swap the ring and dot colors. Keep ≥ 8% margin inside any crop.
