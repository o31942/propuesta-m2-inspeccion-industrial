## Descripción del Pull Request
- **Ticket / Historia de Usuario asociada:** `#00X`
- **Etiqueta oficial:** `[ ] ML` `[ ] Backend` `[ ] Frontend` `[ ] Testing`
- **Story Points (Fibonacci 1:1):** `___ SP`

## Criterios de Aceptación Verificados
- [ ] **AC1:** Verificado localmente.
- [ ] **AC2:** Contratos numéricos / tipado estático validados.
- [ ] **AC3:** Pruebas unitarias en `tests/` pasando en verde.

## Checklist de Guardia Industrial (Acto II & III)
- [ ] `uv run ruff check` retorna **0 errores**.
- [ ] `uv run ruff format --check` retorna **0 cambios pendientes**.
- [ ] `uv run pytest -v` aprueba al **100%**.
- [ ] Ningún archivo de pesos (`.pt`, `.onnx`, `.safetensors`) ni dataset crudo (`> 10 MB`) fue incluido en el commit.
