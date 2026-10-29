---
name: max-academic-bolivia
description: "Asistente metodológico para monografías de compilación (revisión documental) de postgrado: Guía Oficial EIP-FINOR-UAGRM (Santa Cruz, Bolivia), Manual Metodológico Maestro (Sampieri & Mendoza Torres), normas APA 7.ª, datos verificados y enfoque en Bolivia. Búsqueda con Tavily, generación y validación de Word (.docx) con plantilla institucional de 11 elementos, distinción Cita vs. Referencia vs. Bibliografía y Sources.xml para Word. Úsala al redactar o auditar monografías, tesinas, diplomados, EIP, FINOR, UAGRM, matriz bibliográfica (MAB), planteamiento del problema, objetivos con Bloom, marco teórico, postura epistémica, conclusiones biunívocas, referencias APA 7, carátula institucional, fuentes de Bolivia (INE, BCB, ASFI, SciELO) o generar/validar el documento final."
---

# Monografía de Compilación — EIP-FINOR-UAGRM · APA 7.ª · Bolivia · Corte 2026

Construye una monografía de compilación teórica **paso a paso**, con fuentes reales y verificadas,
actualizadas al corte más reciente (**octubre 2026** o posterior), enfocada **exclusivamente en
Bolivia** (nacional, departamental, provincial o municipal). Sigue la **Guía Oficial para la
Elaboración de Monografía** y el **Manual Metodológico Maestro** de la **Escuela Integral de
Postgrado (E.I.P.)** de la **Facultad Integral del Norte (F.I.NOR.)** de la **Universidad Autónoma
Gabriel René Moreno (U.A.G.R.M.)** (Santa Cruz, Bolivia), bajo la escuela metodológica de
**Hernández Sampieri y Mendoza Torres** (el problema como árbitro soberano en cascada). Se detiene
exactamente donde el usuario lo indique y aplica la **prioridad institucional EIP-UAGRM** sobre APA 7
pura cuando haya discrepancia.

## Reglas de oro

0. **Universalidad temática y neutralidad absoluta (Agnóstica a cualquier disciplina).**
   Esta skill es un motor metodológico universal aplicable a **cualquier carrera, diplomado o tema académico**
   (ej. Redes de Computadoras, Telecomunicaciones, Ciberseguridad, Inteligencia Artificial, Derecho, Medicina,
   Agronomía, Educación, Contabilidad, Finanzas, etc.). **Queda estrictamente prohibido asumir, predeterminar o
   mezclar temas de proyectos anteriores** (como bases de datos o riesgo financiero en Santa Cruz). El 100 % del
   contenido, búsqueda, formulación, objetivos y conclusiones debe derivarse **única y exclusivamente del tema
   solicitado por el usuario en su petición actual**. Los ejemplos en las guías son meramente ilustrativos.
1. **Cero invención.** Ninguna cita, DOI, cifra, página o referencia proviene de la memoria. Toda
   fuente se encontró y verificó **en esta sesión** (URL/PDF abierto o resultado de búsqueda con
   enlace). Lo no confirmado se marca `[VERIFICAR]` y se declara en la entrega.
2. **Manejo de datos incompletos (`[CAMPOS PENDIENTES]`).** Si faltan datos clave (tema, población,
   institución, lugar, período o programa de diplomado), **pregunta al usuario o márcalos
   explícitamente como `[CAMPOS PENDIENTES]`**. Jamás inventes datos institucionales ni de contexto.
3. **Revisión documental pura sin trabajo de campo.** No copies párrafos de las fuentes. Lee,
   comprende, sintetiza, confronta y redacta con palabras propias en **tercera persona impersonal**.
   Distingue siempre las ideas de los autores de las interpretaciones del investigador.
4. **Diferenciación conceptual inviolable:**
   - **Cita:** Idea textual o parafraseada inmersa en el texto con autor y año `(p. X si es textual)`.
   - **Referencia:** Listado final con coincidencia biunívoca exacta 1:1 de las fuentes citadas.
   - **Bibliografía:** Obras leídas de fondo pero NO citadas. **Prohibido titular "Bibliografía" a la lista de obras citadas.**
5. **Calidad y umbral de fuentes.** Mínimo 5 fuentes académicas de alta jerarquía (meta 10–15).
   Prohibido Wikipedia, monografias.com o sitios informales. La omisión de citas causa anulación por plagio.
6. **Cuerpo 100 % textual (Prohibición estricta de tablas en el cuerpo).**
   En cada monografía de compilación, el cuerpo del documento (Capítulos 1 al 7: Introducción, Planteamiento del Problema, Objetivos, Revisión de Literatura, Definición de Términos, Discusión y Conclusiones) es **estricta y exclusivamente textual (prosa narrativa continua)**. **Nunca existen tablas, cuadros, figuras ni gráficos dentro del cuerpo**. Toda tabla, matriz comparativa o gráfico suplementario (incluyendo la Matriz de Análisis Bibliográfico MAB, cuadros estadísticos de INE/BCB/ASFI o diagramas) debe ubicarse **exclusivamente al final del documento como Apéndices** (después de Referencias), aun cuando otras normativas generales de estilo permitan insertarlas.

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

## 1. Secuencia de ejecución (11 pasos, en 3 macroetapas praxiológicas)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. Etapa de Cimentación:       P1 (Título) ➔ P2 (Planteamiento) ➔ P3 (Objetivos)       │
│ 2. Etapa de Desarrollo:        P4 (Revisión MAB) ➔ P5 (Términos) ➔ P6 (Discusión) ➔    │
│                                P7 (Conclusiones biunívocas)                            │
│ 3. Etapa de Enmarque/Cierre:   P8 (Introducción) ➔ P9 (Resumen) ➔ P10 (Referencias) ➔ │
│                                P11 (Carátula institucional e índice automático)        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Paso | Producto | Criterio de cierre |
|---|---|---|
| P1 | Título borrador | Procedimiento 5 pasos EIP, ≤ 20 palabras, nominal, QUÉ + PARA QUIÉN + DÓNDE + CUÁNDO, sin punto final |
| P2 | Planteamiento | Pirámide invertida (global → Bolivia → GAP) + una pregunta motora abierta (QUÉ, DÓNDE, CUÁNDO) |
| P3 | Objetivos | OG con las 5 preguntas canónicas + 3–5 OE escalonados (Bloom/Bavaresco/Balestrini), sin verbos de campo |
| P4 | Revisión literaria | Ejes temáticos, 5 preguntas del estado del arte, ≥ 5 fuentes indexadas (meta 10–15), síntesis crítica Nivel 3, MAB |
| P5 | Definiciones | 5–10 constructos, 3 partes, ≤ 100 palabras cada uno, autores especializados |
| P6 | Discusión | 5 partes, voz del investigador, postura epistémica, confrontación de acuerdos y desacuerdos, **cero datos nuevos** |
| P7 | Conclusiones | 1 párrafo conciso por cada OE + 1 para el OG, pretérito impersonal, sin citas nuevas |
| P8 | Introducción | Se redacta al final; 5 párrafos; encabezado `1. Introducción` |
| P9 | Resumen y palabras clave | 3 componentes EIP (intro/objetivos, hallazgos, conclusiones), ≤ 400 palabras, 3–6 palabras clave |
| P10 | Título definitivo y referencias | Auditoría 1:1 citas ↔ referencias, APA 7, enlaces activos, distinción Cita vs. Referencia |
| P11 | Carátula e índice | Carátula oficial de 11 elementos (Arial 14 pt título, 12 pt autor/docente), paginación mixta, índice por estilos |

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
6. **Prioridad EIP.** Resumen ≤ 400 palabras, carátula de 11 elementos con número invisible,
   romanos en preliminares y arábigos reiniciando en la Introducción.
7. **Premadurez prohibida.** En entregas de Cimientos (P1–P3) no se incluye Introducción (P8),
   Índice (P11) ni Referencias finales (P10); el respaldo es la MAB como Apéndice A.
8. **Cuerpo exclusivamente textual.** Cero tablas, cuadros o figuras intercaladas en los capítulos del cuerpo (P1–P8). Todo el análisis es narrativo puro; las tablas y figuras se ubican exclusivamente en la sección final de Apéndices.

Matriz normativa completa (TIT, PRO, OBJ, REV, TER, DIS, CON, INT, RES, REF, CAR, PAG, FOR, IND,
APE, ACT, GEO) y checklist maestro de verificación: `references/reglas_institucionales.md`.

## 3. Capacidades Incorporadas (Word · Tavily · Bibliografía)

La skill es **completamente autocontenida**: funciona en cualquier proyecto limpio sin necesidad de instalar skills externas. Incorpora internamente:

| Capacidad | Módulos y scripts incorporados | Referencia técnica |
|---|---|---|
| **Búsqueda tipo Perplexity** | `scripts/buscar_fuentes.py` (CLI `tvly` o API REST directa con `TAVILY_API_KEY`) y `scripts/generar_consultas.py` | [references/tavily_busqueda.md](references/tavily_busqueda.md) y [references/busqueda_bolivia.md](references/busqueda_bolivia.md) |
| **Generación & validación Word** | `scripts/generar_monografia_docx.py` (compilador dinámico de Markdown a Word sin datos prefijados) y `scripts/docx_utils.py` (validación OOXML, fusión de runs, extracción) | [references/docx_guia.md](references/docx_guia.md) |
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
| `references/reglas_institucionales.md` | Antes de redactar o auditar; matriz normativa y checklist maestro |
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
| `scripts/generar_monografia_docx.py` | Compilador universal y dinámico de Markdown (`monografia_completa.md`) a Word sobre la plantilla oficial |
| `templates/apa7ma.docx` | Plantilla oficial APA 7 con estilos nativos y numeración automática |
| `assets/logo.png` | Logotipo oficial de la institución para la carátula |

## 7. Cierre obligatorio

Antes de declarar terminado un entregable:

1. Ejecuta `python scripts/auditar_monografia.py <archivo> --json` y corrige todo error (✖).
2. Revisa el checklist maestro en `references/reglas_institucionales.md`.
3. Verifica que cada cita del texto tenga su referencia y viceversa (1:1).
4. Revisa que ninguna fuente sea inventada, duplicada o fuera de la ventana 2021–2026.
5. Si hay `.docx`, ábrelo o conviértelo para confirmar carátula, paginación e índice.
6. Ten presentes los plazos institucionales de entrega (anillado en ≤ 10 días hábiles, subsanación, empastados + CD, defensa en ≤ 30 días post-módulo).
7. Entrega un resumen de: archivos generados, fuentes añadidas, supuestos y pendientes
   `[CAMPOS PENDIENTES]` / `[VERIFICAR]`.

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
# Global desde carpeta local
bunx skills add ./skills/max-academic-bolivia -g -y
```

Requisitos y solución de problemas: `README.md` del repositorio.
