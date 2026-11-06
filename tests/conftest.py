"""Fixtures sintéticos para pruebas unitarias de inspección industrial (NEU-DET)."""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture
def synthetic_steel_surface() -> np.ndarray:
    """Genera una imagen sintética 200x200 de lámina de acero con defecto simulado."""
    rng = np.random.default_rng(42)
    img = rng.integers(90, 140, size=(200, 200), dtype=np.uint8)
    # Simular rayadura de alto contraste (Scratch)
    img[60:140, 95:105] = 245
    return img
