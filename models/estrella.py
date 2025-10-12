"""
Modelo de datos para representar una Estrella en el sistema.
Una estrella tiene coordenadas, propiedades de consumo de energía,
tiempo de investigación y puede pertenecer a múltiples constelaciones.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class TipoEstrella(Enum):
    """Tipos de estrellas en el sistema"""
    NORMAL = "normal"
    HIPERGIGANTE = "hipergigante"

@dataclass
class Estrella:
    """
    Representa una estrella en el mapa estelar.
    
    Attributes:
        id: Identificador único de la estrella
        nombre: Nombre de la estrella
        coordenada_x: Posición X en el mapa (unidades de medida)
        coordenada_y: Posición Y en el mapa (unidades de medida) 
        tipo: Tipo de estrella (normal o hipergigante)
        tiempo_investigacion: Tiempo base de investigación en la estrella
        energia_consumida_investigacion: Energía que consume el burro por unidad de tiempo investigando
        tiempo_consumo_pasto: Tiempo necesario para consumir 1kg de pasto
        constelaciones: Lista de IDs de constelaciones a las que pertenece
        tiempo_vida_ganado: Tiempo de vida ganado/perdido por investigaciones (puede ser negativo)
        cambio_salud: Cambio en el estado de salud del burro tras investigaciones
        visitada: Indica si la estrella ya fue visitada
        galaxia_destino: Para hipergigantes, ID de galaxia a la que puede enviar al burro
    """
    
    id: str
    nombre: str
    coordenada_x: float
    coordenada_y: float
    tipo: TipoEstrella = TipoEstrella.NORMAL
    tiempo_investigacion: float = 0.0  # Tiempo en unidades de tiempo
    energia_consumida_investigacion: float = 0.0  # Energía por unidad de tiempo
    tiempo_consumo_pasto: float = 1.0  # Tiempo para consumir 1kg de pasto
    constelaciones: List[str] = None  # Lista de IDs de constelaciones
    tiempo_vida_ganado: float = 0.0  # Puede ser negativo
    cambio_salud: int = 0  # Cambio en nivel de salud (-2, -1, 0, +1, +2)
    visitada: bool = False
    galaxia_destino: Optional[str] = None  # Solo para hipergigantes
    
    def __post_init__(self):
        if self.constelaciones is None:
            self.constelaciones = []
    
    def pertenece_multiples_constelaciones(self) -> bool:
        """Verifica si la estrella pertenece a múltiples constelaciones"""
        return len(self.constelaciones) > 1
    
    def es_hipergigante(self) -> bool:
        """Verifica si la estrella es hipergigante"""
        return self.tipo == TipoEstrella.HIPERGIGANTE
    
    def puede_viajar_galaxia(self) -> bool:
        """Verifica si la estrella puede enviar el burro a otra galaxia"""
        return self.es_hipergigante() and self.galaxia_destino is not None
    
    def marcar_visitada(self):
        """Marca la estrella como visitada"""
        self.visitada = True
    
    def agregar_constelacion(self, constelacion_id: str):
        """Agrega una constelación a la lista de constelaciones de la estrella"""
        if constelacion_id not in self.constelaciones:
            self.constelaciones.append(constelacion_id)
    
    def __str__(self) -> str:
        return f"Estrella {self.nombre} ({self.coordenada_x}, {self.coordenada_y})"