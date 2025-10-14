class PathReconstructor:
    """Reconstruye camino mínimo a partir del diccionario de predecesores."""

    @staticmethod
    def reconstruct(predecesores, inicio, destino):
        """Devuelve la lista de nodos del camino (o None si no alcanzable)."""
        if destino not in predecesores:
            return None
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            if actual == inicio:
                break
            actual = predecesores.get(actual)
        if camino[-1] != inicio:
            return None
        camino.reverse()
        return camino
