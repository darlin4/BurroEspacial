"""Helper para operaciones de archivos.

Se añade una implementación mínima para que otras partes del proyecto
puedan usar funciones básicas de lectura/escritura JSON sin causar
errores de importación. Es intencionalmente pequeña y fácil de
extender.
"""

from pathlib import Path
import json
from typing import Any, Optional


class FileHelper:
	"""Utility para lectura y escritura de archivos JSON.

	Métodos:
	- read_json(path) -> dict
	- write_json(path, obj) -> None
	"""

	@staticmethod
	def read_json(path: str) -> Optional[Any]:
		p = Path(path)
		if not p.exists():
			return None
		try:
			with p.open('r', encoding='utf-8') as fh:
				return json.load(fh)
		except Exception:
			return None

	@staticmethod
	def write_json(path: str, obj: Any) -> bool:
		p = Path(path)
		try:
			p.parent.mkdir(parents=True, exist_ok=True)
			with p.open('w', encoding='utf-8') as fh:
				json.dump(obj, fh, ensure_ascii=False, indent=2)
			return True
		except Exception:
			return False