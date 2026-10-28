"""Rutas portables de la skill.

La skill puede estar instalada en `.agents/skills`, en `~/.agents/skills` o en cualquier
otro directorio. Por eso:

- Los recursos de la skill (plantillas, logo) se resuelven desde `__file__`.
- Las salidas se resuelven desde el proyecto donde se ejecuta (`./output` por defecto),
  nunca dentro del directorio de instalación de la skill.
- `MONOGRAFIA_OUTPUT` permite fijar otra carpeta de salida.
"""

from __future__ import annotations

import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
TEMPLATES_DIR = SKILL_ROOT / "templates"
ASSETS_DIR = SKILL_ROOT / "assets"

NOMBRE_DOCX = "max_academic_bolivia.docx"


def output_dir(crear: bool = True) -> Path:
    """Carpeta de salida del proyecto actual (o la indicada en MAX_ACADEMIC_OUTPUT / MONOGRAFIA_OUTPUT)."""
    raw = (os.environ.get("MAX_ACADEMIC_OUTPUT") or os.environ.get("MONOGRAFIA_OUTPUT", "")).strip()
    base = Path(raw).expanduser() if raw else Path.cwd() / "output"
    if not base.is_absolute():
        base = (Path.cwd() / base).resolve()
    if crear:
        base.mkdir(parents=True, exist_ok=True)
    return base


def archivo_salida(nombre: str) -> Path:
    return output_dir() / nombre


def plantilla(nombre: str = "apa7ma.docx") -> Path:
    return TEMPLATES_DIR / nombre


def asset(nombre: str) -> Path:
    return ASSETS_DIR / nombre


def logo() -> Path | None:
    """Logo institucional: assets/logo.png o, por compatibilidad, output/logo.png."""
    for candidato in (ASSETS_DIR / "logo.png", output_dir(crear=False) / "logo.png"):
        if candidato.exists():
            return candidato
    return None


def buscar_skill(nombre: str) -> Path | None:
    """Localiza una skill compañera instalada, sin asumir una sola ubicación."""
    candidatos = [
        Path.cwd() / ".agents" / "skills" / nombre,
        Path.cwd() / ".claude" / "skills" / nombre,
        Path.cwd() / "skills" / nombre,
        SKILL_ROOT.parent / nombre,
        Path.home() / ".agents" / "skills" / nombre,
        Path.home() / ".claude" / "skills" / nombre,
        Path.home() / ".config" / "opencode" / "skills" / nombre,
    ]
    for candidato in candidatos:
        if candidato.is_dir():
            return candidato
    return None


def scripts_de_skill(nombre: str) -> Path | None:
    """Devuelve `<skill>/scripts` si la skill compañera está instalada."""
    ruta = buscar_skill(nombre)
    if ruta and (ruta / "scripts").is_dir():
        return ruta / "scripts"
    return None
