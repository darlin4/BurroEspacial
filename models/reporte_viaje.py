"""
Modelo de datos para representar el Reporte de Viaje.
Contiene toda la información sobre el viaje realizado por el burro.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from .burro import EstadoSalud

@dataclass
class VisitaEstrella:
    """
    Representa la visita a una estrella individual.
    
    Attributes:
        estrella_id: ID de la estrella visitada
        nombre_estrella: Nombre de la estrella
        orden_visita: Orden en que fue visitada
        tiempo_llegada: Tiempo de llegada a la estrella
        tiempo_salida: Tiempo de salida de la estrella
        tiempo_investigacion: Tiempo dedicado a investigación
        tiempo_alimentacion: Tiempo dedicado a comer
        pasto_consumido: Cantidad de pasto consumido en kg
        energia_antes: Energía del burro al llegar
        energia_despues: Energía del burro al salir
        salud_antes: Estado de salud al llegar
        salud_despues: Estado de salud al salir
        tiempo_vida_antes: Tiempo de vida al llegar
        tiempo_vida_despues: Tiempo de vida al salir
        cambios_salud: Descripción de cambios en la salud
        experimentos_realizados: Lista de experimentos o investigaciones
    """
    
    estrella_id: str
    nombre_estrella: str
    orden_visita: int
    tiempo_llegada: float
    tiempo_salida: float
    tiempo_investigacion: float = 0.0
    tiempo_alimentacion: float = 0.0
    pasto_consumido: float = 0.0
    energia_antes: float = 0.0
    energia_despues: float = 0.0
    salud_antes: EstadoSalud = EstadoSalud.EXCELENTE
    salud_despues: EstadoSalud = EstadoSalud.EXCELENTE
    tiempo_vida_antes: float = 0.0
    tiempo_vida_despues: float = 0.0
    cambios_salud: str = ""
    experimentos_realizados: List[str] = None
    
    def __post_init__(self):
        if self.experimentos_realizados is None:
            self.experimentos_realizados = []
    
    def duracion_visita(self) -> float:
        """Calcula la duración total de la visita"""
        return self.tiempo_salida - self.tiempo_llegada
    
    def cambio_energia(self) -> float:
        """Calcula el cambio neto en energía"""
        return self.energia_despues - self.energia_antes
    
    def cambio_tiempo_vida(self) -> float:
        """Calcula el cambio neto en tiempo de vida"""
        return self.tiempo_vida_despues - self.tiempo_vida_antes

@dataclass
class ViajeGalaxia:
    """
    Representa un viaje intergaláctico realizado.
    
    Attributes:
        galaxia_origen: ID de la galaxia de origen
        galaxia_destino: ID de la galaxia de destino
        estrella_hipergigante: ID de la estrella hipergigante utilizada
        tiempo_viaje: Tiempo del viaje intergaláctico
        energia_antes: Energía antes del viaje
        energia_despues: Energía después del viaje (con recarga del 50%)
        pasto_antes: Pasto antes del viaje
        pasto_despues: Pasto después del viaje (duplicado)
    """
    
    galaxia_origen: str
    galaxia_destino: str
    estrella_hipergigante: str
    tiempo_viaje: float
    energia_antes: float
    energia_despues: float
    pasto_antes: float
    pasto_despues: float

@dataclass
class ReporteViaje:
    """
    Reporte completo del viaje espacial del burro.
    
    Attributes:
        id: Identificador único del reporte
        fecha_inicio: Fecha y hora de inicio del viaje
        fecha_fin: Fecha y hora de finalización del viaje
        burro_nombre: Nombre del burro
        ruta_utilizada: ID de la ruta utilizada
        estado_inicial: Estado inicial del burro
        estado_final: Estado final del burro
        visitas_estrellas: Lista de visitas a estrellas
        viajes_intergalacticos: Lista de viajes entre galaxias
        total_estrellas_visitadas: Número total de estrellas visitadas
        total_galaxias_visitadas: Número total de galaxias visitadas
        duracion_total: Duración total del viaje
        distancia_total: Distancia total recorrida
        pasto_total_consumido: Cantidad total de pasto consumido
        tiempo_total_investigacion: Tiempo total dedicado a investigación
        viaje_exitoso: Indica si el viaje se completó exitosamente
        causa_finalizacion: Razón por la que terminó el viaje
        observaciones: Observaciones adicionales del viaje
    """
    
    id: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    burro_nombre: str = ""
    ruta_utilizada: str = ""
    estado_inicial: Dict = None
    estado_final: Dict = None
    visitas_estrellas: List[VisitaEstrella] = None
    viajes_intergalacticos: List[ViajeGalaxia] = None
    total_estrellas_visitadas: int = 0
    total_galaxias_visitadas: int = 1
    duracion_total: float = 0.0
    distancia_total: float = 0.0
    pasto_total_consumido: float = 0.0
    tiempo_total_investigacion: float = 0.0
    viaje_exitoso: bool = False
    causa_finalizacion: str = ""
    observaciones: List[str] = None
    
    def __post_init__(self):
        if self.estado_inicial is None:
            self.estado_inicial = {}
        if self.estado_final is None:
            self.estado_final = {}
        if self.visitas_estrellas is None:
            self.visitas_estrellas = []
        if self.viajes_intergalacticos is None:
            self.viajes_intergalacticos = []
        if self.observaciones is None:
            self.observaciones = []
    
    def agregar_visita_estrella(self, visita: VisitaEstrella):
        """Agrega una visita a estrella al reporte"""
        self.visitas_estrellas.append(visita)
        self.total_estrellas_visitadas = len(self.visitas_estrellas)
        
        # Actualizar totales
        self.pasto_total_consumido += visita.pasto_consumido
        self.tiempo_total_investigacion += visita.tiempo_investigacion
    
    def agregar_viaje_intergalactico(self, viaje: ViajeGalaxia):
        """Agrega un viaje intergaláctico al reporte"""
        self.viajes_intergalacticos.append(viaje)
        
        # Actualizar contadores
        galaxias_visitadas = set()
        galaxias_visitadas.add(viaje.galaxia_origen)
        galaxias_visitadas.add(viaje.galaxia_destino)
        for v in self.viajes_intergalacticos:
            galaxias_visitadas.add(v.galaxia_origen)
            galaxias_visitadas.add(v.galaxia_destino)
        
        self.total_galaxias_visitadas = len(galaxias_visitadas)
    
    def finalizar_viaje(self, exitoso: bool, causa: str, estado_final: Dict):
        """Finaliza el reporte de viaje"""
        self.fecha_fin = datetime.now()
        self.viaje_exitoso = exitoso
        self.causa_finalizacion = causa
        self.estado_final = estado_final
        
        # Calcular duración total
        if self.fecha_inicio and self.fecha_fin:
            self.duracion_total = (self.fecha_fin - self.fecha_inicio).total_seconds() / 3600  # en horas
    
    def calcular_estadisticas(self):
        """Calcula estadísticas adicionales del viaje"""
        if self.visitas_estrellas:
            # Calcular distancia total (aproximada)
            for i in range(len(self.visitas_estrellas) - 1):
                # Aquí se podría calcular la distancia real entre estrellas
                pass
    
    def obtener_resumen_ejecutivo(self) -> Dict:
        """Obtiene un resumen ejecutivo del viaje"""
        return {
            'id_reporte': self.id,
            'burro': self.burro_nombre,
            'fecha_inicio': self.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_inicio else "",
            'fecha_fin': self.fecha_fin.strftime("%Y-%m-%d %H:%M:%S") if self.fecha_fin else "",
            'duracion_horas': round(self.duracion_total, 2),
            'estrellas_visitadas': self.total_estrellas_visitadas,
            'galaxias_visitadas': self.total_galaxias_visitadas,
            'viajes_intergalacticos': len(self.viajes_intergalacticos),
            'pasto_consumido_kg': round(self.pasto_total_consumido, 2),
            'tiempo_investigacion_total': round(self.tiempo_total_investigacion, 2),
            'viaje_exitoso': self.viaje_exitoso,
            'causa_finalizacion': self.causa_finalizacion,
            'estado_final_burro': self.estado_final
        }
    
    def obtener_detalle_visitas(self) -> List[Dict]:
        """Obtiene el detalle de todas las visitas a estrellas"""
        detalles = []
        for visita in self.visitas_estrellas:
            detalles.append({
                'orden': visita.orden_visita,
                'estrella': visita.nombre_estrella,
                'tiempo_llegada': round(visita.tiempo_llegada, 2),
                'duracion_visita': round(visita.duracion_visita(), 2),
                'investigacion': round(visita.tiempo_investigacion, 2),
                'alimentacion': round(visita.tiempo_alimentacion, 2),
                'pasto_consumido': round(visita.pasto_consumido, 2),
                'cambio_energia': round(visita.cambio_energia(), 2),
                'cambio_tiempo_vida': round(visita.cambio_tiempo_vida(), 2),
                'salud_final': visita.salud_despues.name,
                'experimentos': visita.experimentos_realizados
            })
        return detalles
    
    def agregar_observacion(self, observacion: str):
        """Agrega una observación al reporte"""
        if observacion not in self.observaciones:
            self.observaciones.append(observacion)
    
    def __str__(self) -> str:
        estado = "Exitoso" if self.viaje_exitoso else "Fallido"
        return f"Reporte {self.id} - Burro: {self.burro_nombre} - {self.total_estrellas_visitadas} estrellas - {estado}"