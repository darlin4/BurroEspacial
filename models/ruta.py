"""
Modelo de datos para representar una Ruta en el sistema.
Una ruta es una secuencia de estrellas que el burro visitará.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class TipoRuta(Enum):
    """Tipos de rutas que puede calcular el sistema"""
    MAXIMAS_ESTRELLAS_INICIAL = "maximas_estrellas_inicial"  # Máximas estrellas con condiciones iniciales
    OPTIMA_RECURSOS = "optima_recursos"  # Óptima considerando recursos y gestión

@dataclass
class PasoRuta:
    """
    Representa un paso individual en una ruta.
    
    Attributes:
        estrella_id: ID de la estrella a visitar
        tiempo_viaje: Tiempo de viaje hasta esta estrella
        tiempo_investigacion: Tiempo de investigación en la estrella
        tiempo_alimentacion: Tiempo dedicado a comer pasto
        energia_consumida: Energía consumida en este paso
        pasto_consumido: Cantidad de pasto consumido
        energia_ganada: Energía ganada por alimentación
        tiempo_vida_cambio: Cambio en tiempo de vida (puede ser negativo)
        cambio_salud: Cambio en el estado de salud
        orden: Orden del paso en la ruta (empezando desde 1)
    """
    
    estrella_id: str
    tiempo_viaje: float = 0.0
    tiempo_investigacion: float = 0.0
    tiempo_alimentacion: float = 0.0
    energia_consumida: float = 0.0
    pasto_consumido: float = 0.0
    energia_ganada: float = 0.0
    tiempo_vida_cambio: float = 0.0
    cambio_salud: int = 0
    orden: int = 0

@dataclass
class Ruta:
    """
    Representa una ruta completa que el burro seguirá.
    
    Attributes:
        id: Identificador único de la ruta
        tipo: Tipo de ruta calculada
        estrella_origen: ID de la estrella de origen
        pasos: Lista de pasos de la ruta en orden
        distancia_total: Distancia total de la ruta en años luz
        tiempo_total: Tiempo total estimado de la ruta
        estrellas_visitadas: Número de estrellas que se visitarán
        factible: Indica si la ruta es factible con los recursos iniciales
        energia_final: Energía estimada al final de la ruta
        pasto_final: Pasto estimado al final de la ruta
        tiempo_vida_final: Tiempo de vida estimado al final de la ruta
        observaciones: Lista de observaciones o advertencias sobre la ruta
    """
    
    id: str
    tipo: TipoRuta
    estrella_origen: str
    pasos: List[PasoRuta] = None
    distancia_total: float = 0.0
    tiempo_total: float = 0.0
    estrellas_visitadas: int = 0
    factible: bool = True
    energia_final: float = 0.0
    pasto_final: float = 0.0
    tiempo_vida_final: float = 0.0
    observaciones: List[str] = None
    
    def __post_init__(self):
        if self.pasos is None:
            self.pasos = []
        if self.observaciones is None:
            self.observaciones = []
    
    def agregar_paso(self, paso: PasoRuta):
        """Agrega un paso a la ruta"""
        paso.orden = len(self.pasos) + 1
        self.pasos.append(paso)
        self.estrellas_visitadas = len(self.pasos)
    
    def obtener_secuencia_estrellas(self) -> List[str]:
        """Obtiene la secuencia de IDs de estrellas en orden de visita"""
        secuencia = [self.estrella_origen]
        secuencia.extend([paso.estrella_id for paso in self.pasos])
        return secuencia
    
    def calcular_totales(self):
        """Calcula los totales de distancia, tiempo y recursos"""
        self.distancia_total = sum(paso.tiempo_viaje for paso in self.pasos)
        self.tiempo_total = sum(
            paso.tiempo_viaje + paso.tiempo_investigacion + paso.tiempo_alimentacion 
            for paso in self.pasos
        )
        
        # Calcular recursos finales (simplificado, debería ser más complejo)
        total_energia_consumida = sum(paso.energia_consumida for paso in self.pasos)
        total_energia_ganada = sum(paso.energia_ganada for paso in self.pasos)
        total_pasto_consumido = sum(paso.pasto_consumido for paso in self.pasos)
        total_tiempo_vida_cambio = sum(paso.tiempo_vida_cambio for paso in self.pasos)
        
        # Estos cálculos son estimaciones, los valores reales se calculan durante la simulación
        self.energia_final = max(0, 100 - total_energia_consumida + total_energia_ganada)
        self.pasto_final = max(0, 10 - total_pasto_consumido)  # Asumiendo 10kg iniciales
        self.tiempo_vida_final = max(0, 50 - self.distancia_total + total_tiempo_vida_cambio)  # Asumiendo 50 años luz iniciales
    
    def es_factible(self) -> bool:
        """Verifica si la ruta es factible con los recursos estimados"""
        return (self.factible and 
                self.energia_final > 0 and 
                self.tiempo_vida_final > 0)
    
    def agregar_observacion(self, observacion: str):
        """Agrega una observación o advertencia a la ruta"""
        if observacion not in self.observaciones:
            self.observaciones.append(observacion)
    
    def obtener_paso_por_estrella(self, estrella_id: str) -> Optional[PasoRuta]:
        """Obtiene el paso correspondiente a una estrella específica"""
        for paso in self.pasos:
            if paso.estrella_id == estrella_id:
                return paso
        return None
    
    def obtener_resumen(self) -> Dict:
        """Obtiene un resumen de la ruta para mostrar en la UI"""
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'origen': self.estrella_origen,
            'estrellas_visitadas': self.estrellas_visitadas,
            'distancia_total': round(self.distancia_total, 2),
            'tiempo_total': round(self.tiempo_total, 2),
            'factible': self.factible,
            'recursos_finales': {
                'energia': round(self.energia_final, 1),
                'pasto': round(self.pasto_final, 1),
                'tiempo_vida': round(self.tiempo_vida_final, 1)
            },
            'observaciones': self.observaciones
        }
    
    def __str__(self) -> str:
        estado = "Factible" if self.factible else "No factible"
        return f"Ruta {self.id} ({self.tipo.value}) - {self.estrellas_visitadas} estrellas - {estado}"