# max-academic-bo

Skill de agente para elaborar **monografías de compilación** (revisión documental de postgrado)
de la **EIP-FINOR-UAGRM** (Bolivia, Taller de Grado), bajo la Guía Institucional y las
**Normas APA 7.ª edición**, con enfoque territorial **exclusivo en Bolivia** y fuentes
**reales, verificadas y actualizadas**.

Este repositorio **es la skill**: la carpeta raíz contiene el `SKILL.md` y sus recursos, lista
para copiarse tal cual dentro del directorio de skills de cualquier harness o agente.

```
max-academic-bo/
├── SKILL.md                     # entrada de la skill (frontmatter + flujo P0–P11)
├── references/                  # reglas, búsqueda, APA 7, plantillas por paso
├── scripts/                     # auditoría, consultas, gestor de referencias, generador .docx
├── templates/apa7ma.docx        # plantilla Word oficial (carátula + numeración de estilos)
└── vendor/word-bibliography/    # generador de Sources.xml (referencias) para Word
```

## Qué hace

- Ejecuta la monografía **paso a paso** (P0–P11) y **se detiene exactamente donde le indiques**
  ("hasta el paso 3", "solo el eje 2", "solo buscar fuentes", "audita mi borrador").
- **Cero invención bibliográfica**: toda fuente, DOI y cifra sale de una búsqueda real y abierta.
- Búsqueda con **embudo geográfico boliviano** (local → departamental → nacional → regional → global)
  y fuentes priorizadas (SciELO Bolivia, Redalyc, Latindex, repositorios, INE Censo 2024, BCB, ASFI, CEPAL…).
- Verifica el texto con un **auditor** contra reglas con ID (TIT, PRO, OBJ, REV, DIS, CON, RES, REF…).
- Ensambla el **`.docx` final** sobre la plantilla oficial (carátula, índice, referencias APA 7).

## Requisitos

- Python 3.8+.
- `python-docx` para generar el `.docx`: `pip install python-docx`.
- Una herramienta de búsqueda web y otra de lectura/fetch (las que ofrezca tu harness).

## Instalación

### Opción A — CLI de `skills` (skills.sh) ⭐

Este repositorio ya es instalable con el CLI oficial del ecosistema (`npx skills` / `bunx skills`),
porque la **raíz contiene un `SKILL.md`** (el CLI descubre la skill a nivel raíz):

```bash
# Ver qué skills trae el repo, sin instalar
npx skills add https://github.com/Max29xD/max-academic-bo --list

# Instalar (global, en tu usuario)
npx skills add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo -g -y

# Equivalente con bun
bunx skills@latest add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo -g -y

# Instalar solo en harness concretos
npx skills add Max29xD/max-academic-bo --skill max-academic-bo -a claude-code -a opencode
```

El repositorio es **privado**: el CLI usa tus credenciales de Git / GitHub CLI / SSH ya configuradas.
Si lo haces público, cualquiera podrá instalarlo igual y aparecerá en [skills.sh](https://skills.sh/).

### Opción B — manual (copiar la carpeta)

Copia toda la carpeta dentro del directorio de skills de tu harness, con el nombre `max-academic-bo`.
Rutas típicas:

| Harness | Ámbito | Ruta |
|---|---|---|
| **Claude Code** | personal | `~/.claude/skills/max-academic-bo/` |
| **Claude Code** | proyecto | `<proyecto>/.claude/skills/max-academic-bo/` |
| **OpenCode** | global | `~/.config/opencode/skills/max-academic-bo/` |
| **OpenCode** | proyecto | `<proyecto>/.opencode/skills/max-academic-bo/` |
| **Otros (agents)** | genérico | `<dir-de-skills>/max-academic-bo/` |

La skill se activa sola por su `description` (menciones de monografía, taller de grado, EIP, FINOR,
UAGRM, APA 7, revisión literaria, planteamiento del problema, objetivos, carátula, buscar fuentes de
Bolivia, etc.), aunque no la nombres.

### Ejemplo (Windows / PowerShell)

```powershell
# OpenCode, global
Copy-Item -Recurse -Force ".\max-academic-bo" "$env:USERPROFILE\.config\opencode\skills\max-academic-bo"

# Claude Code, personal
Copy-Item -Recurse -Force ".\max-academic-bo" "$env:USERPROFILE\.claude\skills\max-academic-bo"
```

## Uso rápido (dentro de la skill)

```bash
# Buscar literatura (genera cadenas booleanas y consultas por embudo)
python scripts/generar_consultas.py --grupo "comercio electrónico|e-commerce|MyPE" --desde 2021 --hasta 2026

# Auditar un borrador (.md / .txt / .docx)
python scripts/auditar_monografia.py borrador.md --parcial --year 2026
python scripts/auditar_monografia.py monografia.docx --titulo "…" --year 2026 --json

# Mantener y compilar referencias (APA 7 + Sources.xml para Word)
python scripts/gestor_referencias.py --output output --init
python scripts/gestor_referencias.py --output output --add-file fuentes.json --auto-apa
python scripts/gestor_referencias.py --output output --check
python scripts/gestor_referencias.py --output output --build

# Ensamblar el documento final .docx sobre la plantilla oficial
python scripts/generar_monografia_docx.py \
  --input output/monografia.md --references output/referencias.json \
  --caratula output/caratula.json --out output/monografia.docx
```

Todos los artefactos generados van a `output/` (se crea automáticamente).

## Estructura del flujo

P1 Título · P2 Planteamiento · P3 Objetivos · P4 Revisión · P5 Términos · P6 Discusión ·
P7 Conclusiones · P8 Introducción · P9 Resumen · P10 Título final y Referencias · P11 Formales.

El detalle de reglas, búsqueda, formato APA y plantillas está en `references/`.

> **Nota:** la carpeta `datos/` (apuntes de trabajo) y `.agents/` (herramientas de desarrollo) están
> excluidas de git en `.gitignore`; no forman parte de la skill instalable.
