# Free Server (Claude Code / OpenCode Proxy)

Este es un servidor proxy personalizado diseñado para funcionar como un puente (middleware) entre extensiones de programación como **Claude Code** u **OpenCode Zen** y diversas APIs de inteligencia artificial (Gemini, OpenRouter, Groq, Ollama, OpenCode Zen, etc.).

Ha sido **optimizado y modificado** para soportar el ecosistema de modelos del año 2026 (por ejemplo, `gemini-3.5-flash`), para arreglar problemas de tiempo de espera (timeouts) en proveedores locales, y para reparar errores visuales en la interfaz gráfica.

## 🚀 Requisitos

- **Python 3.10+**
- **uv** (El instalador y gestor de paquetes ultrarrápido de Python)

## 📥 Instalación en VPS (Linux/Ubuntu/Arm64) o Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/cryptokgame/free-server.git
   cd free-server
   ```

2. **Instalar dependencias y crear el entorno automáticamente usando `uv`:**
   ```bash
   # Esto descargará todas las librerías basadas en uv.lock y configurará los comandos
   uv sync
   ```

## ⚙️ Configuración

El servidor necesita conocer tus llaves de API (API Keys). Estas se leen desde un archivo oculto llamado `.env`.

1. Crea la carpeta global de configuración (si no existe):
   ```bash
   mkdir -p ~/.fcc
   ```

2. Copia la plantilla `.env.example` a la carpeta de configuración:
   ```bash
   cp .env.example ~/.fcc/.env
   ```

3. Abre el archivo `~/.fcc/.env` y coloca tus propias API Keys. **Importante:** Puedes usar números al final de las variables para tener múltiples llaves rotativas (ejemplo: `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`). El servidor las detectará automáticamente.

   ```env
   # Ejemplo de configuración en ~/.fcc/.env
   GEMINI_API_KEY_1="TU_LLAVE_DE_GEMINI_AQUI"
   OPENROUTER_API_KEY_1="TU_LLAVE_DE_OPENROUTER_AQUI"
   OPENCODE_API_KEY_1="TU_LLAVE_DE_OPENCODE_AQUI"

   # --- DEFAULT MODEL ROUTING ---
   MODEL="gemini/gemini-3.5-flash"
   MODEL_OPUS="gemini/gemini-3.5-flash"
   MODEL_SONNET="gemini/gemini-3.5-flash"
   MODEL_HAIKU="gemini/gemini-3.5-flash"
   MODEL_FABLE="gemini/gemini-3.5-flash"
   ```

## 🏃 Cómo ejecutarlo

Para arrancar el servidor proxy, simplemente ejecuta el comando:

```bash
uv run fcc-server
```

*(O alternativamente, si activas el entorno virtual con `source .venv/bin/activate`, puedes ejecutar directamente `fcc-server`).*

El servidor se iniciará en el puerto `1616` (por defecto `127.0.0.1:1616`).

### Panel Gráfico (Admin UI)
Una vez que el servidor esté corriendo, puedes abrir tu navegador y entrar a:
`http://localhost:1616/` o `http://<IP-DE-TU-VPS>:1616/` (si abriste el puerto).
Allí verás una interfaz visual donde todas tus llaves aparecerán como **Configured** en color verde.

## 🔌 Cómo conectarlo con Claude Code / OpenCode Zen

En la configuración de la extensión (por ejemplo, en VS Code), busca la URL del Endpoint de la API o la URL de Anthropic, y cámbiala por la de tu servidor local:
```
http://127.0.0.1:1616
```

**⚠️ PASO CRÍTICO PARA VER TODOS LOS MODELOS:**
Por defecto, Claude Code ignora los modelos de proveedores externos. Para obligarlo a que lea nuestra lista VIP completa (OpenRouter, Nvidia, Ollama) cuando escribas el comando `/model`, debes agregar esta variable de entorno oculta en tu sistema o terminal (ej. en tu `.bashrc`):

```bash
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY="1"
```

*(Nota: Si usas el comando `fcc-claude`, esta variable se inyecta mágicamente de forma automática. Solo la necesitas si usas el comando original `claude` a secas o plugins visuales).*

A partir de este momento, todas las peticiones viajarán sin retrasos directamente desde la extensión hasta tu proxy local en el VPS, y de ahí hacia los proveedores gratuitos o de pago que hayas configurado.
