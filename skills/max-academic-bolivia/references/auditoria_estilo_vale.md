# Auditoría de Estilo y Detección de Patrones de IA con Vale

Este documento describe la integración de **Vale** (linter de prosa en Go) en la skill **Max Academic Bolivia**, orientado a garantizar una redacción académica rigurosa y libre de sesgos estilísticos o muletillas sintéticas típicas de modelos de lenguaje (LLM / IA).

---

## 1. ¿Por qué Vale en una Monografía de Compilación?

Mientras que `auditar_monografia.py` verifica la **macroestructura institucional** (normas EIP-FINOR, verbos cognitivos Bloom, anclaje geográfico boliviano, reciprocidad 1:1 de citas APA), **Vale audita la microestructura de la prosa**:
* **Determinista y sin consumo de tokens:** Ejecución nativa en milisegundos en Go.
* **Compatibilidad dual:** Procesa archivos `.md` / `.txt` durante la redacción y archivos `.docx` finales.
* **Tolerancia cero a la retórica de IA:** Detecta fórmulas sintéticas, guiones largos espurios y adjetivación vacía.

---

## 2. Instalación de Vale

### En Windows con Scoop (Recomendado)
```powershell
# Instalar Scoop si no está disponible:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Instalar Vale:
scoop install vale
```

### Métodos alternativos
* **Chocolatey:** `choco install vale`
* **Winget:** `winget install errata-ai.vale`
* **macOS:** `brew install vale`
* **Linux:** `brew install vale` o descarga directa desde [Vale Releases](https://github.com/errata-ai/vale/releases)

---

## 3. Configuración y Reglas Nativas (`Monografia`)

El archivo `.vale.ini` en la raíz del proyecto activa el estilo `Monografia`:

```ini
StylesPath = styles
MinAlertLevel = suggestion

[*.{md,txt,docx}]
BasedOnStyles = Monografia
```

### Reglas implementadas en `styles/Monografia/`:

1. **`EmDash.yml` (Nivel: Error):**
   * **Problema:** Los LLM en inglés usan masivamente la raya o guion largo (`—`) o semirraya (`–`) como inciso reflexivo. En español académico, esto genera un calco anglicado artificial.
   * **Corrección:** Usar comas (`,`), paréntesis `(...)` o subordinación sintáctica fluida.

2. **`AiCliches.yml` (Nivel: Warning):**
   * **Problema:** Muletillas y aperturas grandilocuentes de relleno (*AI fluff*): *"es crucial destacar"*, *"es imperativo señalar"*, *"cabe resaltar"*, *"navegar el complejo panorama"*, *"un tapiz de"*, *"un testimonio de"*, *"la piedra angular"*, *"en el vertiginoso mundo"*, *"a modo de colofón"*.
   * **Corrección:** Exponer los hechos y datos empíricos de forma directa y sobria.

3. **`AiAdjectives.yml` (Nivel: Warning):**
   * **Problema:** Adjetivación inflada y laudatoria de IA: *revolucionario, transformador, paradigmático, holístico, fascinante, multifacético, intrínseco*.
   * **Corrección:** Emplear terminología científica sobria, mesurada y precisa.

4. **`Impersonalidad.yml` (Nivel: Error):**
   * **Problema:** Deslizamientos hacia la primera persona: *"yo analicé"*, *"nosotros"*, *"nuestro estudio"*, *"podemos ver"*, *"veremos"*.
   * **Corrección:** Tercera persona impersonal obligatoria bajo guía EIP-FINOR (*"se analizó"*, *"se concluye"*, *"el presente estudio"*).

5. **`Sustituciones.yml` (Nivel: Suggestion):**
   * Propone sustituciones inmediatas de giros trillados por fórmulas académicas precisas (ej. *"juega un papel fundamental"* → *"influye de manera directa"*).

---

## 4. Uso y Comandos

### Verificación y Autoconfiguración Inicial
```bash
python scripts/verificar_entorno.py --setup
```
Este comando detecta si Vale está instalado; si no lo está y Scoop está disponible, lo instala automáticamente y asegura que `.vale.ini` y `styles/Monografia` estén desplegados en el proyecto.

### Auditoría Integrada en el Script Institucional
```bash
python scripts/auditar_monografia.py output/monografia_completa.md
# O sobre el archivo compilado de Word:
python scripts/auditar_monografia.py output/max_academic_bolivia.docx
```
El script ejecuta Vale internamente y reporta las observaciones con los identificadores `[VAL-ERR]`, `[VAL-WARN]` y `[VAL-SUG]`.

### Ejecución Directa de Vale
```bash
# Auditar un borrador en Markdown:
vale output/cimientos.md

# Auditar una carpeta completa:
vale output/

# Auditar el documento final .docx:
vale output/max_academic_bolivia.docx
```
