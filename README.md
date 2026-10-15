<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/header/graph.svg?title=max-academic-bo&subtitle=Monograf%C3%ADas%20de%20compilaci%C3%B3n%20%C2%B7%20APA%207.%C2%AA%20%C2%B7%20Bolivia&mode=dark" />
    <img alt="max-academic-bo — monografías de compilación · APA 7.ª · Bolivia" src="https://shieldcn.dev/header/graph.svg?title=max-academic-bo&subtitle=Monograf%C3%ADas%20de%20compilaci%C3%B3n%20%C2%B7%20APA%207.%C2%AA%20%C2%B7%20Bolivia&mode=light" />
  </picture>
</p>

<p align="center">
  <img alt="Agent Skill compatible" src="https://shieldcn.dev/badge/Agent%20Skill-compatible-18181b.svg?variant=secondary" />
  <img alt="APA 7.ª obligatoria" src="https://shieldcn.dev/badge/APA%207.%C2%AA-obligatoria-1d4ed8.svg?variant=secondary" />
  <img alt="Bolivia, enfoque exclusivo" src="https://shieldcn.dev/badge/Bolivia-enfoque%20exclusivo-16a34a.svg?variant=secondary" />
  <img alt="EIP FINOR UAGRM, guía institucional" src="https://shieldcn.dev/badge/EIP%20FINOR%20UAGRM-gu%C3%ADa%20institucional-7c3aed.svg?variant=secondary" />
  <img alt="Python 3.8+" src="https://shieldcn.dev/badge/Python-3.8%2B-3776ab.svg?logo=python" />
</p>

Skill de agente para elaborar **monografías de compilación** (EIP-FINOR-UAGRM, Bolivia, Taller de Grado)
bajo la guía institucional y las **normas APA 7.ª**, con enfoque territorial **exclusivo en Bolivia**,
**fuentes reales y verificadas** (cero invención) y control exacto del alcance paso a paso (P0–P11).

## Instalación

```bash
npx  skills add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo
bunx skills add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo
pnpx skills add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo
```

Usa la que tengas. Con `-g` se instala global (en tu usuario) y con `-y` se omiten las confirmaciones:

```bash
npx skills add https://github.com/Max29xD/max-academic-bo --skill max-academic-bo -g -y
```

## Requisitos

- **Python 3.8+**
- `python-docx` para generar el `.docx`: `pip install python-docx`
- Una herramienta de búsqueda web y otra de fetch (las del harness)

## Estructura

```
max-academic-bo/
├── SKILL.md                  # entrada de la skill (flujo P0–P11)
├── references/               # reglas, búsqueda Bolivia, APA 7, plantillas por paso
├── scripts/                  # auditar · consultas · referencias · generar .docx
├── templates/apa7ma.docx     # plantilla Word oficial
└── vendor/                   # generador de Sources.xml
```

## Creador

**Marcos Leandro Bonilla Borges** · [@Max29xD](https://github.com/Max29xD) · [maxcoding.pages.dev](https://maxcoding.pages.dev)
