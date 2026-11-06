"""Orquestador desacoplado del pipeline de inspección industrial (MVC / MaaS)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from sistema_inspeccion_industrial.load_model import SurfaceDefectDetector
from sistema_inspeccion_industrial.preprocess_img import preprocess_image
from sistema_inspeccion_industrial.read_img import read_industrial_image


@dataclass
class DefectDetectionItem:
    """Representa un defecto superficial detectado en la lámina de acero."""

    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]


@dataclass
class InspectionResult:
    """Contrato de salida del pipeline de inspección industrial."""

    is_defective: bool
    primary_defect: str
    max_confidence: float
    latency_ms: float
    detections: list[DefectDetectionItem]
    raw_image: np.ndarray
    preprocessed_tensor: np.ndarray
    heatmap: np.ndarray
    overlay_rgb: np.ndarray


class IndustrialInspectionPipeline:
    """Pipeline end-to-end para inspección de defectos superficiales NEU-DET."""

    def __init__(self, conf_threshold: float = 0.35) -> None:
        self.detector = SurfaceDefectDetector(conf_threshold=conf_threshold)

    def run(self, source: str | Path | bytes | np.ndarray) -> InspectionResult:
        t0 = time.perf_counter()
        raw = read_industrial_image(source)
        tensor = preprocess_image(raw, target_size=512, clip_limit=2.0)
        raw_dets, heatmap = self.detector.predict(tensor)

        base_u8 = (tensor[:, :, 0] * 255.0).astype(np.uint8)
        base_bgr = cv2.cvtColor(base_u8, cv2.COLOR_GRAY2BGR)
        heat_u8 = (heatmap * 255.0).astype(np.uint8)
        color_map = cv2.applyColorMap(heat_u8, cv2.COLORMAP_JET)
        blended = cv2.addWeighted(base_bgr, 0.65, color_map, 0.35, 0)

        items: list[DefectDetectionItem] = []
        for d in raw_dets:
            bbox = tuple(int(v) for v in d["bbox"])  # type: ignore[arg-type]
            item = DefectDetectionItem(
                class_id=int(d["class_id"]),  # type: ignore[arg-type]
                class_name=str(d["class_name"]),
                confidence=float(d["confidence"]),  # type: ignore[arg-type]
                bbox=bbox,  # type: ignore[arg-type]
            )
            items.append(item)
            x1, y1, x2, y2 = bbox
            cv2.rectangle(blended, (x1, y1), (x2, y2), (0, 255, 0), 2)

        overlay_rgb = cv2.cvtColor(blended, cv2.COLOR_BGR2RGB)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        is_def = len(items) > 0
        primary = (
            items[0].class_name if is_def else "Superficie Conforme (Sin Defectos)"
        )
        max_conf = max((it.confidence for it in items), default=0.0)

        return InspectionResult(
            is_defective=is_def,
            primary_defect=primary,
            max_confidence=max_conf,
            latency_ms=round(elapsed_ms, 2),
            detections=items,
            raw_image=raw,
            preprocessed_tensor=tensor,
            heatmap=heatmap,
            overlay_rgb=overlay_rgb,
        )
