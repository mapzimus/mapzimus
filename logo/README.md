# Mapzimus route mark

An M drawn as one OSRM-style route: open **origin ring** → ruby **destination stop**.
Deep cyan + orange, with Archivo from mapzimus.com.

| Use | File |
|---|---|
| Avatars (GitHub, LinkedIn, Bluesky…) | `png/mapzimus-mark-cyan-400.png` (or `-1024`) |
| Large / banners / about page | `png/mapzimus-mark-*-terrain-1024.png` |
| Illustrator / print | `print/*.pdf` (open directly; fully outlined, no fonts) or `print/*.eps` |
| Web / editable vector | `mapzimus-mark-*.svg` (layers: background, terrain, mark) |
| Specs | `png/construction.png`, `board.png` |

**Construction (1024 artboard, u = 8px):** stroke 13u · outer shoulder radius 13u, inner corners sharp · ~55° diagonals ·
mitred valley with 3.5u flat · nodes R 10.5u, origin hole 4.5u, destination ring 3u · optical centre 12px above middle ·
terrain = route offsets every 5u, tone-on-tone.

**Palette:** Deep cyan `#0a5c6e` · Paper `#f4efe3` · Orange `#e4690c` (on cyan) / `#f28a2e` (on paper) / `#ff9a4a` (night) · Night `#141618` / `#eceeed`. Paper on cyan = 6.6:1 contrast.

**Don't:** stretch it, outline it, add drop shadows, or swap the ring and dot colors (orange is always the destination). Keep ≥ 8% margin inside any crop.
