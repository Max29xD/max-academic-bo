# 🎓 Monografía de Compilación — EIP-FINOR-UAGRM (Bolivia)

> **Skill de agente para elaboración, búsqueda documental, generación en Word y auditoría de monografías de postgrado (EIP-FINOR-UAGRM, corte 2026, APA 7.ª edición).**

[![Skill Compatible](https://img.shields.io/badge/skills.sh-compatible-blue?style=flat-square)](https://skills.sh)
[![Normas APA](https://img.shields.io/badge/Normas-APA%207.%C2%AA%20edici%C3%B3n-success?style=flat-square)](https://apastyle.apa.org/)
[![Enfoque](https://img.shields.io/badge/Enfoque-Bolivia%20(2021--2026)-red?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)

Esta skill permite a cualquier agente de IA (Antigravity, Claude Code, Cursor, Cline, etc.) asistir paso a paso en la elaboración de **monografías de compilación documental**. Es **100 % autocontenida y portable**: no requiere instalar plugins adicionales para generar documentos Word ni para gestionar citas.

---

## ⚡ Instalación Rápida con `bunx skills`

En cualquier proyecto donde quieras trabajar, ejecuta en tu terminal:

### Opción A: Desde GitHub (Recomendado)
```bash
bunx skills add <tu-usuario>/<tu-repo> --skill monografia-compilacion-bolivia -y
```

### Opción B: Instalación Global (disponible en todos tus proyectos)
```bash
bunx skills add <tu-usuario>/<tu-repo> --skill monografia-compilacion-bolivia -g -y
```

### Opción C: Desde una copia local (sin subir a GitHub)
```bash
bunx skills add ./skills/monografia-compilacion-bolivia -y
```

---

## 🧩 ¿Qué incluye esta Skill?

No necesitas instalar skills secundarias. Todo viene integrado en el paquete:

| Capacidad | Módulo Incorporado | Descripción |
|---|---|---|
| 📄 **Word Profesional (.docx)** | `scripts/generar_monografia_docx.py`<br>`scripts/docx_utils.py` | Genera el `.docx` oficial sobre la plantilla `apa7ma.docx`, con carátula de 10 elementos, numeración romana/arábiga y validación contra el esquema XML de Word. |
| 🔍 **Búsqueda tipo Perplexity** | `scripts/buscar_fuentes.py`<br>`scripts/generar_consultas.py` | Búsqueda profunda de literatura real en Bolivia (BCB, ASFI, INE, SciELO) mediante el CLI `tvly` o directamente con `TAVILY_API_KEY`. Guarda evidencia reproducible en `output/fuentes/`. |
| 📚 **Bibliografía APA 7 + Word** | `scripts/word_bibliography.py`<br>`scripts/gestor_referencias.py` | Genera `Sources.xml` para importar directamente en Microsoft Word (**Referencias → Administrar fuentes**) y la lista de referencias en Markdown APA 7. |
| 🛡️ **Auditoría Metodológica** | `scripts/auditar_monografia.py` | Audita borradores contra las reglas institucionales (cero citas inventadas, ventana 2021–2026, verbos Bloom y ausencia de premadurez). |

---

## 📝 Secuencia de Trabajo (11 Pasos)

La skill trabaja de manera modular y no lineal; puedes pedirle que ejecute pasos individuales o bloques completos:

```text
CIMIENTOS (P1–P3)  ──►  NÚCLEO (P4–P7)  ──►  CIERRE (P8–P11)  ──►  ENTREGA (.docx)
```

| Paso | Entregable | Criterio de Cierre |
|---|---|---|
| **P1** | **Título borrador** | ≤ 20 palabras, nominal, sin punto final (Qué + Quién + Dónde + Cuándo). |
| **P2** | **Planteamiento** | Pirámide invertida (Global → Bolivia → GAP local) + 1 pregunta motora abierta. |
| **P3** | **Objetivos** | 1 Objetivo General canónico + 3 a 5 Objetivos Específicos escalonados (Bloom). |
| **P4** | **Revisión literaria** | Síntesis crítica por temas, ≥ 5 fuentes indexadas y Matriz de Análisis (MAB). |
| **P5** | **Definiciones** | 5 a 10 constructos clave conceptualizados por autores reconocidos. |
| **P6** | **Discusión** | Análisis crítico de hallazgos; **cero autores o cifras nuevas**. |
| **P7** | **Conclusiones** | 1 conclusión por objetivo específico + 1 integradora; pretérito impersonal. |
| **P8** | **Introducción** | Se redacta al final (5 párrafos canónicos que integran todo el trabajo). |
| **P9** | **Resumen y palabras clave** | Párrafo único de hasta 400 palabras + 3 a 6 palabras clave. |
| **P10** | **Título definitivo y citas** | Auditoría 1:1 entre citas del texto y lista de referencias APA 7. |
| **P11** | **Carátula e índice** | Carátula institucional reglamentaria, índice automático y paginación mixta. |

---

## 💬 Prompts Listos para Usar con tu Agente

Una vez instalada la skill, puedes darle instrucciones como estas:

### 1. Iniciar los Cimientos (Pasos 1 al 3)
> *"Hasta el paso 3 (CIMIENTOS): elabora el título, el planteamiento del problema y los objetivos para una monografía sobre adopción de pagos QR en Santa Cruz, Bolivia (corte 2026). Busca fuentes reales y guarda la MAB como Apéndice A."*

### 2. Buscar Literatura Verificada
> *"Busca literatura académica e informes oficiales sobre regulación fintech en Bolivia entre 2021 y 2026. Guarda la evidencia de búsqueda y añade las fuentes al catálogo."*

### 3. Generar la Bibliografía y `Sources.xml` para Word
> *"Toma las fuentes encontradas, genera el archivo referencias.json, la lista formateada en APA 7 y el Sources.xml para importarlo en Microsoft Word."*

### 4. Generar el Documento Word y Auditar
> *"Ensambla la monografía completa en Word usando la plantilla institucional y corre la auditoría para verificar que cumpla todas las reglas antes de entregar."*

---

## 🛠️ Comandos de Terminal Útiles

Todos los scripts pueden ejecutarse manualmente en cualquier momento:

```bash
# 1. Comprobar que tu entorno tenga todo lo necesario
python skills/monografia-compilacion-bolivia/scripts/verificar_entorno.py

# 2. Buscar literatura (CLI tvly o mediante variable TAVILY_API_KEY)
python skills/monografia-compilacion-bolivia/scripts/buscar_fuentes.py "inclusión financiera Bolivia" --tipo search --rango-tiempo year

# 3. Generar la bibliografía (Sources.xml y referencias_bibliograficas.md)
python skills/monografia-compilacion-bolivia/scripts/gestor_referencias.py

# 4. Construir el documento Word oficial
python skills/monografia-compilacion-bolivia/scripts/generar_monografia_docx.py

# 5. Auditar el contenido contra las normas institucionales
python skills/monografia-compilacion-bolivia/scripts/auditar_monografia.py output/monografia_completa.md --json

# 6. Validar que el archivo .docx no tenga errores de esquema OOXML
python skills/monografia-compilacion-bolivia/scripts/docx_utils.py validar output/monografia_compilacion_bolivia.docx
```

---

## 📂 Directorio de Salida (`output/`)

Cuando la skill trabaja en tu proyecto, deposita todos los archivos generados en `./output/` (ignorado por Git para mantener tu repositorio limpio):

- `output/monografia_completa.md`: Manuscrito de trabajo en Markdown.
- `output/monografia_compilacion_bolivia.docx`: Documento Word final listo para presentar.
- `output/referencias.json`: Catálogo maestro de fuentes verificadas.
- `output/referencias_bibliograficas.md`: Lista de referencias en formato APA 7.
- `output/Sources.xml`: Archivo importable en Word (**Referencias → Administrar fuentes → Examinar**).
- `output/fuentes/*.json`: Evidencia reproducible de cada búsqueda realizada.

---

## ❓ Preguntas Frecuentes

<details>
<summary><b>¿Qué necesito tener instalado en mi computadora?</b></summary>
Solo necesitas <b>Python 3.10+</b> y la librería <code>python-docx</code> (<code>pip install python-docx</code>). La búsqueda con Tavily y la bibliografía funcionan de forma nativa.
</details>

<details>
<summary><b>¿Cómo activo las búsquedas profundas con Tavily?</b></summary>
Puedes instalar el CLI oficial (<code>curl -fsSL https://cli.tavily.com/install.sh | bash</code>) o simplemente definir tu clave en las variables de entorno:<br>
<code>$env:TAVILY_API_KEY="tvly-..."</code> (en Windows PowerShell) o <code>export TAVILY_API_KEY="tvly-..."</code> (en Linux/Mac). Si no tienes clave, el agente utilizará su búsqueda web nativa y registrará la evidencia con <code>--plantilla</code>.
</details>

<details>
<summary><b>¿Cómo importo las fuentes en Microsoft Word?</b></summary>
Abre tu Word, ve a la pestaña <b>Referencias</b> → <b>Administrar fuentes</b> → haz clic en <b>Examinar...</b> y selecciona el archivo <code>output/Sources.xml</code>. Copia las fuentes a la lista del documento y listo.
</details>

---

## 📄 Licencia

Este proyecto está disponible bajo la licencia MIT. La plantilla institucional y logotipos pertenecen a la EIP-FINOR-UAGRM para fines académicos.
