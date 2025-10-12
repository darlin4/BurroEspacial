"""
Modelo de datos para representar una Galaxia en el sistema.
Una galaxia contiene múltiples constelaciones y estrellas.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from .estrella import Estrella, TipoEstrella
from .constelacion import Constelacion

@dataclass
class Galaxia:
    """
    Representa una galaxia en el sistema estelar.
    
    Attributes:
        id: Identificador único de la galaxia
        nombre: Nombre de la galaxia
        constelaciones: Lista de constelaciones en esta galaxia
        estrellas: Diccionario de estrellas indexadas por ID
        estrellas_hipergigantes: Lista de IDs de estrellas hipergigantes
        distancias: Matriz de distancias entre estrellas
        rutas_bloqueadas: Lista de tuplas (origen, destino) de rutas bloqueadas
    """
    
    id: str
    nombre: str
    constelaciones: List[Constelacion] = None
    estrellas: Dict[str, Estrella] = None
    estrellas_hipergigantes: List[str] = None
    distancias: Dict[tuple, float] = None
    rutas_bloqueadas: List[tuple] = None
    
    def __post_init__(self):
        if self.constelaciones is None:
            self.constelaciones = []
        if self.estrellas is None:
            self.estrellas = {}
        if self.estrellas_hipergigantes is None:
            self.estrellas_hipergigantes = []
        if self.distancias is None:
            self.distancias = {}
        if self.rutas_bloqueadas is None:
            self.rutas_bloqueadas = []
    
    def agregar_estrella(self, estrella: Estrella):
        """Agrega una estrella a la galaxia"""
        self.estrellas[estrella.id] = estrella
        
        if estrella.es_hipergigante():
            if len(self.estrellas_hipergigantes) < 2:  # Máximo 2 por galaxia
                self.estrellas_hipergigantes.append(estrella.id)
            else:
                raise ValueError(f"La galaxia {self.nombre} ya tiene el máximo de estrellas hipergigantes (2)")
    
    def agregar_constelacion(self, constelacion: Constelacion):
        """Agrega una constelación a la galaxia"""
        constelacion.galaxia_id = self.id
        self.constelaciones.append(constelacion)
    
    def calcular_distancia(self, estrella1_id: str, estrella2_id: str) -> float:
        """
        Calcula la distancia euclidiana entre dos estrellas.
        
        Args:
            estrella1_id: ID de la primera estrella
            estrella2_id: ID de la segunda estrella
            
        Returns:
            Distancia en años luz entre las estrellas
        """
        if estrella1_id not in self.estrellas or estrella2_id not in self.estrellas:
            raise ValueError("Una o ambas estrellas no existen en esta galaxia")
        
        # Verificar si ya está calculada
        clave = (estrella1_id, estrella2_id)
        clave_inversa = (estrella2_id, estrella1_id)
        
        if clave in self.distancias:
            return self.distancias[clave]
        if clave_inversa in self.distancias:
            return self.distancias[clave_inversa]
        
        # Calcular distancia euclidiana
        estrella1 = self.estrellas[estrella1_id]
        estrella2 = self.estrellas[estrella2_id]
        
        dx = estrella2.coordenada_x - estrella1.coordenada_x
        dy = estrella2.coordenada_y - estrella1.coordenada_y
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        
        # Guardar en ambas direcciones
        self.distancias[clave] = distancia
        self.distancias[clave_inversa] = distancia
        
        return distancia
    
    def obtener_estrellas_conectadas(self, estrella_id: str) -> List[str]:
        """Obtiene todas las estrellas conectadas a una estrella dada"""
        conectadas = set()
        
        for constelacion in self.constelaciones:
            if constelacion.tiene_estrella(estrella_id):
                conectadas.update(constelacion.obtener_estrellas_conectadas(estrella_id))
        
        return list(conectadas)
    
    def existe_ruta(self, origen_id: str, destino_id: str) -> bool:
        """Verifica si existe una ruta directa entre dos estrellas y no está bloqueada"""
        if (origen_id, destino_id) in self.rutas_bloqueadas:
            return False
        
        for constelacion in self.constelaciones:
            if constelacion.tiene_conexion(origen_id, destino_id):
                return True
        return False
    
    def bloquear_ruta(self, origen_id: str, destino_id: str):
        """Bloquea una ruta bidireccional entre dos estrellas"""
        if (origen_id, destino_id) not in self.rutas_bloqueadas:
            self.rutas_bloqueadas.append((origen_id, destino_id))
        if (destino_id, origen_id) not in self.rutas_bloqueadas:
            self.rutas_bloqueadas.append((destino_id, origen_id))
    
    def habilitar_ruta(self, origen_id: str, destino_id: str):
        """Habilita una ruta previamente bloqueada"""
        rutas_a_remover = [
            (origen_id, destino_id),
            (destino_id, origen_id)
        ]
        
        for ruta in rutas_a_remover:
            if ruta in self.rutas_bloqueadas:
                self.rutas_bloqueadas.remove(ruta)
    
    def obtener_estrellas_no_visitadas(self) -> List[str]:
        """Obtiene la lista de IDs de estrellas no visitadas"""
        return [estrella_id for estrella_id, estrella in self.estrellas.items() 
                if not estrella.visitada]
    
    def obtener_estrellas_visitadas(self) -> List[str]:
        """Obtiene la lista de IDs de estrellas visitadas"""
        return [estrella_id for estrella_id, estrella in self.estrellas.items() 
                if estrella.visitada]
    
    def resetear_visitas(self):
        """Resetea el estado de visita de todas las estrellas"""
        for estrella in self.estrellas.values():
            estrella.visitada = False
    
    def obtener_hipergigantes_disponibles(self) -> List[str]:
        """Obtiene las estrellas hipergigantes que pueden enviar a otra galaxia"""
        return [estrella_id for estrella_id in self.estrellas_hipergigantes 
                if self.estrellas[estrella_id].puede_viajar_galaxia()]
    
    def __str__(self) -> str:
        return f"Galaxia {self.nombre} ({len(self.estrellas)} estrellas, {len(self.constelaciones)} constelaciones)"