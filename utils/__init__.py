"""Módulo de utilidades y helpers para el sistema.

This initializer is intentionally defensive: helper modules may be
lightweight stubs in this workspace. We try to import algorithm
implementations but never raise on missing optional helpers — instead
we expose None so callers can handle absence gracefully.
"""

# Pathfinding: prefer a class or function exported by the module. We
# don't import any heavy helpers here to avoid cascading ImportErrors.
try:
    # some code expects a class named Pathfinding
    from .algorithms.pathfinding import Pathfinding  # type: ignore
except Exception:
    try:
        # fallback: expose the function under the Pathfinding name
        from .algorithms.pathfinding import propose_route as Pathfinding  # type: ignore
    except Exception:
        Pathfinding = None

try:
    from .algorithms.optimization import OptimizadorRutas  # type: ignore
except Exception:
    OptimizadorRutas = None

# Helper utilities: import if present, otherwise keep None.
try:
    from .helpers.file_helper import FileHelper  # type: ignore
except Exception:
    FileHelper = None

try:
    from .helpers.math_helper import MathHelper  # type: ignore
except Exception:
    MathHelper = None

try:
    from .helpers.sound_helper import SoundHelper  # type: ignore
except Exception:
    SoundHelper = None

__all__ = [
    'Pathfinding',
    'OptimizadorRutas',
    'FileHelper',
    'MathHelper',
    'SoundHelper',
]