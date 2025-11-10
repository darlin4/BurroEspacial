"""Helper para operaciones matemáticas.

Implementación mínima: distancia euclidiana y utilidades pequeñas que
son útiles en el resto del proyecto.
"""

import math
from typing import Tuple


class MathHelper:
	@staticmethod
	def euclidean_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
		"""Distancia euclidiana entre dos puntos (x,y)."""
		return math.hypot(a[0] - b[0], a[1] - b[1])

	@staticmethod
	def clamp(value: float, minv: float, maxv: float) -> float:
		if value < minv:
			return minv
		if value > maxv:
			return maxv
		return value