---
name: max-academic-bolivia
description: >-
  Asistente metodológico para monografías de compilación (revisión documental) de postgrado:
  Guía EIP-FINOR-UAGRM 2025/2026, APA 7.ª, datos verificados (corte 2026) y enfoque en Bolivia.
  Incorpora búsqueda tipo Perplexity con Tavily (CLI o REST API), generación y validación de Word
  (.docx) con plantilla institucional y bibliografía APA 7 con Sources.xml para Word. Úsala al
  redactar o auditar monografías, tesinas, diplomados, EIP, FINOR, UAGRM, estado del arte,
  matriz bibliográfica (MAB), planteamiento, objetivos, marco teórico, referencias APA 7, resumen,
  carátula institucional, buscar o verificar fuentes de Bolivia (INE, BCB, ASFI, SciELO) o
  generar/validar el documento Word final.
compatibility: >-
  Requiere Python 3.10+ y python-docx. Tavily CLI (tvly) o TAVILY_API_KEY son opcionales (soporta
  búsqueda web nativa con registro de evidencia). Autocontenido en cualquier proyecto.
metadata:
  version: "2.1.0"
  idioma: es
---

# Monografía de Compilación — EIP-FINOR-UAGRM · APA 7.ª · Bolivia · Corte 2026

Construye una monografía de compilación **paso a paso**, con fuentes reales y verificadas,
actualizadas al corte más reciente (**octubre 2026** o posterior), enfocada **exclusivamente en
Bolivia** (nacional, departamental, provincial o municipal). Se detiene exactamente donde el
usuario lo indique y aplica la **prioridad institucional EIP-UAGRM** sobre APA 7 pura cuando
haya discrepancia.

## Regla de oro

**Cero invención.** Ninguna cita, DOI, cifra, página o referencia proviene de la memoria. Toda
fuente se encontró y verificó **en esta sesión** (URL/PDF abierto o resultado de búsqueda con
enlace). Lo no confirmado se marca `[VERIFICAR]` y se declara en la entrega.

## 0. Antes de empezar (30 segundos)

1. Ejecuta el diagnóstico de entorno:

   ```bash
   python scripts/verificar_entorno.py
   ```

   Informa qué hay disponible: `python-docx`, `tvly`, skills `docx`, `word-bibliography` y
   `tavily-*`, y qué rutas de salida se usarán. Si falta algo, aplica el plan B de
   [references/integraciones.md](references/integraciones.md); **nunca bloquees la tarea**.
2. Confirma con el usuario, si no está claro: tema, delimitación boliviana, carrera/programa,
   año de corte, alcance (`HASTA Pn`, `CIMIENTOS`, `NUCLEO`, `CIERRE`, `COMPLETO`) y ritmo
   (`PAUSA` o `CORRIDO`). Si el usuario ya lo dijo, no vuelvas a preguntar.
3. Lee solo lo necesario: `references/reglas_institucionales.md` antes de redactar o auditar;
   `references/plantillas_por_paso.md` para el paso concreto; `references/apa7_formatos.md`
   para citas, tablas y referencias; `references/busqueda_bolivia.md` antes de buscar.

## 1. Secuencia de ejecución (11 pasos, no lineal)

| Paso | Producto | Criterio de cierre |
|---|---|---|
| P1 | Título borrador | ≤ 20 palabras, nominal, QUÉ + PARA QUIÉN + DÓNDE + CUÁNDO, sin punto final |
| P2 | Planteamiento | Pirámide invertida (global → Bolivia → GAP) + una pregunta motora abierta |
| P3 | Objetivos | OG con las 5 preguntas canónicas + 3–5 OE escalonados (Bloom), sin verbos de campo |
| P4 | Revisión literaria | Por temas, ≥ 5 fuentes indexadas (meta 10–15), síntesis crítica Nivel 3, MAB |
| P5 | Definiciones | 5–10 constructos, 3 partes, ≤ 100 palabras cada uno, autores especializados |
| P6 | Discusión | 5 partes, voz del investigador, **cero autores o datos nuevos** |
| P7 | Conclusiones | 1 por OE + 1 integradora, pretérito impersonal, sin citas nuevas |
| P8 | Introducción | Se redacta al final; 5 párrafos; encabezado `1. Introducción` |
| P9 | Resumen y palabras clave | Párrafo único ≤ 400 palabras, 3–6 palabras clave |
| P10 | Título definitivo y referencias | Auditoría 1:1 citas ↔ referencias, APA 7, enlaces activos |
| P11 | Carátula e índice | 10 elementos, paginación mixta, índice automático por estilos |

**Por qué este orden:** no se puede introducir ni resumir lo que aún no existe; la revisión (P4)
alimenta P5–P7; los objetivos (P3) fijan el contrato que P7 debe liquidar; la carátula y el
índice (P11) requieren datos finales cerrados.

Detalle operativo, cuestionarios y esqueletos: `references/plantillas_por_paso.md`.

## 2. Reglas inviolables

1. **Enfoque Bolivia obligatorio.** La literatura extranjera solo sirve como marco conceptual o
   contraste; el objeto de estudio siempre es Bolivia o una de sus jurisdicciones.
2. **Actualidad.** Al menos 70 % de fuentes de 2021–2026, con publicaciones activas 2024–2026
   (INE Censo 2024, BCB, ASFI, UDAPE, CEPAL, SciELO Bolivia, repositorios).
3. **Documental puro.** Prohibido encuestar, entrevistar, medir en campo o proponer modelos
   empíricos propios.
4. **Cadena biunívoca.** Título → Problema → Objetivos → Revisión → Discusión → Conclusiones.
   P6 y P7 no introducen autores ni datos nuevos.
5. **Voz crítica Nivel 3.** Paráfrasis > 80 %; > 60 % de párrafos de P4 confrontan autores y
   contextualizan a Bolivia.
6. **Prioridad EIP.** Resumen ≤ 400 palabras, carátula de 10 elementos con número invisible,
   romanos en preliminares y arábigos reiniciando en la Introducción.
7. **Premadurez prohibida.** En entregas de Cimientos (P1–P3) no se incluye Introducción (P8),
   Índice (P11) ni Referencias finales (P10); el respaldo es la MAB como Apéndice A.

Matriz normativa completa (TIT, PRO, OBJ, REV, TER, DIS, CON, INT, RES, REF, CAR, PAG, FOR, IND,
APE, ACT, GEO) y checklist maestro de 16 puntos: `references/reglas_institucionales.md`.

## 3. Capacidades Incorporadas (Word · Tavily · Bibliografía)

La skill es **completamente autocontenida**: funciona en cualquier proyecto limpio sin necesidad de instalar skills externas. Incorpora internamente:

| Capacidad | Módulos y scripts incorporados | Referencia técnica |
|---|---|---|
| **Búsqueda tipo Perplexity** | `scripts/buscar_fuentes.py` (CLI `tvly` o API REST directa con `TAVILY_API_KEY`) y `scripts/generar_consultas.py` | [references/tavily_busqueda.md](references/tavily_busqueda.md) y [references/busqueda_bolivia.md](references/busqueda_bolivia.md) |
| **Generación & validación Word** | `scripts/generar_monografia_docx.py` (plantilla oficial) y `scripts/docx_utils.py` (validación OOXML, fusión de runs, extracción) | [references/docx_guia.md](references/docx_guia.md) |
| **Bibliografía APA 7 + Sources.xml** | `scripts/gestor_referencias.py`, `scripts/word_bibliography.py` y `scripts/actualizar_sources_xml.py` | [references/word_bibliography_guia.md](references/word_bibliography_guia.md) y [references/apa7_formatos.md](references/apa7_formatos.md) |
| **Auditoría metodológica** | `scripts/auditar_monografia.py` y `scripts/auditor_utils.py` | [references/reglas_institucionales.md](references/reglas_institucionales.md) |

**Evidencia de búsqueda:** cada consulta guarda un JSON en `output/fuentes/` con parámetros, fecha, resultados y URLs. La MAB (Apéndice A) y el registro de búsqueda (Apéndice B) se sustentan estrictamente en esa evidencia. Sin URL/DOI verificable no se admite ninguna fuente.

## 4. Rutas y salidas

- **Salida por defecto:** `./output/` del proyecto donde se ejecuta la skill.
- **Override:** variable de entorno `MONOGRAFIA_OUTPUT` (ruta absoluta o relativa).
- **Recursos internos (inmutables):** `templates/apa7ma.docx`, `assets/logo.png`, `references/`.
- **Archivos generados en el proyecto:**
  - `output/<tema>.md` o `output/monografia_completa.md`
  - `output/monografia_compilacion_bolivia.docx`
  - `output/referencias.json`, `output/referencias_bibliograficas.md`, `output/Sources.xml`
  - `output/fuentes/*.json` (evidencia de rastreo de literatura)

Si el usuario ya tiene un `output/` con avances, **no lo sobrescribas a ciegas**: compara y pide confirmación antes de reemplazar.

## 5. Comandos de control de alcance

- `HASTA Pn` — ejecuta hasta el paso n y pausa.
- `CIMIENTOS` (P1–P3) · `NUCLEO` (P4–P7) · `CIERRE` (P8–P11) · `COMPLETO` (P1–P11).
- `SOLO Pn` o `SOLO BUSCAR` — ejecuta únicamente esa tarea.
- `AUDITAR` — evalúa un borrador contra las reglas con ID y la recencia 2021–2026.
- `PAUSA` — espera aprobación tras cada paso; `CORRIDO` — avanza hasta el siguiente bloqueo.

## 6. Mapa de archivos

| Archivo | Cuándo leerlo / usarlo |
|---|---|
| `references/reglas_institucionales.md` | Antes de redactar o auditar; matriz normativa y checklist maestro de 16 puntos |
| `references/plantillas_por_paso.md` | Al ejecutar cualquier paso: cuestionarios, esqueletos y fórmulas canónicas |
| `references/apa7_formatos.md` | Citas, 5 niveles de encabezado, formato de tablas/figuras y lista APA 7 |
| `references/docx_guia.md` | Buenas prácticas Word OOXML, encabezados multinivel, tablas y validación |
| `references/tavily_busqueda.md` | Búsqueda estilo Perplexity con Tavily (search, research, extract) y evidencia |
| `references/word_bibliography_guia.md` | Estándar XML de bibliografía Word, SourceTypes y pasos de importación |
| `references/busqueda_bolivia.md` | Protocolo de recencia 2024–2026 y embudo territorial boliviano |
| `references/integraciones.md` | Matriz de compatibilidad y planes de degradación elegante |
| `scripts/verificar_entorno.py` | Diagnóstico inicial de capacidades y rutas |
| `scripts/buscar_fuentes.py` | Búsqueda reproducible con evidencia en `output/fuentes/` (Tavily CLI o REST API) |
| `scripts/generar_consultas.py` | Cadenas booleanas y consultas por embudo geográfico |
| `scripts/docx_utils.py` | Validación OOXML, extracción de texto y fusión de runs para Word |
| `scripts/word_bibliography.py` | Generador directo de `Sources.xml` y formateador APA 7 |
| `scripts/gestor_referencias.py` | `referencias.json` → APA 7 + `Sources.xml` + incrustación en docx |
| `scripts/actualizar_sources_xml.py` | Motor XML de bibliografía compatible con Microsoft Word |
| `scripts/auditar_monografia.py` | Auditoría automática de `.md`/`.txt`/`.docx` contra la guía institucional |
| `scripts/generar_monografia_docx.py` | Ensamblado del `.docx` institucional sobre la plantilla oficial |
| `templates/apa7ma.docx` | Plantilla oficial APA 7 con estilos nativos y numeración automática |
| `assets/logo.png` | Logotipo oficial de la institución para la carátula |

## 7. Cierre obligatorio

Antes de declarar terminado un entregable:

1. Ejecuta `python scripts/auditar_monografia.py <archivo> --json` y corrige todo error (✖).
2. Revisa el checklist maestro de 16 puntos en `references/reglas_institucionales.md`.
3. Verifica que cada cita del texto tenga su referencia y viceversa (1:1).
4. Revisa que ninguna fuente sea inventada, duplicada o fuera de la ventana 2021–2026.
5. Si hay `.docx`, ábrelo o conviértelo para confirmar carátula, paginación e índice.
6. Entrega un resumen de: archivos generados, fuentes añadidas, supuestos y pendientes
   `[VERIFICAR]`.

## 8. Instalación (para el agente o el usuario)

Repositorio con la skill en `skills/max-academic-bolivia/`. Instalación global o por
proyecto:

```bash
# Global (disponible en todos los proyectos)
bunx skills add Max29xD/max-academic-bo --skill max-academic-bolivia -g -y

# Por proyecto (queda en .agents/skills y se fija en skills-lock.json)
bunx skills add Max29xD/max-academic-bo --skill max-academic-bolivia -y
```

Si el repo no está publicado, también acepta la ruta local:

```bash
bunx skills add ./skills/max-academic-bolivia -g -y
```

Requisitos y solución de problemas: `README.md` del repositorio.
