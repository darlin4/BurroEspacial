class Vertice:
    def __init__(self, id):
        self.id = id                      # nombre estrella
        self.adjacent = {}                # diccionario: {vertice_vecino: peso}
        self.distancia = float('inf')     # distancia
        self.visitado = False             # marca si ya fue visitado
        self.anterior = None              # vértice anterior en el camino más corto

    def add_neighbor(self, vecino, peso=0):
        """Agrega un vecino con su peso (distancia)."""
        self.adjacent[vecino] = peso

    def get_connections(self):
        """Devuelve los vértices vecinos."""
        return self.adjacent.keys()

    def get_id(self):
        """Devuelve el nombre de la estrella."""
        return self.id

    def get_peso(self, vecino):
        """Devuelve el peso de la conexión a un vecino."""
        return self.adjacent[vecino]

    def __str__(self):
        """Representación en texto del vértice y sus conexioness."""
        return f"{self.id} conectado a {[x.id for x in self.adjacent]}"
