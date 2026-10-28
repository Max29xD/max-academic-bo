#!/usr/bin/env python3
"""Diagnóstico de capacidades de la skill (sin instalar nada).

Uso:
  python scripts/verificar_entorno.py [--json]

Informa:
- Python y dependencias (python-docx, lxml).
- Tavily CLI (`tvly`) y si hay sesión/API key.
- Skills compañeras instaladas (docx, word-bibliography, tavily-*).
- Rutas efectivas de salida, plantilla y logo.

Códigos de salida: 0 = todo lo esencial disponible; 2 = falta algo esencial
(python-docx). Las carencias opcionales no bloquean.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import SKILL_ROOT, buscar_skill, logo, output_dir, plantilla  # noqa: E402


def _version_paquete(nombre: str) -> str | None:
    try:
        modulo = __import__(nombre)
        return getattr(modulo, "__version__", "instalado")
    except Exception:
        return None


def _tvly() -> dict:
    exe = shutil.which("tvly")
    api_key_set = bool(os.environ.get("TAVILY_API_KEY", "").strip())
    info = {"disponible": bool(exe or api_key_set), "ruta": exe, "version": None, "api_key": api_key_set}
    if exe:
        try:
            salida = subprocess.run(
                [exe, "--version"], capture_output=True, text=True, timeout=15
            )
            info["version"] = (salida.stdout or salida.stderr).strip().splitlines()[0]
        except Exception:
            pass
    return info


def diagnosticar() -> dict:
    skills = {
        "docx": buscar_skill("docx"),
        "word-bibliography": buscar_skill("word-bibliography"),
        "tavily-search": buscar_skill("tavily-search"),
        "tavily-research": buscar_skill("tavily-research"),
        "tavily-extract": buscar_skill("tavily-extract"),
    }
    return {
        "python": sys.version.split()[0],
        "ejecutable": sys.executable,
        "skill_root": str(SKILL_ROOT),
        "output_dir": str(output_dir(crear=False)),
        "plantilla": str(plantilla()),
        "plantilla_ok": plantilla().exists(),
        "logo": str(logo()) if logo() else None,
        "dependencias": {
            "python-docx": _version_paquete("docx"),
            "lxml": _version_paquete("lxml"),
        },
        "tavily": _tvly(),
        "skills_companeras": {k: (str(v) if v else None) for k, v in skills.items()},
    }


def principal() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="Salida JSON legible por máquina")
    args = ap.parse_args()
    d = diagnosticar()

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        print("Monografía de compilación — diagnóstico de entorno")
        print("=" * 55)
        print(f"Python            : {d['python']} ({d['ejecutable']})")
        print(f"Skill             : {d['skill_root']}")
        print(f"Salida            : {d['output_dir']}")
        print(f"Plantilla         : {'OK' if d['plantilla_ok'] else 'FALTA'} — {d['plantilla']}")
        print(f"Logo              : {d['logo'] or 'no encontrado (la carátula usará un marcador)'}")
        print("-" * 55)
        for nombre, version in d["dependencias"].items():
            print(f"{nombre:<18}: {version or 'NO INSTALADO'}")
        tv = d["tavily"]
        tv_desc = tv['version'] or ('CLI instalado' if tv['ruta'] else ('TAVILY_API_KEY activa' if tv.get('api_key') else 'NO DISPONIBLE'))
        print(f"{'Tavily / tvly':<18}: {tv_desc}")
        print("-" * 55)
        print("Capacidades incorporadas (nativas en la skill):")
        print("  ✔ docx_utils        : Validación OOXML, extracción de texto y fusión de runs")
        print("  ✔ word_bibliography : XML Sources.xml para Word y formateo APA 7")
        print("  ✔ gestor_referencias: Catálogo referencias.json -> Markdown + Sources.xml")
        print("  ✔ buscar_fuentes    : Búsqueda académica Tavily (CLI / API REST) + evidencia")
        print("-" * 55)
        print("Skills compañeras detectadas en el entorno (refuerzos opcionales):")
        for nombre, ruta in d["skills_companeras"].items():
            print(f"  {nombre:<20}: {ruta or 'no detectada'}")
        print("-" * 55)
        if d["dependencias"]["python-docx"]:
            print("✔ Esencial disponible. La generación institucional de Word funcionará.")
        else:
            print("✖ Falta python-docx: pip install python-docx")
        if not tv["disponible"]:
            print("ℹ Sin Tavily (CLI o TAVILY_API_KEY): usa la búsqueda web nativa del agente (ver references/tavily_busqueda.md).")
        print("✔ La skill es 100% autocontenida y funciona en cualquier proyecto.")

    return 0 if d["dependencias"]["python-docx"] else 2


if __name__ == "__main__":
    raise SystemExit(principal())
