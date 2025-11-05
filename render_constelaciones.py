"""
Utilities used by the GUI to load and render the constellations JSON.
This is a small, dependency-free module that provides the minimal API
expected by `views/components/mapa_widget.py` and `views/main_window.py`.

Functions:
- load_json(path)
- find_star_by_id(data, id)
- collect_coords_counts(data)
- compute_bounds(data)
- coord_to_canvas(x, y, minx, miny, w, h, canvas_w=800, canvas_h=800)
- generate_colors(n)

Also supports a simple `--test` mode when executed directly.
"""

from __future__ import annotations
import json
import os
import math
import sys
from typing import Tuple, Dict, Any, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_star_by_id(data: Dict[str, Any], sid) -> Dict[str, Any] | None:
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            if s.get('id') == sid:
                return s
    return None


def collect_coords_counts(data: Dict[str, Any]) -> Dict[tuple, int]:
    counts: Dict[tuple, int] = {}
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            coord = (s['coordenates']['x'], s['coordenates']['y'])
            counts[coord] = counts.get(coord, 0) + 1
    return counts


def compute_bounds(data: Dict[str, Any]) -> Tuple[float, float, float, float]:
    xs = []
    ys = []
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            xs.append(s['coordenates']['x'])
            ys.append(s['coordenates']['y'])
    if not xs or not ys:
        return 0.0, 0.0, 200.0, 200.0
    minx = min(xs)
    miny = min(ys)
    maxx = max(xs)
    maxy = max(ys)
    w = max(200.0, maxx - minx or 200.0)
    h = max(200.0, maxy - miny or 200.0)
    return float(minx), float(miny), float(w), float(h)


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    # h in [0,1]
    i = int(h * 6)
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return '#{0:02x}{1:02x}{2:02x}'.format(int(r * 255), int(g * 255), int(b * 255))


def generate_colors(n: int) -> List[str]:
    if n <= 0:
        return []
    colors = []
    for i in range(n):
        h = (i / max(1, n)) % 1.0
        colors.append(_hsv_to_hex(h, 0.7, 0.9))
    return colors


def coord_to_canvas(x: float, y: float, minx: float, miny: float, w: float, h: float,
                    canvas_w: int = 800, canvas_h: int = 800) -> Tuple[float, float]:
    """Map logical coordinates to canvas pixel coordinates.

    - Places a 20px margin around the drawing area.
    - If w or h are zero, fall back to 200.
    """
    if w == 0:
        w = 200.0
    if h == 0:
        h = 200.0
    margin = 20
    usable_w = max(10, canvas_w - 2 * margin)
    usable_h = max(10, canvas_h - 2 * margin)
    # normalized
    nx = (x - minx) / w
    ny = (y - miny) / h
    cx = margin + nx * usable_w
    # invert y so larger logical y sits lower on screen (typical cartesian -> screen)
    cy = margin + (1 - ny) * usable_h
    return float(cx), float(cy)


def headless_stats(path: str) -> None:
    data = load_json(path)
    consts = data.get('constellations', [])
    stars = sum(len(c.get('starts', [])) for c in consts)
    counts = collect_coords_counts(data)
    overlaps = sum(1 for v in counts.values() if v > 1)
    hyper = sum(1 for c in consts for s in c.get('starts', []) if s.get('hypergiant'))
    print(f"JSON cargado correctamente. Constelaciones: {len(consts)}, Estrellas: {stars}, Coordenadas únicas: {len(counts)} (sobrelapos: {overlaps}), Hipergigantes: {hyper}")


if __name__ == '__main__':
    # simple CLI for testing
    args = sys.argv[1:]
    if '--test' in args:
        cand = os.path.join(os.path.dirname(__file__), 'constelaciones.json')
        if os.path.exists(cand):
            headless_stats(cand)
        else:
            print('No se encontró constelaciones.json en la raíz. Pasa la ruta como argumento.')
    else:
        print('Módulo de utilidades para el render. Importa sus funciones desde tu GUI.')
