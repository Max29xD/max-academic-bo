<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://shieldcn.dev/header/gradient.svg?title=Max%20Academic%20Bo%20-%20Agent%20Skill&subtitle=Monograf%C3%ADas%20de%20compilaci%C3%B3n%20%C2%B7%20APA%207.%C2%AA%20%C2%B7%20Bolivia&logo=googlescholar&mode=dark" />
    <img alt="max-academic-bo — monografías de compilación · APA 7.ª · Bolivia" src="https://shieldcn.dev/header/gradient.svg?title=Max%20Academic%20Bo%20-%20Agent%20Skill&subtitle=Monograf%C3%ADas%20de%20compilaci%C3%B3n%20%C2%B7%20APA%207.%C2%AA%20%C2%B7%20Bolivia&logo=googlescholar&mode=light" />
  </picture>
</p>

<p align="center">
  <img alt="Agent Skill compatible" src="https://shieldcn.dev/badge/Agent%20Skill-compatible-18181b.svg?variant=secondary" />
  <img alt="APA 7.ª obligatoria" src="https://shieldcn.dev/badge/APA%207.%C2%AA-obligatoria-1d4ed8.svg?variant=secondary" />
  <img alt="Bolivia, enfoque exclusivo" src="https://shieldcn.dev/badge/Bolivia-enfoque%20exclusivo-16a34a.svg?variant=secondary" />
  <img alt="EIP FINOR UAGRM, guía institucional" src="https://shieldcn.dev/badge/EIP%20FINOR%20UAGRM-gu%C3%ADa%20institucional-7c3aed.svg?variant=secondary" />
  <img alt="Python 3.8+" src="https://shieldcn.dev/badge/Python-3.8%2B-3776ab.svg?logo=python" />
</p>

<p align="center">
  Elabora <b>monografías de compilación</b> de la EIP-FINOR-UAGRM (Bolivia, Taller de Grado) bajo la<br/>
  guía institucional y las <b>normas APA 7.ª</b>, con enfoque <b>exclusivo en Bolivia</b> y<br/>
  fuentes <b>reales y verificadas</b> (cero invención), paso a paso y con control exacto del alcance.
</p>

## ✨ Qué hace

- Ejecuta la monografía **paso a paso** (P0–P11) y **se detiene exactamente donde le indiques**.
- **Cero invención bibliográfica**: cada fuente, DOI y cifra sale de una búsqueda real y abierta.
- Búsqueda con **embudo geográfico boliviano** (local → departamental → nacional → regional → global).
- **Auditor** automático contra reglas con ID (TIT, PRO, OBJ, REV, DIS, CON, RES, REF…).
- Ensambla el **`.docx` final** sobre la plantilla oficial (carátula, índice, referencias APA 7).

## 🚀 Instalación

```bash
npx skills add https://github.com/max29xd/max-academic-bo --skill max-academic-bo
bunx skills add https://github.com/max29xd/max-academic-bo --skill max-academic-bo
pnpx skills add https://github.com/max29xd/max-academic-bo --skill max-academic-bo
```

Usa la que tengas. Añade `-g` para instalar global (en tu usuario) y `-y` para omitir confirmaciones:

```bash
npx skills add https://github.com/max29xd/max-academic-bo --skill max-academic-bo -g -y
```

## 🤖 Cómo se usa en el agente

Se activa **sola** (por su `description`): basta con hablar de tu monografía. Después la diriges en
lenguaje natural y se detiene donde se lo pidas:

| Le pides… | Hace… |
|---|---|
| `Hazme la monografía completa` | Ejecuta P1–P11 y va parando en cada control |
| `Solo el planteamiento del problema` | Entrega únicamente el paso 2, con datos oficiales de Bolivia |
| `Hasta el paso 3` | Ejecuta P1–P3 y se detiene |
| `Solo buscar fuentes` | Búsqueda real + verificación y matriz de análisis bibliográfico |
| `Solo el eje 2` | Redacta una sola sección de la revisión literaria |
| `Audita mi borrador` | Revisa tu texto y te dice exactamente qué incumple |
| `Genera el .docx` | Ensambla el documento final sobre la plantilla oficial |

## 📦 Requisitos

- **Python 3.8+**
- `python-docx` para el `.docx`: `pip install python-docx`
- Una herramienta de búsqueda web y otra de fetch (las del harness)

## 🗂 Estructura

```
max-academic-bo/
├── SKILL.md                  # entrada de la skill (flujo P0–P11)
├── references/               # reglas, búsqueda Bolivia, APA 7, plantillas por paso
├── scripts/                  # auditar · consultas · referencias · generar .docx
├── tests/                    # pruebas de regresión del auditor
├── templates/apa7ma.docx     # plantilla Word oficial
└── vendor/                   # generador de Sources.xml
```

## 👨‍💻 Autor

<p>
  <a href="https://github.com/max29xd">
    <img src="https://avatars.githubusercontent.com/u/85517789?v=4" width="104" height="104" alt="Marcos Leandro Bonilla Borges" />
  </a>
</p>

<p>
  <b>MaxCoding</b> •
  <i>Fullstack & System Engineer · UI/UX Designer</i>
</p>

<p>
  <a href="https://maxcoding.pages.dev/"><img src="https://shieldcn.dev/badge/Portfolio-maxcoding.pages.dev-10b981.svg?logo=cloudflarepages&variant=secondary" alt="Portfolio" /></a>
  <a href="https://github.com/max29xd"><img src="https://shieldcn.dev/badge/GitHub-Max29xD-181717.svg?logo=github&variant=secondary" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/maxcoding"><img src="https://shieldcn.dev/badge/LinkedIn-MaxCoding-0a66c2.svg?logo=linkedin&variant=secondary" alt="LinkedIn" /></a>
  <a href="mailto:marcos291198@gmail.com"><img src="https://shieldcn.dev/badge/Email-marcos291198@gmail.com-ea4335.svg?logo=gmail&variant=secondary" alt="Email" /></a>
</p>
