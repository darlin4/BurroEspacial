from utils.algorithms import pathfinding


def make_sample_json():
    return {
        'constellations': [
            {'name': 'C1', 'starts': [{'id': 1, 'label': 'A', 'linkedTo': []}]},
            {'name': 'C2', 'starts': [{'id': 2, 'label': 'B', 'linkedTo': []}]}
        ]
    }


def test_propose_route_basic():
    grafo = {
        'A': {'B': 1.0},
        'B': {'A': 1.0}
    }
    data = make_sample_json()
    res = pathfinding.propose_route(grafo, data, 'A', {'salud': 'excelente', 'edad': 5.0, 'energia': 100.0, 'pasto': 10.0}, time_limit_seconds=0.5)
    assert isinstance(res, dict)
    assert 'ruta' in res
    assert isinstance(res['ruta'], list)
    # at least the origin must be present
    assert res['ruta'][0] == 'A'
