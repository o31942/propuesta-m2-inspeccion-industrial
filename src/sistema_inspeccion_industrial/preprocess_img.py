"""Módulo de preprocesamiento CLAHE, normalización y verificación de contratos."""

from __future__ import annotations

import cv2
import numpy as np


def validate_preprocessed_contract(
    tensor: np.ndarray,
    expected_shape: tuple[int, int, int] = (512, 512, 1),
) -> None:
    """Valida formalmente el contrato matemático del tensor preprocesado."""
    if not isinstance(tensor, np.ndarray):
        raise TypeError("El tensor debe ser una instancia de np.ndarray.")
    if tensor.dtype != np.float32:
        raise ValueError(f"Tipo de dato inválido: {tensor.dtype}, esperado float32.")
    if tensor.shape != expected_shape:
        raise ValueError(
            f"Invarianza dimensional violada: {tensor.shape} != {expected_shape}."
        )
    if not np.all(np.isfinite(tensor)):
        raise ValueError("El tensor contiene valores NaN o Infinitos.")
    if float(tensor.min()) < 0.0 or float(tensor.max()) > 1.0:
        raise ValueError("El rango de valores excede el intervalo [0.0, 1.0].")


def preprocess_image(
    raw_img: np.ndarray,
    target_size: int = 512,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
) -> np.ndarray:
    """Aplica CLAHE, redimensionamiento a (512, 512, 1) y normalización [0.0, 1.0]."""
    if raw_img is None or raw_img.size == 0:
        raise ValueError("La imagen de entrada está vacía.")

    if raw_img.ndim == 3:
        gray = cv2.cvtColor(raw_img, cv2.COLOR_BGR2GRAY)
    elif raw_img.ndim == 2:
        gray = raw_img.copy()
    else:
        raise ValueError(f"Dimensiones no soportadas: {raw_img.shape}")

    gray_u8 = gray.astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(gray_u8)

    resized = cv2.resize(
        enhanced, (target_size, target_size), interpolation=cv2.INTER_LINEAR
    )
    normalized = resized.astype(np.float32) / 255.0
    tensor = np.expand_dims(normalized, axis=-1)

    validate_preprocessed_contract(tensor, expected_shape=(target_size, target_size, 1))
    return tensor
