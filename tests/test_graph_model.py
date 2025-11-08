"""Simple tests for models/graph_model.py

Run with: python tests/test_graph_model.py
"""
import sys
from models.graph_model import Graph


def main():
    data = {
        "stars": [
            {"starId": 1, "x": 0, "y": 0, "linkedTo": [{"starId": 2}]},
            {"starId": 2, "x": 3, "y": 4, "linkedTo": [{"starId": 1}, {"starId": 3}]},
            {"starId": 3, "x": 3, "y": 0, "linkedTo": [{"starId": 2}]},
        ]
    }

    g, missing = Graph.from_json(data, validate=True)
    if missing:
        print("Missing refs:", missing)
        sys.exit(2)

    # nodes and edges
    assert len(g.nodes) == 3, f"expected 3 nodes, got {len(g.nodes)}"
    # edges should be 2 unique edges: 1-2 and 2-3
    keys = sorted(list(g._edge_keys))
    assert (1, 2) in keys and (2, 3) in keys, f"edges keys wrong: {keys}"

    # distance between 1 and 2 is 5.0 (3-4-5 triangle)
    path, cost = g.shortest_path(1, 2)
    assert path == [1, 2], f"unexpected path: {path}"
    assert abs(cost - 5.0) < 1e-6, f"unexpected cost: {cost}"

    print("test_graph_model: OK")


if __name__ == "__main__":
    main()
