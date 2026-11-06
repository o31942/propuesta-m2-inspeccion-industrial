# Propuesta Formal M2 — Sistema de Inspección de Calidad Industrial (NEU-DET + YOLOv8 / RT-DETR)

Repositorio industrial y generador documental para el **Acto III: Formulación Formal de la Propuesta de Proyecto** de la asignatura **Gestión de Proyectos en IA y Ciencia de Datos** — *Maestría en Inteligencia Artificial y Ciencia de Datos*, **Universidad Autónoma de Occidente (UAO)** (Docente: Prof. Jan Polanco Velasco).

---

## 1. Documentos Generados (Entregables Oficiales del Acto III)

En el directorio [`docs/`](./docs/) se encuentran los artefactos formales listos para radicación:

- **`docs/Propuesta_Formal_M2_Inspeccion_Industrial_UAO.pdf`**: Documento PDF formal diagramado bajo las especificaciones exactas del Acto III (márgenes de 2.5 cm, tipografía Arial, títulos H1 14 pt negrita, subtítulos H2/H3 12 pt negrita, cuerpo 12 pt, interlineado 1.5, extensión $\le 15$ páginas de contenido excluyendo portada e índice, portada institucional con los 7 elementos obligatorios y los 6 capítulos completos).
- **`docs/Propuesta_Formal_M2_Inspeccion_Industrial_UAO.docx`**: Versión editable en Microsoft Word con el mismo formato editorial.
- **`docs/Propuesta_Formal_M2_Inspeccion_Industrial_UAO.md`**: Versión estructurada en Markdown.
- **`docs/gantt_cpm_15_dias.png`**: Diagrama de Gantt a 15 días calendario con las 3 fases universales (Preparación, Desarrollo & Refactoring, Implementación & Despliegue) y la Ruta Crítica (CPM, Holgura = 0) resaltada en rojo.

### ¿Cómo personalizar los nombres y códigos de los integrantes en la Portada?
Edita el diccionario `PROJECT_INFO["integrantes"]` al inicio de [`generar_propuesta_m2.py`](./generar_propuesta_m2.py) (líneas 47–52) y ejecuta:

```powershell
uv run python generar_propuesta_m2.py
```

---

## 2. Arquitectura Industrial del Paquete (`src/` layout)

El repositorio implementa la estructura desacoplada exigida en los Actos II y III:

```text
propuesta-m2-inspeccion-industrial/
├── pyproject.toml                       # Manifiesto moderno PEP 621 + configuración Ruff y Pytest
├── uv.lock                              # Lockfile determinista de dependencias (Astral uv)
├── .pre-commit-config.yaml              # Guardia automática de commits (ruff check + ruff format)
├── Dockerfile                           # Contenedor CPU reproducible con libgl1 y libglib2.0-0
├── generar_propuesta_m2.py              # Generador del PDF, DOCX, Markdown y Gantt CPM a 15 días
├── docs/                                # Documentos formales generados (PDF, DOCX, MD, PNG)
├── src/
│   └── sistema_inspeccion_industrial/
│       ├── __init__.py                  # Exportación limpia de la API del paquete
│       ├── read_img.py                  # Ingesta de imágenes industriales en escala de grises
│       ├── preprocess_img.py            # Filtro CLAHE (clipLimit=2.0) + contrato float32 [0.0, 1.0]
│       ├── load_model.py                # Detector multiclase NEU-DET (6 clases) + Eigen-CAM
│       └── integrator.py                # Orquestador desacoplado de extremo a extremo
└── tests/
    ├── conftest.py                      # Fixture sintético determinista (synthetic_steel_surface)
    └── test_preprocess.py               # Suite unitaria bajo patrón AAA (Arrange, Act, Assert)
```

---

## 3. Comandos de Verificación Industrial (`uv`, `pytest`, `ruff`)

```powershell
# 1. Ejecutar suite de pruebas unitarias (Patrón AAA)
uv run pytest -v

# 2. Ejecutar linter y verificador de formato (Ruff)
uv run ruff check
uv run ruff format --check

# 3. Empaquetar artefacto distribuible Wheel (.whl)
uv build
```
