from vertice import Vertex
from vertice  import VerticeNotFoundError



class Graph:
    """Grafo dirigido por defecto. Responsable solo de mantener vértices y aristas."""

    def __init__(self):
        self.vertex_list = {}
        self.num_vertex = 0

    def add_vertex(self, id):
        if id in self.vertex_list:
            return self.vertex_list[id]
        self.num_vertex += 1
        new_vertex = Vertex(id)
        self.vertex_list[id] = new_vertex
        return new_vertex

    def get_vertex(self, id):
        return self.vertex_list.get(id)

    def add_edge(self, from_id, to_id, weight=0):
        if from_id not in self.vertex_list:
            self.add_vertex(from_id)
        if to_id not in self.vertex_list:
            self.add_vertex(to_id)
        self.vertex_list[from_id].add_neighbor(to_id, weight)

    def get_vertices(self):
        return list(self.vertex_list.keys())

    def ensure_vertex_exists(self, id):
        if id not in self.vertex_list:
            raise VertexNotFoundError(f"Vértice '{id}' no existe en el grafo.")
