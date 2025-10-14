class Vertex:
    def __init__(self, id):
        self.id = id
        self.adjacent = {}  # dict: neighbor_id -> weight

    def add_neighbor(self, neighbor, weight=0):
        """Agregar un vecino (por id) con su peso."""
        self.adjacent[neighbor] = weight

    def get_connections(self):
        """Devuelve el diccionario de adyacencias (neighbor_id -> weight)."""
        return self.adjacent

    def get_id(self):
        return self.id
