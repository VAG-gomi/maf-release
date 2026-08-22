"""MAF Release 1.0 — Mechanism–Artifact Factorization."""
from .model import MAFModel
from .worlds import generate_world

__version__ = "1.0.0"
__all__ = ["MAFModel", "generate_world"]
