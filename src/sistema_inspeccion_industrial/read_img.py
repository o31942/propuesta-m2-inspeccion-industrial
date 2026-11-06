"""Módulo de lectura y validación de imágenes industriales de superficies metálicas."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def read_industrial_image(source: str | Path | bytes | np.ndarray) -> np.ndarray:
    """Lee una imagen superficial de acero laminado desde ruta, bytes o matriz.

    Retorna una matriz 2D en escala de grises (uint8, rango [0, 255]).
    """
    if isinstance(source, np.ndarray):
        if source.ndim == 3:
            img = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
        elif source.ndim == 2:
            img = source.copy()
        else:
            raise ValueError(f"Dimensiones no soportadas: {source.shape}")
        return img.astype(np.uint8)

    if isinstance(source, bytes):
        arr = np.frombuffer(source, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("No se pudo decodificar el buffer de imagen.")
        return img

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Archivo de imagen no encontrado: {path}")

    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Formato de imagen inválido o corrupto: {path}")
    return img
