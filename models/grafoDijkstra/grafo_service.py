import heapq
from src.exceptions import VertexNotFoundError
    
class DijkstraService:
    """Servicio que calcula distancias mínimas usando Dijkstra."""

    @staticmethod
    def compute(graph, inicio):
        """Devuelve (distancias, predecesores).
        - distancias: dict nodo -> distancia mínima desde inicio
        - predecesores: dict nodo -> nodo anterior en el camino mínimo
        """
        graph.ensure_vertex_exists(inicio)

        # inicialización
        distancias = {v: float('inf') for v in graph.get_vertices()}
        predecesores = {v: None for v in graph.get_vertices()}
        distancias[inicio] = 0

        heap = [(0, inicio)]
        visited = set()

        while heap:
            d_u, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)

            if d_u > distancias[u]:
                continue

            vertex_u = graph.get_vertex(u)
            if vertex_u is None:
                continue

            for vecino, peso in vertex_u.get_connections().items():
                if graph.get_vertex(vecino) is None:
                    continue
                nueva_dist = distancias[u] + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    predecesores[vecino] = u
                    heapq.heappush(heap, (nueva_dist, vecino))

        return distancias, predecesores
