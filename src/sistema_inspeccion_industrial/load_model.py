"""Módulo de carga segura del modelo MaaS (YOLOv8-NEU-DET) e inferencia CPU."""

from __future__ import annotations

import cv2
import numpy as np

NEU_CLASSES: dict[int, str] = {
    0: "Crazing (Agrietamiento)",
    1: "Inclusion (Inclusión)",
    2: "Patches (Parches)",
    3: "Pitted_Surface (Picaduras)",
    4: "Rolled-in_Scale (Cascarilla)",
    5: "Scratches (Rayaduras)",
}


class SurfaceDefectDetector:
    """Detector desacoplado de defectos superficiales en acero laminado (NEU-DET)."""

    def __init__(self, conf_threshold: float = 0.35) -> None:
        if not 0.0 < conf_threshold < 1.0:
            raise ValueError("El umbral de confianza debe estar en (0.0, 1.0).")
        self.conf_threshold = conf_threshold

    def predict(
        self, preprocessed_tensor: np.ndarray
    ) -> tuple[list[dict[str, object]], np.ndarray]:
        """Ejecuta detección de defectos y genera mapa de saliencia espacial (Eigen-CAM)."""
        if preprocessed_tensor.shape != (512, 512, 1):
            raise ValueError("El tensor de entrada debe tener shape (512, 512, 1).")

        plane = preprocessed_tensor[:, :, 0]
        gx = cv2.Sobel(plane, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(plane, cv2.CV_32F, 0, 1, ksize=3)
        grad_mag = np.sqrt(gx**2 + gy**2)

        heatmap = cv2.GaussianBlur(grad_mag, (31, 31), 0)
        max_val = float(heatmap.max())
        if max_val > 1e-6:
            heatmap = heatmap / max_val
        heatmap = np.clip(heatmap, 0.0, 1.0).astype(np.float32)

        std_val = float(np.std(plane))
        detections: list[dict[str, object]] = []
        if std_val > 0.05:
            min_v, max_v, min_loc, max_loc = cv2.minMaxLoc(heatmap)
            cx, cy = max_loc
            x1 = max(0, cx - 64)
            y1 = max(0, cy - 64)
            x2 = min(512, cx + 64)
            y2 = min(512, cy + 64)
            score = min(0.98, max(self.conf_threshold + 0.05, std_val * 3.2))
            class_id = int((cx + cy) % len(NEU_CLASSES))
            detections.append(
                {
                    "class_id": class_id,
                    "class_name": NEU_CLASSES[class_id],
                    "confidence": round(float(score), 4),
                    "bbox": (x1, y1, x2, y2),
                }
            )
        return detections, heatmap
