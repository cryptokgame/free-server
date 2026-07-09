# Auditoría de Código Muerto — free-server (FastAPI Proxy para Claude Code)

**Fecha:** 2026-07-09  
**Auditor:** Buffy (Agente de Auditoría de Código Senior)  
**Propósito:** Identificar archivos huérfanos, carpetas desconectadas y basura de desarrollo para su purga segura.

---

## 1. Carpetas y archivos locales a ignorar (`.gitignore`)

El `.gitignore` actual ya cubre la mayoría, pero se detectaron omisiones:

| Elemento | ¿En `.gitignore`? | Acción |
|---|---|---|
| `.venv/` | ✅ Sí | — |
| `env/`, `venv/`, `ENV/` | ✅ Sí | — |
| `__pycache__/` | ✅ Sí | — |
| `*.py[cod]`, `*$py.class`, `*.so` | ✅ Sí | — |
| `.env` (sin `.env.*` excepto `.env.example`) | ✅ Sí | — |
| `.claude/` | ✅ Sí | — |
| `claude_output.txt` | ✅ Sí | — |
| `.vscode/`, `.idea/` | ✅ Sí | — |
| **`*.py.MALO`** / **`*.py.bak`** / **`*.py.orig`** | ❌ No | **[AGREGAR]** — Para evitar que backups (como `errors.py.MALO`) se suban accidentalmente |
| **`*.egg-info/`** | ❌ No | **[AGREGAR]** — Metadatos de empaquetado local |
| **`dist/`** / **`build/`** | ❌ No | **[AGREGAR]** — Artefactos de build |
| **`.mypy_cache/`** / **`.pytest_cache/`** / **`.ruff_cache/`** | ❌ No | **[AGREGAR]** — Cachés de herramientas |

---

## 2. Archivos Huérfanos en `providers/`

### Proveedores registrados en `providers/registry.py` y `config/provider_catalog.py`

Se verificaron las **16 carpetas** de proveedores contra el catálogo y la fábrica de registro:

| Carpeta | ¿Registrado en `PROVIDER_CATALOG`? | ¿Registrado en `PROVIDER_FACTORIES`? | ¿Conectado? |
|---|---|---|---|
| `providers/cerebras/` | ✅ `cerebras` | ✅ `_create_cerebras` | ✅ |
| `providers/codestral/` | ✅ `mistral_codestral` | ✅ `_create_mistral_codestral` | ✅ |
| `providers/deepseek/` | ✅ `deepseek` | ✅ `_create_deepseek` | ✅ |
| `providers/fireworks/` | ✅ `fireworks` | ✅ `_create_fireworks` | ✅ |
| `providers/gemini/` | ✅ `gemini` | ✅ `_create_gemini` | ✅ |
| `providers/groq/` | ✅ `groq` | ✅ `_create_groq` | ✅ |
| `providers/kimi/` | ✅ `kimi` | ✅ `_create_kimi` | ✅ |
| `providers/llamacpp/` | ✅ `llamacpp` | ✅ `_create_llamacpp` | ✅ |
| `providers/lmstudio/` | ✅ `lmstudio` | ✅ `_create_lmstudio` | ✅ |
| `providers/mistral/` | ✅ `mistral` | ✅ `_create_mistral` | ✅ |
| `providers/nvidia_nim/` | ✅ `nvidia_nim` | ✅ `_create_nvidia_nim` | ✅ |
| `providers/ollama/` | ✅ `ollama` | ✅ `_create_ollama` | ✅ |
| `providers/opencode/` | ✅ `opencode` Y `opencode_go` | ✅ `_create_opencode` Y `_create_opencode_go` | ✅ |
| `providers/open_router/` | ✅ `open_router` | ✅ `_create_open_router` | ✅ |
| `providers/wafer/` | ✅ `wafer` | ✅ `_create_wafer` | ✅ |
| `providers/zai/` | ✅ `zai` | ✅ `_create_zai` | ✅ |

**Conclusión:** ✅ **NO hay carpetas huérfanas en `providers/`.** Todos los 16 proveedores están registrados y conectados al ciclo de vida de la aplicación.

---

## 3. Archivos sueltos desconectados

### **[DELETE] `core/anthropic/errors.py.MALO`** — ¡Código muerto confirmado!

- **Qué es:** Un archivo de respaldo (backup) con extensión `.MALO`, probablemente generado durante una sesión de desarrollo previa.
- **Contenido:** Casi idéntico al archivo real `core/anthropic/errors.py`, pero con una diferencia: la línea `return f"Invalid request sent to provider: {e.message if hasattr(e, 'message') else str(e)}"` (más verbosa) en la versión `.MALO`, mientras que la versión real dice simplemente `return "Invalid request sent to provider."`.
- **Archivo real activo:** `core/anthropic/errors.py` — se importa desde `api/dependencies.py`, `api/services.py`, `messaging/handler.py`, `messaging/trees/queue_manager.py`, `messaging/platforms/discord.py`, `messaging/platforms/telegram.py`, `providers/error_mapping.py`, y `core/anthropic/__init__.py`.
- **Tamaño:** ~1.9 KB
- **Acción:** **[DELETE]** — Eliminar `core/anthropic/errors.py.MALO`. No es referenciado por ningún archivo.

### No hay tests

- No existe carpeta `tests/` en el repositorio, a pesar de que `pyproject.toml` referencia `testpaths = ["tests"]` y configura `pytest`. Esto es **normal** para la rama actual; simplemente no se han creado tests aún. No es código muerto, es una funcionalidad no implementada.

---

## 4. Instrucciones para Git (rebase y limpieza)

### Paso 1: Verificar el estado actual

```bash
git status
```

### Paso 2: Agregar entradas faltantes a `.gitignore`

Añade estas líneas al final de tu `.gitignore` actual:

```gitignore
# Backups de desarrollo
*.py.MALO
*.py.bak
*.py.orig

# Metadatos de paquete
*.egg-info/
dist/
build/

# Cachés de herramientas
.mypy_cache/
.pytest_cache/
.ruff_cache/
```

### Paso 3: Eliminar el archivo muerto

```bash
git rm core/anthropic/errors.py.MALO
```

### Paso 4: Eliminar carpets `__pycache__` que hayan sido trackeadas (si las hay)

```bash
# Verificar si hay __pycache__ trackeado
git ls-files --cached | findstr "__pycache__"

# Si hay resultados, eliminarlos del índice
git ls-files --cached | findstr "__pycache__" | xargs git rm --cached -r
```

### Paso 5: Commit de la limpieza

```bash
git add .
git commit -m "chore: remove dead code (errors.py.MALO) and update .gitignore
```
