"""
Modelo de datos para representar el Burro espacial en el sistema.
El burro tiene estado de salud, energía, edad, y otras propiedades vitales.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EstadoSalud(Enum):
    """Estados de salud posibles del burro"""
    MUERTO = 0
    MORIBUNDO = 1
    MALO = 2
    BUENO = 3
    EXCELENTE = 4

@dataclass
class Burro:
    """
    Representa el burro espacial que realiza el viaje.
    
    Attributes:
        nombre: Nombre del burro
        estado_salud: Estado actual de salud del burro
        edad: Edad del burro en años
        burroenergía: Porcentaje de energía actual (0-100)
        pasto_bodega: Cantidad de pasto disponible en kg
        tiempo_vida: Tiempo de vida restante en años luz
        estrella_actual: ID de la estrella donde se encuentra actualmente
        vivo: Indica si el burro está vivo
    """
    
    nombre: str = "Burrito Espacial"
    estado_salud: EstadoSalud = EstadoSalud.EXCELENTE
    edad: float = 5.0  # años
    burroenergia: float = 100.0  # porcentaje 0-100
    pasto_bodega: float = 10.0  # kg
    tiempo_vida: float = 50.0  # años luz
    estrella_actual: Optional[str] = None
    vivo: bool = True
    
    def esta_vivo(self) -> bool:
        """Verifica si el burro está vivo"""
        return self.vivo and self.tiempo_vida > 0 and self.estado_salud != EstadoSalud.MUERTO
    
    def necesita_pasto(self) -> bool:
        """Verifica si el burro necesita comer pasto (energía < 50%)"""
        return self.burroenergia < 50.0
    
    def puede_comer(self) -> bool:
        """Verifica si el burro puede comer (tiene pasto disponible)"""
        return self.pasto_bodega > 0
    
    def comer_pasto(self, cantidad_kg: float) -> float:
        """
        El burro come pasto y recupera energía.
        
        Args:
            cantidad_kg: Cantidad de pasto a consumir en kg
            
        Returns:
            Cantidad real de pasto consumido
        """
        if not self.puede_comer():
            return 0.0
            
        cantidad_real = min(cantidad_kg, self.pasto_bodega)
        self.pasto_bodega -= cantidad_real
        
        # Calcular energía recuperada según estado de salud
        energia_por_kg = self._obtener_eficiencia_pasto()
        energia_recuperada = cantidad_real * energia_por_kg
        
        self.burroenergia = min(100.0, self.burroenergia + energia_recuperada)
        
        return cantidad_real
    
    def _obtener_eficiencia_pasto(self) -> float:
        """Obtiene la eficiencia de conversión de pasto a energía según el estado de salud"""
        eficiencias = {
            EstadoSalud.EXCELENTE: 5.0,
            EstadoSalud.BUENO: 3.0,
            EstadoSalud.MALO: 2.0,
            EstadoSalud.MORIBUNDO: 1.0,
            EstadoSalud.MUERTO: 0.0
        }
        return eficiencias.get(self.estado_salud, 0.0)
    
    def consumir_energia(self, cantidad: float):
        """Consume energía del burro"""
        self.burroenergia = max(0.0, self.burroenergia - cantidad)
        
        # Si se queda sin energía, puede afectar la salud
        if self.burroenergia <= 0:
            self._reducir_salud()
    
    def consumir_tiempo_vida(self, tiempo: float):
        """Consume tiempo de vida del burro"""
        self.tiempo_vida = max(0.0, self.tiempo_vida - tiempo)
        
        if self.tiempo_vida <= 0:
            self.morir()
    
    def ganar_tiempo_vida(self, tiempo: float):
        """Agrega tiempo de vida al burro"""
        self.tiempo_vida += tiempo
    
    def cambiar_salud(self, cambio: int):
        """
        Cambia el estado de salud del burro.
        
        Args:
            cambio: Cambio en el nivel de salud (-2, -1, 0, +1, +2)
        """
        nivel_actual = self.estado_salud.value
        nuevo_nivel = max(0, min(4, nivel_actual + cambio))
        self.estado_salud = EstadoSalud(nuevo_nivel)
        
        if self.estado_salud == EstadoSalud.MUERTO:
            self.morir()
    
    def _reducir_salud(self):
        """Reduce el estado de salud del burro en un nivel"""
        self.cambiar_salud(-1)
    
    def morir(self):
        """Mata al burro"""
        self.vivo = False
        self.estado_salud = EstadoSalud.MUERTO
        self.tiempo_vida = 0.0
        self.burroenergia = 0.0
    
    def recargar_hipergigante(self):
        """Recarga del 50% de energía y duplica pasto (beneficio de estrella hipergigante)"""
        self.burroenergia = min(100.0, self.burroenergia + (self.burroenergia * 0.5))
        self.pasto_bodega *= 2
    
    def mover_a_estrella(self, estrella_id: str):
        """Mueve el burro a una nueva estrella"""
        self.estrella_actual = estrella_id
    
    def obtener_estado_porcentual(self) -> dict:
        """Obtiene el estado del burro en formato de porcentajes para la UI"""
        return {
            'energia': self.burroenergia,
            'salud': (self.estado_salud.value / 4) * 100,
            'tiempo_vida': max(0, self.tiempo_vida),
            'pasto': self.pasto_bodega
        }
    
    def __str__(self) -> str:
        estado = f"{self.nombre} - Salud: {self.estado_salud.name}, Energía: {self.burroenergia:.1f}%"
        estado += f", Pasto: {self.pasto_bodega:.1f}kg, Vida: {self.tiempo_vida:.1f} años luz"
        return estado