# Auditoría: Relación entre `free-claude-code-analysis`, `free-server` y el comando `fcc-server`

**Fecha:** Julio 2026
**Modo:** Solo lectura — no se modificó ningún archivo

---

## 1. ¿Qué es el comando `fcc-server`?

El comando `fcc-server` está definido como **entry point** en el `pyproject.toml` de **ambos repositorios**:

```toml
[project.scripts]
fcc-server = "cli.entrypoints:serve"
```

Esto significa que **ambos repos** compiten por el mismo nombre de comando. Quien se instale último (o quien tenga prioridad en el `PATH`) gana.

### Ubicaciones del ejecutable en el sistema

Se encontraron **3 copias** del ejecutable `fcc-server.exe`:

| Ruta | Tipo |
|------|------|
| `C:\Users\Katherine\AppData\Local\hermes\hermes-agent\venv\Scripts\fcc-server.exe` | Virtual env de Hermes |
| `C:\Users\Katherine\AppData\Local\Programs\Python\Python311\Scripts\fcc-server.exe` | Python global |
| `C:\Users\Katherine\.local\bin\fcc-server.exe` | Local user bin |

No se encontró ningún paquete pip instalado con el nombre `fcc-server`, lo que sugiere que fue instalado mediante `uv` o `pip install -e .` (editable) desde alguno de los dos repos.

---

## 2. Mapeo de repositorios

### Repo A: `D:\Agente\REPOS\free-server` (actual)

- **Nombre del paquete:** `free-claude-code` v1.2.41
- **Estado:** Activo, con modificaciones sin commit
- **Contiene:** Código fuente completo del proxy
- **Entry points:** `fcc-server`, `fcc-init`, `fcc-claude`, `free-claude-code`
- **Particularidades:**
  - Hardcodea listas de modelos en `list_model_ids()` (varios providers modificados)
  - Cambió la validación de credenciales en `registry.py` (eliminó el chequeo `if not credential`)
  - Tiene `providers/ollama/request.py` como archivo nuevo sin trackear
  - **NO** tiene los directorios: `scripts/`, `smoke/`, `tests/`, `.github/`, `assets/`
  - Tiene `core/anthropic/errors.py.MALO` (backup de desarrollo)

### Repo B: `D:\Agente\REPOS\free-claude-code-analysis`

- **Nombre del paquete:** `free-claude-code` v1.2.41 (idéntico)
- **Estado:** Repositorio completo (fork original de `github.com/Alishahryar1/free-claude-code`)
- **Contiene:** Código fuente completo del proxy
- **Entry points:** `fcc-server`, `fcc-init`, `fcc-claude`, `free-claude-code`
- **Particularidades:**
  - Tiene directorios adicionales: `scripts/`, `smoke/`, `tests/`, `.github/`, `assets/`
  - Tiene scripts de instalación para macOS/Linux y Windows (`scripts/install.sh`, `scripts/install.ps1`)
  - Tiene suite de tests completa
  - Tiene `read_keys.py` y `read_keys2.py` (⚠️ scripts que leen un transcript de Gemini en busca de API keys)
  - Tiene su propio `.venv/` (entorno virtual)

---

## 3. Relación entre los dos repositorios

**Conclusión: `free-server` es una copia/fork incompleta de `free-claude-code-analysis`.**

Ambos repositorios contienen esencialmente el mismo proyecto (`free-claude-code`), pero:

| Elemento | `free-server` | `free-claude-code-analysis` |
|----------|:---:|:---:|
| `pyproject.toml` idéntico | ✅ | ✅ |
| `server.py` | ✅ | ✅ |
| `api/` | ✅ | ✅ |
| `cli/` | ✅ | ✅ |
| `config/` | ✅ | ✅ |
| `core/` | ✅ | ✅ |
| `messaging/` | ✅ | ✅ |
| `providers/` (16 carpetas) | ✅ | ✅ |
| `scripts/` (instaladores) | ❌ | ✅ |
| `smoke/` (tests de humo) | ❌ | ✅ |
| `tests/` (tests unitarios) | ❌ | ✅ |
| `.github/` (CI/CD) | ❌ | ✅ |
| `assets/` (imágenes) | ❌ | ✅ |
| `read_keys.py` | ❌ | ✅ |
| `read_keys2.py` | ❌ | ✅ |
| `.venv/` | ❌ | ✅ |
| Modificaciones hardcode en providers | ✅ | ❌ |
| `errors.py.MALO` | ✅ | ❌ |
| `providers/ollama/request.py` nuevo | ✅ | ❌ |

### ¿Están conectados los dos repos?

**Sí, comparten el mismo origen.** Ambos tienen:
- Mismo `pyproject.toml` con mismo nombre, versión y dependencias
- Misma estructura de carpetas base
- Mismos entry points de CLI

**Pero `free-server` tiene modificaciones únicas** que no están en `free-claude-code-analysis`:
1. Modelos hardcodeados (Gemini, Groq, NVIDIA NIM, Ollama, OpenCode)
2. Cambio en validación de credenciales en `registry.py`
3. Archivo `providers/ollama/request.py` inexistente en el otro repo

---

## 4. ¿El comando `fcc-server` instalado en el sistema tiene que ver con `free-claude-code-analysis`?

**Sí, ambos repositorios producen el mismo comando `fcc-server`.**

Dado que:
1. Ambos tienen el mismo entry point en `pyproject.toml`
2. No hay un paquete pip `fcc-server` oficial listado
3. Hay 3 ejecutables en el sistema

Es probable que **ambos repos hayan sido instalados en modo editable** en diferentes entornos/ubicaciones, y el que realmente se ejecuta al escribir `fcc-server` depende del orden del `PATH`.

### ⚠️ Observación de seguridad

El archivo `read_keys.py` en `free-claude-code-analysis` es preocupante:

```python
# Lee un transcript de Gemini buscando strings que contengan "sk-" o "api" o "key"
with open(r'C:\Users\Katherine\.gemini\antigravity\brain\...\transcript.jsonl') as f:
    for line in f:
        data = json.loads(line)
        if 'sk-' in content or 'api' in content or 'key' in content.lower():
            print(content)
```

Esto **no está presente** en `free-server`, solo en `free-claude-code-analysis`.

---

## 5. Conclusión final

| Pregunta | Respuesta |
|----------|-----------|
| ¿`free-claude-code-analysis` produce `fcc-server`? | ✅ **Sí**, define el entry point |
| ¿`free-server` produce `fcc-server`? | ✅ **Sí**, también lo define |
| ¿Los repos están conectados? | ✅ **Sí**, mismo proyecto, `free-server` es una copia con modificaciones |
| ¿Uno depende del otro? | ❌ **No**, son repos independientes que compiten por el mismo nombre |
| ¿`fcc-server` viene de `free-claude-code-analysis`? | Podría, pero `free-server` también lo define — **depende del PATH** |
| ¿Hay datos sensibles en `free-claude-code-analysis`? | ⚠️ Sí, `read_keys.py`/`read_keys2.py` leen logs de Gemini en busca de API keys |

### Recomendación

Si la intención es tener un único proyecto funcional, se recomienda:
1. Decidir cuál de los dos repos será el **canónico**
2. Migrar los cambios útiles de `free-server` (si los hay) al canónico
3. Eliminar el otro repositorio para evitar conflictos de nombres y confusión
4. Reinstalar `fcc-server` desde el repositorio elegido
5. **Eliminar los scripts `read_keys.py` y `read_keys2.py`** del sistema — son una fuga de seguridad potencial
