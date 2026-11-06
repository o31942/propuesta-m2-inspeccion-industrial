"""Pruebas unitarias AAA para preprocesamiento, contrato e inferencia (NEU-DET)."""

from __future__ import annotations

import numpy as np
import pytest

from sistema_inspeccion_industrial.integrator import IndustrialInspectionPipeline
from sistema_inspeccion_industrial.preprocess_img import (
    preprocess_image,
    validate_preprocessed_contract,
)
from sistema_inspeccion_industrial.read_img import read_industrial_image


def test_preprocess_shape_and_range(synthetic_steel_surface: np.ndarray) -> None:
    # Arrange & Act
    tensor = preprocess_image(synthetic_steel_surface, target_size=512, clip_limit=2.0)

    # Assert
    assert isinstance(tensor, np.ndarray)
    assert tensor.dtype == np.float32
    assert tensor.shape == (512, 512, 1)
    assert float(tensor.min()) >= 0.0
    assert float(tensor.max()) <= 1.0
    assert np.all(np.isfinite(tensor))


def test_contract_rejects_nan() -> None:
    # Arrange
    bad_tensor = np.zeros((512, 512, 1), dtype=np.float32)
    bad_tensor[10, 10, 0] = np.nan

    # Act & Assert
    with pytest.raises(ValueError, match="NaN"):
        validate_preprocessed_contract(bad_tensor)


def test_end_to_end_pipeline_latency_and_output(
    synthetic_steel_surface: np.ndarray,
) -> None:
    # Arrange
    pipeline = IndustrialInspectionPipeline(conf_threshold=0.35)

    # Act
    result = pipeline.run(synthetic_steel_surface)

    # Assert
    assert result.is_defective is True
    assert result.latency_ms < 250.0
    assert result.overlay_rgb.shape == (512, 512, 3)
    assert len(result.detections) >= 1


def test_read_image_from_ndarray(synthetic_steel_surface: np.ndarray) -> None:
    # Arrange & Act
    out = read_industrial_image(synthetic_steel_surface)

    # Assert
    assert out.shape == (200, 200)
    assert out.dtype == np.uint8
