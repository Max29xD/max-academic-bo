# Monografía de Compilación — EIP-FINOR-UAGRM (Bolivia)

Skill de agente para elaborar monografías de compilación de postgrado: Guía Institucional
EIP-FINOR-UAGRM 2025/2026, APA 7.ª, enfoque exclusivo en Bolivia, información verificada y
actualizada, ejecución en 11 pasos y auditoría automatizada.

Integra, sin depender de ellas:

- **docx** para Word profesional (la skill trae su propio generador institucional).
- **Tavily** (`tvly`) para búsquedas tipo Perplexity, extracción y research con citas.
- **word-bibliography** para bibliografía APA 7 y `Sources.xml` de Microsoft Word.

## Características e Integración Nativa

La skill es **100 % autocontenida y portable** para cualquier proyecto gracias a la incorporación de las capacidades clave de:

1. **DOCX profesional (Word):**
   - Ensamblado institucional con `scripts/generar_monografia_docx.py` sobre `templates/apa7ma.docx`.
   - Utilidades OOXML en `scripts/docx_utils.py`: validación contra esquemas XML (previene archivos corruptos), fusión de text runs fragmentados y extracción de texto a Markdown.
   - Guía técnica completa en `references/docx_guia.md`.

2. **Búsqueda académica tipo Perplexity (Tavily):**
   - `scripts/buscar_fuentes.py` opera tanto con el CLI oficial (`tvly`) como mediante conexión directa a la API REST de Tavily (`TAVILY_API_KEY`), sin librerías externas obligatorias.
   - Búsqueda profunda (`search`), investigación sintética multi-fuente (`research`) y extracción de contenido limpio (`extract`).
   - Registro automático de evidencia en `output/fuentes/*.json`.
   - Protocolo y embudo territorial en `references/tavily_busqueda.md` y `references/busqueda_bolivia.md`.

3. **Bibliografía Word APA 7 (word-bibliography):**
   - Generación de `Sources.xml` compatible con el esquema Office Open XML Bibliography mediante `scripts/word_bibliography.py` y `scripts/gestor_referencias.py`.
   - Importación directa en Microsoft Word (**Referencias → Administrar fuentes → Examinar...**).
   - Formateo estricto en Markdown APA 7.ª edición con sangría francesa y orden alfabético.
   - Guía de esquemas y tipos en `references/word_bibliography_guia.md`.

## Estructura

```text
.
├── skills/
│   └── monografia-compilacion-bolivia/   # ← paquete instalable completo
│       ├── SKILL.md                      # Instrucciones del agente (<500 líneas)
│       ├── references/                   # Guías: APA 7, reglas, Word OOXML, Tavily, bibliografía
│       ├── scripts/                      # Generadores, validador OOXML, búsqueda, bibliografía, auditor
│       ├── templates/                    # Plantilla Word oficial APA 7 (apa7ma.docx)
│       └── assets/                       # Logotipo oficial y catálogo de ejemplo
├── evals/                                # Suite de pruebas y benchmarks (desarrollo)
├── output/                               # Directorio de trabajo del usuario (generado en ejecución)
├── .gitignore                            # Exclusión limpia de archivos de entorno y temporales
└── README.md                             # Documentación
```

`output/` y `.agents/` **no forman parte** del paquete instalable: el CLI solo toma
`skills/monografia-compilacion-bolivia/`.

## Requisitos

- Python 3.10+ y `python-docx`.
- Opcional: `tvly` (Tavily CLI) para búsquedas y research.
- Opcional: skills `docx`, `word-bibliography` y `tavily-*`.

```bash
pip install python-docx
python skills/monografia-compilacion-bolivia/scripts/verificar_entorno.py
```

## Instalación con `bunx skills`

**Global** (disponible en todos los proyectos):

```bash
bunx skills add <owner>/<repo> --skill monografia-compilacion-bolivia -g -y
```

**Por proyecto** (queda en `.agents/skills` y se fija en `skills-lock.json`):

```bash
bunx skills add <owner>/<repo> --skill monografia-compilacion-bolivia -y
```

**Desde una copia local** (sin publicar el repo):

```bash
bunx skills add ./skills/monografia-compilacion-bolivia -g -y
```

> **Importante:** usa siempre `--skill monografia-compilacion-bolivia`. Sin ese filtro, el CLI
> también detecta las skills de desarrollo de `.agents/skills` (docx, pdf, pptx,
> word-bibliography) e intentaría instalarlas. No uses `--all` en este repo.

Verificar y mantener:

```bash
bunx skills list
bunx skills update monografia-compilacion-bolivia -y
```

Al instalar en otro proyecto, el CLI copia solo la carpeta de la skill. El agente la detecta por
`SKILL.md`; no hace falta configurar nada más.

### Skills compañeras (opcionales)

```bash
# Word avanzado (edición, control de cambios, PDF)
bunx skills add anthropics/skills --skill docx -g -y

# Tavily (búsqueda, extracción, research)
bunx skills add tavily-ai/skills -g -y
```

`word-bibliography` se instala desde la fuente que ya uses; si no está, el generador interno de la
monografía produce el mismo `Sources.xml`.

## Uso

Dentro del proyecto donde quieras trabajar:

```bash
cp -r <ruta-a-la-skill>/templates ./templates   # solo si quieres personalizar la plantilla
```

Pídele al agente, por ejemplo:

- «Hasta el paso 3: planteamiento y objetivos para una monografía sobre fintech en Santa Cruz».
- «Busca literatura 2024–2026 sobre inclusión financiera en Bolivia y arma la MAB».
- «Convierte estas referencias a APA 7 y genera `Sources.xml`».
- «Genera el `.docx` final y audítalo».

Artefactos en `./output/` (configurable con `MONOGRAFIA_OUTPUT`):

| Archivo | Contenido |
|---|---|
| `monografia_completa.md` | Manuscrito de trabajo |
| `monografia_compilacion_bolivia.docx` | Entregable Word |
| `referencias.json` | Catálogo verificado de fuentes |
| `referencias_bibliograficas.md` | Lista APA 7 + fichas |
| `Sources.xml` | Bibliografía para Word |
| `fuentes/*.json` | Evidencia de búsquedas (consulta, fecha, URLs) |

## Comandos útiles

```bash
# Diagnóstico
python skills/monografia-compilacion-bolivia/scripts/verificar_entorno.py

# Bibliografía (primera vez: catálogo de ejemplo)
python skills/monografia-compilacion-bolivia/scripts/gestor_referencias.py --init
python skills/monografia-compilacion-bolivia/scripts/gestor_referencias.py

# Word y auditoría
python skills/monografia-compilacion-bolivia/scripts/generar_monografia_docx.py
python skills/monografia-compilacion-bolivia/scripts/auditar_monografia.py output/monografia_completa.md --json

# Búsqueda con evidencia
python skills/monografia-compilacion-bolivia/scripts/buscar_fuentes.py "tema" --tipo search --rango-tiempo year
```

En PowerShell funciona igual, cambiando las barras si lo prefieres:
`python skills\monografia-compilacion-bolivia\scripts\verificar_entorno.py`.

## Solución de problemas

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: docx` | `pip install python-docx` |
| `tvly` no existe | Instálalo o usa la búsqueda web del agente (plan B documentado) |
| `research` pide login | `tvly login` (interactivo) o usa `search` + `extract` |
| `oauth_refresh_failed` | `tvly login` o `tvly logout` para volver al modo keyless |
| Word bloquea el `.docx` | Cierra Word; se genera `*_actualizada.docx` |
| El CLI instala todo el repo | Asegúrate de que exista `skills/monografia-compilacion-bolivia/SKILL.md` y no un `SKILL.md` en la raíz |
| El índice sale vacío | Usa los estilos Heading de la plantilla incluida |

## Desarrollo

- Reglas y checklist: `skills/monografia-compilacion-bolivia/references/reglas_institucionales.md`.
- Integraciones y planes B: `references/integraciones.md`.
- Validación del frontmatter: `skills-ref validate ./skills/monografia-compilacion-bolivia`
  (si tienes `skills-ref`).
- Los scripts históricos específicos del proyecto están en `archive/` y no se instalan.

## Licencias

Cada skill compañera conserva su licencia original (`docx`, `pdf`, `pptx` y `word-bibliography`
son propietarias; Tavily y `skill-creator` tienen las suyas). Esta skill no las copia: solo las
invoca si están presentes.
