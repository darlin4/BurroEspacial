from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any
import math
import heapq


@dataclass
class StarNode:
    starId: int
    x: float
    y: float
    constellation: Optional[str] = None
    galaxy: Optional[int] = None
    is_hypergiant: bool = False
    research: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def distance_to(self, other: "StarNode") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.hypot(dx, dy)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "starId": self.starId,
            "x": self.x,
            "y": self.y,
            "constellation": self.constellation,
            "galaxy": self.galaxy,
            "is_hypergiant": self.is_hypergiant,
            "research": self.research,
            "metadata": self.metadata,
        }


@dataclass
class Edge:
    a: int
    b: int
    distance: float
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def other(self, node_id: int) -> int:
        return self.b if node_id == self.a else self.a

    def key(self) -> Tuple[int, int]:
        return (min(self.a, self.b), max(self.a, self.b))

    def to_dict(self) -> Dict[str, Any]:
        return {"a": self.a, "b": self.b, "distance": self.distance, "blocked": self.blocked, "metadata": self.metadata}


class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[int, StarNode] = {}
        self.adj: Dict[int, List[Edge]] = {}
        # set of edge keys to avoid duplicates
        self._edge_keys: Set[Tuple[int, int]] = set()

    def add_node(self, node: StarNode) -> None:
        self.nodes[int(node.starId)] = node
        self.adj.setdefault(int(node.starId), [])

    def add_edge(self, a_id: int, b_id: int, distance: Optional[float] = None, blocked: bool = False, metadata: Optional[Dict[str, Any]] = None) -> Edge:
        a_id = int(a_id)
        b_id = int(b_id)
        if a_id not in self.nodes or b_id not in self.nodes:
            raise KeyError(f"Node not found when adding edge: {a_id} - {b_id}")
        key = (min(a_id, b_id), max(a_id, b_id))
        if key in self._edge_keys:
            # find existing edge and return it
            for e in self.adj[a_id]:
                if e.key() == key:
                    return e
        na = self.nodes[a_id]
        nb = self.nodes[b_id]
        if distance is None:
            distance = na.distance_to(nb)
        metadata = metadata or {}
        edge = Edge(a=a_id, b=b_id, distance=float(distance), blocked=bool(blocked), metadata=metadata)
        self.adj[a_id].append(edge)
        self.adj[b_id].append(edge)
        self._edge_keys.add(key)
        return edge

    def neighbors(self, starId: int) -> List[Edge]:
        return list(self.adj.get(int(starId), []))

    def get_node(self, starId: int) -> StarNode:
        return self.nodes[int(starId)]

    def set_blocked(self, a_id: int, b_id: int, blocked: bool) -> None:
        key = (min(int(a_id), int(b_id)), max(int(a_id), int(b_id)))
        for e in self.adj.get(a_id, []):
            if e.key() == key:
                e.blocked = blocked
        for e in self.adj.get(b_id, []):
            if e.key() == key:
                e.blocked = blocked

    def connected_components(self) -> List[Set[int]]:
        seen: Set[int] = set()
        comps: List[Set[int]] = []
        for nid in self.nodes:
            if nid in seen:
                continue
            stack = [nid]
            comp: Set[int] = set()
            while stack:
                cur = stack.pop()
                if cur in comp:
                    continue
                comp.add(cur)
                seen.add(cur)
                for e in self.neighbors(cur):
                    other = e.other(cur)
                    if other not in comp:
                        stack.append(other)
            comps.append(comp)
        return comps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for k in sorted(self._edge_keys) for e in self.adj[k[0]] if e.key() == k],
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any], validate: bool = True) -> Tuple["Graph", List[str]]:
        """
        Construye un grafo a partir de un diccionario similar al JSON de constelaciones.
        Devuelve (graph, missing_refs)
        """
        g = cls()
        missing: Set[str] = set()
        # Expecting a top-level 'stars' list
        stars = data.get("stars") or data.get("starsList") or []
        for s in stars:
            sid = int(s.get("starId"))
            node = StarNode(
                starId=sid,
                x=float(s.get("x", 0)),
                y=float(s.get("y", 0)),
                constellation=s.get("constellation") or s.get("constelacion"),
                galaxy=s.get("galaxy"),
                is_hypergiant=bool(s.get("is_hypergiant", s.get("hipergigante", False))),
                research=s.get("research", {}),
                metadata={k: v for k, v in s.items() if k not in ("starId", "x", "y", "linkedTo", "constellation", "galaxy", "is_hypergiant", "research")},
            )
            g.add_node(node)

        # Second pass: edges from linkedTo
        for s in stars:
            sid = int(s.get("starId"))
            linked = s.get("linkedTo") or []
            for l in linked:
                target = l.get("starId")
                if target is None:
                    continue
                try:
                    tid = int(target)
                except Exception:
                    missing.add(str(target))
                    continue
                if tid not in g.nodes:
                    missing.add(str(tid))
                    continue
                blocked = bool(l.get("blocked", False))
                distance = l.get("distance")
                metadata = {k: v for k, v in l.items() if k not in ("starId", "blocked", "distance")}
                # add edge (Graph.add_edge handles duplicates)
                try:
                    g.add_edge(sid, tid, distance=distance, blocked=blocked, metadata=metadata)
                except KeyError:
                    missing.add(str(tid))

        missing_list = sorted(list(missing))
        if validate and missing_list:
            # return graph and missing refs; caller may choose to patch
            return g, missing_list
        return g, missing_list

    def shortest_path(self, start_id: int, goal_id: int, weight: str = "distance") -> Tuple[List[int], float]:
        """Dijkstra shortest path using edge.distance by default."""
        start_id = int(start_id)
        goal_id = int(goal_id)
        if start_id not in self.nodes or goal_id not in self.nodes:
            raise KeyError("start or goal node not in graph")
        dist: Dict[int, float] = {n: float("inf") for n in self.nodes}
        prev: Dict[int, Optional[int]] = {n: None for n in self.nodes}
        dist[start_id] = 0.0
        heap: List[Tuple[float, int]] = [(0.0, start_id)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == goal_id:
                break
            for e in self.neighbors(u):
                if e.blocked:
                    continue
                v = e.other(u)
                w = e.distance if weight == "distance" else e.metadata.get(weight, e.distance)
                nd = d + float(w)
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        if dist[goal_id] == float("inf"):
            return [], float("inf")
        # reconstruct path
        path: List[int] = []
        cur = goal_id
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path, dist[goal_id]
