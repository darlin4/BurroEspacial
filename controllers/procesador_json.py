import json
from typing import Any, Dict, List, Set, Tuple


def load_json(path_or_data: Any) -> Dict:
    if isinstance(path_or_data, str):
        with open(path_or_data, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif isinstance(path_or_data, dict):
        return path_or_data
    else:
        raise TypeError('path_or_data debe ser ruta o dict')


def collect_star_ids(data: Dict) -> Set[int]:
    ids = set()
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            ids.add(int(s['id']))
    return ids


def find_missing_references(data: Dict) -> Tuple[Set[int], Dict[int, List[int]]]:
    """Return (missing_ids, missing_by_source)"""
    ids = collect_star_ids(data)
    missing = set()
    missing_by_source = {}
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            src = int(s['id'])
            for link in s.get('linkedTo', []):
                tgt = int(link['starId'])
                if tgt not in ids:
                    missing.add(tgt)
                    missing_by_source.setdefault(src, []).append(tgt)
    return missing, missing_by_source


def validate_schema(data: Dict) -> List[str]:
    errors = []
    if 'constellations' not in data or not isinstance(data['constellations'], list):
        errors.append('Falta campo "constellations" o no es lista')
        return errors
    for ci, c in enumerate(data['constellations']):
        if 'starts' not in c or not isinstance(c['starts'], list):
            errors.append(f'constellation[{ci}] falta "starts" o no es lista')
            continue
        for si, s in enumerate(c['starts']):
            if 'id' not in s:
                errors.append(f'constellation[{ci}].starts[{si}] falta id')
            if 'coordenates' not in s or 'x' not in s['coordenates'] or 'y' not in s['coordenates']:
                errors.append(f'constellation[{ci}].starts[{si}] falta coordenates.x/y')
            # basic types
            if 'timeToEat' in s and not isinstance(s['timeToEat'], (int, float)):
                errors.append(f'constellation[{ci}].starts[{si}].timeToEat debe ser número')
            # optional research fields
            if 'research_energy_cost_per_time' in s and not isinstance(s['research_energy_cost_per_time'], (int, float)):
                errors.append(f'constellation[{ci}].starts[{si}].research_energy_cost_per_time debe ser número')
            if 'research_life_delta_per_time' in s and not isinstance(s['research_life_delta_per_time'], (int, float)):
                errors.append(f'constellation[{ci}].starts[{si}].research_life_delta_per_time debe ser número')
    return errors


def generar_parche_missing_stars(missing: Set[int]) -> List[Dict]:
    """Genera entradas mínimas sugeridas para cada missing id. No infiere constellation; caller decide dónde insertarlas."""
    parche = []
    for mid in sorted(missing):
        entry = {
            'id': mid,
            'label': f'Auto{mid}',
            'linkedTo': [],
            'radius': 0.4,
            'timeToEat': 2,
            'amountOfEnergy': 1,
            'coordenates': {'x': 0, 'y': 0},
            'hypergiant': False,
            # investigación por defecto: coste de energía por unidad de tiempo y delta de vida por unidad de tiempo
            'research_energy_cost_per_time': 0,
            'research_life_delta_per_time': 0
        }
        parche.append(entry)
    return parche


def aplicar_parche_a_data(data: Dict, parche: List[Dict], target_constellation_name: str = None) -> Dict:
    """Inserta las entradas del parche en la constelación indicada o en la primera si no se da."""
    data = dict(data)  # shallow copy
    consts = data.setdefault('constellations', [])
    if target_constellation_name:
        for c in consts:
            if c.get('name') == target_constellation_name:
                target = c
                break
        else:
            target = consts[0] if consts else {'name': 'Default', 'starts': []}
            if target not in consts:
                consts.append(target)
    else:
        target = consts[0] if consts else {'name': 'Default', 'starts': []}
        if target not in consts:
            consts.append(target)
    starts = target.setdefault('starts', [])
    for e in parche:
        starts.append(e)
    return data


def summary(data: Dict) -> str:
    ids = collect_star_ids(data)
    missing, missing_by_source = find_missing_references(data)
    return f"Estrellas definidas: {len(ids)}; referencias faltantes: {sorted(missing)}; detalles: {missing_by_source}"


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Uso: procesador_json.py <archivo.json>')
        sys.exit(1)
    path = sys.argv[1]
    data = load_json(path)
    errors = validate_schema(data)
    if errors:
        print('Errores de esquema:')
        for e in errors:
            print(' -', e)
    missing, missing_by_source = find_missing_references(data)
    if missing:
        print('Faltan definiciones de estrellas referenciadas:', sorted(missing))
        parche = generar_parche_missing_stars(missing)
        print('\nParche sugerido (no aplicado):')
        print(json.dumps(parche, indent=2, ensure_ascii=False))
    else:
        print('No faltan referencias. OK.')
"""
Procesador JSON para el sistema de navegación espacial.
Maneja la carga y conversión de archivos JSON a objetos del modelo.
"""

# Aquí iría la implementación del ProcesadorJSON
# - Carga de archivos JSON
# - Validación de estructura JSON
# - Conversión a objetos del modelo de datos
# - Manejo de errores de formato