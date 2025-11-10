"""
Pathfinding / Optimizer prototype

Proporciona una implementación simple (time-limited DFS con poda básica)
que intenta maximizar el número de estrellas visitadas y, entre soluciones
con igual cobertura, minimizar el gasto energético total.

Reglas implementadas (suposiciones documentadas):
- Cada estrella en el JSON puede contener:
  - timeToEat: tiempo (unidades) para consumir 1 kg de pasto (validado en procesador_json)
  - amountOfEnergy: valor nutritivo indicado en JSON (no usado directamente aquí)
  - research_energy_cost_per_time: energía consumida por unidad de tiempo durante investigación
  - research_life_delta_per_time: delta de tiempo de vida (puede ser negativo)
  - opcional: visit_time (si está, es la "estadía" total en la estrella)
- Si no existe `visit_time` se usa un valor por defecto VISIT_TIME_DEFAULT.
- Al llegar, si la energía del burro < 50% y hay pasto en bodega, el burro intentará
  comer hasta recuperar energía usando como máximo el 50% de la estadía para comer.
  El número máximo de kg comestibles queda limitado por: pasto disponible y
  (visit_time * 0.5) / timeToEat.
- La energía recuperada por kg depende del estado de salud del Burro (usamos
  la misma tabla que `models.burro.Burro._obtener_eficiencia_pasto`).
- La fracción restante del tiempo de estadía se usa para investigación: consume
  research_energy_cost_per_time * research_time y aplica research_life_delta_per_time * research_time
  a la vida del burro.

El optimizador explora rutas evitando visitar una estrella más de una vez.
Devuelve la mejor ruta encontrada y estadísticas (estrellas visitadas, energía final, pasto final, vida final, pasos).
"""
from __future__ import annotations

import time
from typing import Dict, Any, Tuple, List, Optional

from models.burro import Burro, EstadoSalud

VISIT_TIME_DEFAULT = 10.0  # units of time per visit (assumption)


def _salud_factor(salud_str: str) -> float:
    m = {
        'excelente': 0.5,
        'buena': 0.7,
        'mala': 1.0,
        'moribundo': 1.5,
        'muerto': 999.0
    }
    return m.get(salud_str.lower(), 1.0)


def propose_route(grafo: Dict[str, Dict[str, float]], json_data: Dict[str, Any], origen: str,
                  burro_init: Dict[str, Any], time_limit_seconds: float = 2.0,
                  max_nodes_explored: int = 20000,
                  forced_jumps: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Propuesta de ruta optimizada.

    grafo: mapping label -> {neighbor_label: distance}
    json_data: original JSON dict (para leer timeToEat, research params)
    origen: label de la estrella origen
    burro_init: dict con keys 'salud','edad','energia','pasto','tiempo_vida' (opcional)
    """
    start_time = time.time()

    # helper to find star metadata by label
    def find_star(label: str) -> Optional[Dict[str, Any]]:
        for c in json_data.get('constellations', []):
            for s in c.get('starts', []):
                if s.get('label') == label or str(s.get('id')) == str(label):
                    return s
        return None

    # build initial burro
    b = Burro()
    salud = burro_init.get('salud', 'excelente')
    # map salud string to enum
    try:
        b.estado_salud = EstadoSalud[salud.upper()]
    except Exception:
        # fallback
        b.estado_salud = EstadoSalud.EXCELENTE
    b.edad = float(burro_init.get('edad', b.edad))
    b.burroenergia = float(burro_init.get('energia', b.burroenergia))
    b.pasto_bodega = float(burro_init.get('pasto', b.pasto_bodega))
    b.tiempo_vida = float(burro_init.get('tiempo_vida', b.tiempo_vida))

    best = {
        'ruta': [origen],
        'estrellas_visitadas': 1,
        'energia_final': b.burroenergia,
        'pasto_final': b.pasto_bodega,
        'tiempo_vida_final': b.tiempo_vida,
        'pasos': []
    }

    nodes_explored = 0

    # DFS with pruning: maximize visited count, tie-breaker minimize energy spent (i.e., maximize energia_final)
    def dfs(actual_label: str, burro_state: Burro, visited: List[str], pasos: List[Dict[str, Any]]):
        nonlocal best, nodes_explored
        if nodes_explored > max_nodes_explored:
            return
        if time.time() - start_time > time_limit_seconds:
            return
        nodes_explored += 1

        # update best
        if len(visited) > best['estrellas_visitadas'] or (len(visited) == best['estrellas_visitadas'] and burro_state.burroenergia > best['energia_final']):
            best = {
                'ruta': visited.copy(),
                'estrellas_visitadas': len(visited),
                'energia_final': burro_state.burroenergia,
                'pasto_final': burro_state.pasto_bodega,
                'tiempo_vida_final': burro_state.tiempo_vida,
                'pasos': pasos.copy()
            }

        # explore neighbors
        for vecino, distancia in grafo.get(actual_label, {}).items():
            if vecino in visited:
                continue

            # simulate travel: energy and time costs
            factor = _salud_factor(burro_state.estado_salud.name.lower())
            consumo_energia_viaje = distancia * factor * 0.5
            consumo_pasto_viaje = distancia * 0.05  # same heuristic as panel_rutas
            consumo_tiempo_viaje = distancia  # time reduces by distance

            # make a copy of burro state
            b2 = Burro(**vars(burro_state))

            # apply travel costs
            b2.consumir_energia(consumo_energia_viaje)
            # model pasto consumption during travel as reduction from bodega
            b2.pasto_bodega = max(0.0, b2.pasto_bodega - consumo_pasto_viaje)
            b2.consumir_tiempo_vida(consumo_tiempo_viaje)

            if not b2.esta_vivo():
                continue

            # arrival: retrieve star params
            star = find_star(vecino)
            time_to_eat = float(star.get('timeToEat', VISIT_TIME_DEFAULT)) if star else VISIT_TIME_DEFAULT
            amount_of_energy = float(star.get('amountOfEnergy', 1)) if star else 1.0
            visit_time = float(star.get('visit_time', VISIT_TIME_DEFAULT)) if star else VISIT_TIME_DEFAULT
            research_cost = float(star.get('research_energy_cost_per_time', 0)) if star else 0.0
            research_life_delta = float(star.get('research_life_delta_per_time', 0)) if star else 0.0
            research_health_delta = float(star.get('research_health_delta_per_time', 0)) if star else 0.0
            is_hyper = bool(star.get('hypergiant', False)) if star else False
            # Per spec: hypergiant jumps recarga 50% de la energía actual y duplica el pasto
            # We enforce these values to match the requirement; JSON overrides are ignored
            jump_recharge_pct = 0.5
            jump_pasto_multiplier = 2.0

            # determine eat_time (50% of visit_time)
            eat_time = visit_time * 0.5
            research_time = visit_time - eat_time

            # if needs pasto (energia <50%) try to eat
            eaten_kg = 0.0
            energia_before_eat = b2.burroenergia
            if b2.necesita_pasto() and b2.pasto_bodega > 0:
                max_kg_by_time = eat_time / time_to_eat if time_to_eat > 0 else 0
                max_kg_by_time = max(0.0, max_kg_by_time)
                kg_to_eat = min(b2.pasto_bodega, max_kg_by_time)
                eaten_kg = b2.comer_pasto(kg_to_eat)

            # research consumes energy and affects life
            energia_consumida_research = research_cost * research_time
            b2.consumir_energia(energia_consumida_research)
            b2.consumir_tiempo_vida(0)  # research does not directly consume life; life delta added below
            # apply life delta
            delta_life = research_life_delta * research_time
            if delta_life != 0:
                if delta_life > 0:
                    b2.ganar_tiempo_vida(delta_life)
                else:
                    b2.consumir_tiempo_vida(-delta_life)

            # apply health delta: convert per-time delta into integer health changes
            if research_health_delta != 0:
                try:
                    total_health_delta = research_health_delta * research_time
                    # round to nearest integer for health state changes
                    health_change = int(round(total_health_delta))
                    if health_change != 0:
                        b2.cambiar_salud(health_change)
                except Exception:
                    pass

            # discard if dead
            if not b2.esta_vivo():
                continue

            paso = {
                'desde': actual_label,
                'hacia': vecino,
                'distancia': distancia,
                'consumo_energia_viaje': consumo_energia_viaje,
                'consumo_pasto_viaje': consumo_pasto_viaje,
                'eaten_kg': eaten_kg,
                'energia_antes': energia_before_eat,
                'energia_despues': b2.burroenergia,
                'pasto_restante': b2.pasto_bodega,
                'tiempo_vida_restante': b2.tiempo_vida,
                'hypergiant': is_hyper,
                'estado_salud': b2.estado_salud.name.lower()
            }

            # Normal move
            dfs(vecino, b2, visited + [vecino], pasos + [paso])

            # If arrival is a hypergiant, allow a jump to a star in a different galaxy
            # (these jumps represent multi-galaxy transfers; they recharge and increase pasto)
            if is_hyper and star:
                try:
                    origin_galaxy = int(star.get('galaxy', -1))
                except Exception:
                    origin_galaxy = -1

                # Per requirement: allow scientist to define destination in the NEXT galaxy
                target_galaxy = origin_galaxy + 1

                # enumerate candidate targets in the next galaxy only
                for c in json_data.get('constellations', []):
                    for s_target in c.get('starts', []):
                        try:
                            tgt_gal = int(s_target.get('galaxy', -1))
                        except Exception:
                            tgt_gal = -1
                        if tgt_gal != target_galaxy:
                            continue
                        dst_label = s_target.get('label')
                        if not dst_label:
                            continue

                        # If a forced jump is specified for this hypergiant, skip other candidates
                        if forced_jumps and isinstance(forced_jumps, dict):
                            star_label = star.get('label') if star else None
                            if star_label in forced_jumps:
                                forced_dst = forced_jumps.get(star_label)
                                if forced_dst != dst_label:
                                    continue

                        # simulate the jump: copy state after arrival
                        b3 = Burro(**vars(b2))

                        # Apply exact hypergiant effects per spec
                        try:
                            b3.burroenergia = min(100.0, b3.burroenergia + (b3.burroenergia * jump_recharge_pct))
                        except Exception:
                            pass
                        try:
                            b3.pasto_bodega = b3.pasto_bodega * jump_pasto_multiplier
                        except Exception:
                            pass

                        paso_jump = dict(paso)
                        paso_jump.update({'jump_to': dst_label, 'jump_recharge_pct': jump_recharge_pct, 'jump_pasto_multiplier': jump_pasto_multiplier, 'target_galaxy': target_galaxy})
                        paso_jump['estado_salud'] = b3.estado_salud.name.lower()

                        # continue DFS from the jump destination, mark it visited
                        dfs(dst_label, b3, visited + [vecino, dst_label], pasos + [paso_jump])

    # start DFS
    dfs(origen, b, [origen], [])

    # attach nodes_explored
    best['nodes_explored'] = nodes_explored
    best['time_taken'] = time.time() - start_time
    return best


if __name__ == '__main__':
    # simple smoke test if run directly
    import json
    from pathlib import Path

    repo = Path(__file__).resolve().parents[2]
    jsf = repo / 'constelaciones.json'
    data = json.loads(jsf.read_text(encoding='utf-8'))

    # build simple grafo from labels like panel_rutas
    grafo = {}
    for c in data.get('constellations', []):
        for s in c.get('starts', []):
            nombre = s.get('label')
            grafo.setdefault(nombre, {})
            for link in s.get('linkedTo', []):
                if link.get('blocked'):
                    continue
                dst = link.get('starId')
                # find dst label
                dst_label = None
                for c2 in data.get('constellations', []):
                    for s2 in c2.get('starts', []):
                        if s2.get('id') == dst:
                            dst_label = s2.get('label')
                            break
                    if dst_label:
                        break
                if dst_label:
                    grafo[nombre][dst_label] = link.get('distance', 1.0)

    res = propose_route(grafo, data, list(grafo.keys())[0], {'salud': 'excelente', 'edad': 5.0, 'energia': 100.0, 'pasto': 10.0})
    print('Smoke test result:', res['ruta'], 'visited', res['estrellas_visitadas'])
