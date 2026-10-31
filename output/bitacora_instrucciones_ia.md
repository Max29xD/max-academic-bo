# Bitácora de Registro de Prompts e Interacción con Inteligencia Artificial
**Programa:** Escuela Integral de Postgrado (EIP) — Facultad Integral del Norte (FINOR) — UAGRM  
**Postgraduante:** Marcos Leandro Bonilla Borges  
**Gestión:** 2026  
**Lugar:** Santa Cruz, Bolivia  

---

## 1. Declaración de Integridad Académica y Uso Ético de Inteligencia Artificial

En cumplimiento con los principios de honestidad intelectual, transparencia metodológica y las directrices institucionales de postgrado de la Universidad Autónoma Gabriel René Moreno (UAGRM), se certifica que:

1. **Autoría y Responsabilidad Intelectual:** Las herramientas de Inteligencia Artificial Generativa y asistentes agenticos han sido empleados exclusivamente como **apoyo técnico, metodológico, de compilación y formateo estructural**. La formulación de los juicios críticos, la selección de la postura epistémica, la delimitación temática en Bolivia y la verificación de cada dato, cifra y fuente bibliográfica corresponden de forma soberana e indelegable al postgraduante.
2. **Trazabilidad y Verificabilidad:** Cada instrucción, consulta heurística y código automatizado ejecutado durante la elaboración y corrección de la monografía se encuentra rigurosamente documentado en la presente bitácora para fines de auditoría por el Comité Académico y el Tribunal Evaluador.
3. **Cero Invención (Antialucinación):** Ningún hallazgo o referencia bibliográfica proviene de la memoria generativa no sustentada. Todas las citas y fuentes han sido contrastadas con repositorios científicos indexados (SciELO, Redalyc, Dialnet, repositorios universitarios) y entidades oficiales del Estado Plurinacional de Bolivia (INE, BCB, ASFI, ministerios sectoriales).

---

## 2. Registro Cronológico de Instrucciones y Prompts Ejecutados

| No. | Fecha / Hora | Paso / Fase | Prompt / Instrucción Ejecutada | Asistente / Herramienta IA | Producto / Salida Generada | Control y Verificación Humana del Postgraduante |
|---|---|---|---|---|---|---|
| **01** | 2026-10-31 | P0 — Diagnóstico y Configuración | "Verificar el entorno de trabajo, bibliotecas de Python, plantillas OOXML institucionales y dependencias de generación Word." | Antigravity CLI / Python `verificar_entorno.py` | Diagnóstico de entorno y estructura base de carpetas (`output/`, `skills/`). | Verificación de instalación de `python-docx`, `lxml` y plantilla oficial `apa7ma.docx`. |
| **02** | 2026-10-31 | P1–P11 — Auditoría de Motor y Corrección de DOCX | "Hay que corregir algo: después del índice sale Universidad: UAGRM... Autor:... antes de la Introducción. Corregir numeración en esquina superior derecha: preliminares romanos invisibles, cuerpo en arábigos continuos sin reiniciar en 1. Tipografía en Arial. Generar archivos Markdown y la Bitácora de instrucciones de IA. Investigar humanizadores gratuitos a corte 2026." | Antigravity Agent (Gemini 3.8 Flash High) + `generar_monografia_docx.py` | 1. Corrección del compilador DOCX (`generar_monografia_docx.py`).<br>2. Supresión de fuga de metadatos en el cuerpo.<br>3. Paginación mixta institucional superior derecha continua.<br>4. Unificación tipográfica en Arial 11 pt.<br>5. Creación de `output/bitacora_instrucciones_ia.md`.<br>6. Reporte de investigación sobre humanizadores. | Inspección del código XML del documento `.docx`, confirmación de eliminación de metadatos duplicados entre Índice e Introducción y validación de numeración continua en encabezado derecho. |
| **03** | 2026-10-31 | Estilo y Redacción — Integración Humanamente | "usa entonces ese de humanamente e implementalo en el skills de max" | Antigravity Agent (Gemini 3.8 Flash High) | 1. Creación de `scripts/humanizar_texto.py` (auditor y reescritor conservador con protección total de citas APA).<br>2. Creación de `references/humanamente_guia.md`.<br>3. Adición de reglas Vale (`Paralelismos.yml`, `GerundiosConsecuencia.yml`, `AperturasFluff.yml`).<br>4. Integración nativa en `auditar_monografia.py` (`HUM-1` a `HUM-7`).<br>5. Actualización de `SKILL.md` con la Regla de Oro 10 (Protocolo Humanamente). | Validación de ejecución del auditor con el nuevo módulo Humanamente (puntaje 100/100 en textos limpios y detección precisa de tics en textos artificiales sin tocar citas ni siglas). |

---

## 3. Guía de Actualización Continua de la Bitácora

Cada vez que se ejecute una nueva instrucción de generación o ajuste (redacción de acápites, búsqueda de fuentes en Tavily, auditoría metodológica), se debe añadir una nueva fila a la tabla anterior con:
- **No.:** Número correlativo de la instrucción.
- **Fecha / Hora:** Registro temporal de la interacción.
- **Paso / Fase:** Acápite de la monografía (ej. P1 Título, P2 Planteamiento, P4 Revisión MAB, P6 Discusión, P7 Conclusiones).
- **Prompt:** Instrucción exacta enviada a la IA.
- **Producto:** Archivo Markdown o Word modificado (`monografia_completa.md`, `Sources.xml`, `monografia.docx`).
- **Verificación Humana:** Ajustes realizados personalmente por el autor sobre la respuesta generada.
