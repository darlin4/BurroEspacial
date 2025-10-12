"""
Modelo de datos para representar la Nave espacial en el sistema.
La nave transporta al burro y tiene propiedades de navegación.
"""

from dataclasses import dataclass
from typing import Optional, List
from .burro import Burro

@dataclass
class Nave:
    """
    Representa la nave espacial que transporta al burro.
    
    Attributes:
        id: Identificador único de la nave
        nombre: Nombre de la nave
        burro: Instancia del burro que transporta
        estrella_actual: ID de la estrella donde se encuentra
        galaxia_actual: ID de la galaxia donde se encuentra
        en_viaje: Indica si la nave está actualmente viajando
        destino: ID de la estrella de destino si está en viaje
        velocidad: Velocidad de la nave (años luz por unidad de tiempo)
    """
    
    id: str = "NAVE-001"
    nombre: str = "Burro Express"
    burro: Optional[Burro] = None
    estrella_actual: Optional[str] = None
    galaxia_actual: Optional[str] = None
    en_viaje: bool = False
    destino: Optional[str] = None
    velocidad: float = 1.0  # años luz por unidad de tiempo
    
    def __post_init__(self):
        if self.burro is None:
            self.burro = Burro()
    
    def iniciar_viaje(self, destino_id: str):
        """Inicia un viaje hacia una estrella destino"""
        if not self.burro.esta_vivo():
            raise ValueError("No se puede viajar con un burro muerto")
        
        self.en_viaje = True
        self.destino = destino_id
    
    def finalizar_viaje(self):
        """Finaliza el viaje y actualiza la posición"""
        if self.destino:
            self.estrella_actual = self.destino
            self.burro.mover_a_estrella(self.destino)
        
        self.en_viaje = False
        self.destino = None
    
    def viajar_a_estrella(self, estrella_destino_id: str, distancia: float):
        """
        Viaja a una estrella específica, consumiendo tiempo de vida.
        
        Args:
            estrella_destino_id: ID de la estrella destino
            distancia: Distancia en años luz
        """
        if not self.burro.esta_vivo():
            raise ValueError("No se puede viajar con un burro muerto")
        
        # Consumir tiempo de vida por el viaje
        tiempo_viaje = distancia / self.velocidad
        self.burro.consumir_tiempo_vida(tiempo_viaje)
        
        # Si el burro sigue vivo, mover la nave
        if self.burro.esta_vivo():
            self.estrella_actual = estrella_destino_id
            self.burro.mover_a_estrella(estrella_destino_id)
        
        return tiempo_viaje
    
    def viajar_a_galaxia(self, galaxia_destino_id: str):
        """
        Viaja a otra galaxia usando una estrella hipergigante.
        Recarga al burro con los beneficios del viaje intergaláctico.
        """
        if not self.burro.esta_vivo():
            raise ValueError("No se puede viajar con un burro muerto")
        
        # Aplicar beneficios del viaje hipergigante
        self.burro.recargar_hipergigante()
        
        # Cambiar de galaxia
        self.galaxia_actual = galaxia_destino_id
        self.estrella_actual = None  # Se definirá el destino específico
    
    def aterrizar_en_estrella(self, estrella_id: str):
        """Aterriza en una estrella específica dentro de la galaxia actual"""
        self.estrella_actual = estrella_id
        self.burro.mover_a_estrella(estrella_id)
    
    def puede_viajar(self) -> bool:
        """Verifica si la nave puede viajar"""
        return not self.en_viaje and self.burro.esta_vivo()
    
    def obtener_estado(self) -> dict:
        """Obtiene el estado completo de la nave y el burro"""
        return {
            'nave_id': self.id,
            'nombre': self.nombre,
            'estrella_actual': self.estrella_actual,
            'galaxia_actual': self.galaxia_actual,
            'en_viaje': self.en_viaje,
            'destino': self.destino,
            'burro_estado': self.burro.obtener_estado_porcentual() if self.burro else None,
            'burro_vivo': self.burro.esta_vivo() if self.burro else False
        }
    
    def __str__(self) -> str:
        estado_viaje = "En viaje" if self.en_viaje else "En reposo"
        ubicacion = f"Estrella: {self.estrella_actual}" if self.estrella_actual else "Sin ubicación"
        return f"Nave {self.nombre} - {estado_viaje} - {ubicacion}"