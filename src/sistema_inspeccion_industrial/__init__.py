"""Paquete principal del Sistema de Inspección de Calidad Industrial (NEU-DET).

Estructura profesional bajo src/ layout cumpliendo los estándares de ingeniería de IA (M2).
"""

from sistema_inspeccion_industrial.integrator import (
    DefectDetectionItem,
    IndustrialInspectionPipeline,
    InspectionResult,
)
from sistema_inspeccion_industrial.load_model import NEU_CLASSES, SurfaceDefectDetector
from sistema_inspeccion_industrial.preprocess_img import (
    preprocess_image,
    validate_preprocessed_contract,
)
from sistema_inspeccion_industrial.read_img import read_industrial_image

__all__ = [
    "NEU_CLASSES",
    "DefectDetectionItem",
    "IndustrialInspectionPipeline",
    "InspectionResult",
    "SurfaceDefectDetector",
    "preprocess_image",
    "read_industrial_image",
    "validate_preprocessed_contract",
]
__version__ = "0.1.0"
