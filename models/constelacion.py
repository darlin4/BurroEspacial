"""
Modelo de datos para representar una Constelación en el sistema.
Una constelación es un conjunto de estrellas conectadas con un color específico.
"""

from dataclasses import dataclass
from typing import List, Tuple
import random

@dataclass
class Constelacion:
    """
    Representa una constelación en el mapa estelar.
    
    Attributes:
        id: Identificador único de la constelación
        nombre: Nombre de la constelación
        estrellas: Lista de IDs de estrellas que pertenecen a esta constelación
        conexiones: Lista de tuplas (estrella_origen_id, estrella_destino_id) representando las rutas
        color: Color RGB para representar la constelación en el mapa
        galaxia_id: ID de la galaxia a la que pertenece esta constelación
    """
    
    id: str
    nombre: str
    estrellas: List[str] = None
    conexiones: List[Tuple[str, str]] = None
    color: Tuple[int, int, int] = None  # RGB
    galaxia_id: str = ""
    
    def __post_init__(self):
        if self.estrellas is None:
            self.estrellas = []
        if self.conexiones is None:
            self.conexiones = []
        if self.color is None:
            self.color = self._generar_color_aleatorio()
    
    def _generar_color_aleatorio(self) -> Tuple[int, int, int]:
        """Genera un color RGB aleatorio para la constelación"""
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    
    def agregar_estrella(self, estrella_id: str):
        """Agrega una estrella a la constelación"""
        if estrella_id not in self.estrellas:
            self.estrellas.append(estrella_id)
    
    def agregar_conexion(self, origen_id: str, destino_id: str):
        """Agrega una conexión bidireccional entre dos estrellas"""
        conexion_directa = (origen_id, destino_id)
        conexion_inversa = (destino_id, origen_id)
        
        if conexion_directa not in self.conexiones:
            self.conexiones.append(conexion_directa)
        if conexion_inversa not in self.conexiones:
            self.conexiones.append(conexion_inversa)
    
    def tiene_estrella(self, estrella_id: str) -> bool:
        """Verifica si una estrella pertenece a esta constelación"""
        return estrella_id in self.estrellas
    
    def tiene_conexion(self, origen_id: str, destino_id: str) -> bool:
        """Verifica si existe una conexión entre dos estrellas"""
        return (origen_id, destino_id) in self.conexiones
    
    def obtener_estrellas_conectadas(self, estrella_id: str) -> List[str]:
        """Obtiene todas las estrellas conectadas directamente a una estrella dada"""
        conectadas = []
        for origen, destino in self.conexiones:
            if origen == estrella_id:
                conectadas.append(destino)
        return conectadas
    
    def __str__(self) -> str:
        return f"Constelación {self.nombre} ({len(self.estrellas)} estrellas)"