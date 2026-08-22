"""MAF Release 1.1 — Mechanism–Artifact Factorization."""
from .model import MAFModel
from .worlds import generate_world

__version__ = "1.1.1"
__all__ = ["MAFModel", "generate_world"]
