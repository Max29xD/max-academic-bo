#!/usr/bin/env python3
"""Diagnóstico y configuración de capacidades de la skill.

Uso:
  python scripts/verificar_entorno.py [--json] [--setup]

Informa y configura:
- Python y dependencias (python-docx, lxml).
- Linter de prosa y anti-patrones de IA: Vale (con Scoop / PATH).
- Configuración y reglas estilísticas de Vale (.vale.ini + styles/Monografia).
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


def _vale() -> dict:
    exe = shutil.which("vale")
    info = {"disponible": bool(exe), "ruta": exe, "version": None}
    if exe:
        try:
            salida = subprocess.run([exe, "-v"], capture_output=True, text=True, timeout=10)
            info["version"] = (salida.stdout or salida.stderr).strip().splitlines()[0]
        except Exception:
            pass
    return info


def _scoop() -> dict:
    exe = shutil.which("scoop") or shutil.which("scoop.cmd") or shutil.which("scoop.ps1")
    return {"disponible": bool(exe), "ruta": str(exe) if exe else None}


def desplegar_estilos_vale() -> bool:
    """Copia la configuración de Vale (.vale.ini y styles/Monografia) al directorio de trabajo si no existen."""
    cwd = Path.cwd()
    ini_cwd = cwd / ".vale.ini"
    ini_skill = SKILL_ROOT / ".vale.ini"
    if not ini_cwd.exists() and ini_skill.exists():
        shutil.copy2(ini_skill, ini_cwd)

    styles_cwd = cwd / "styles" / "Monografia"
    styles_skill = SKILL_ROOT / "styles" / "Monografia"
    if not styles_cwd.exists() and styles_skill.exists():
        styles_cwd.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(styles_skill, styles_cwd, dirs_exist_ok=True)

    return (cwd / ".vale.ini").exists() and styles_cwd.exists()


def autoconfigurar() -> None:
    """Instala dependencias esenciales de Python, Vale (vía Scoop) y despliega estilos."""
    print("\n[Auto-Configuración y Verificación]")
    print("-" * 55)
    # 1. Dependencias Python
    deps_faltantes = []
    if not _version_paquete("docx"):
        deps_faltantes.append("python-docx")
    if not _version_paquete("lxml"):
        deps_faltantes.append("lxml")
    if deps_faltantes:
        print(f"📦 Instalando dependencias Python faltantes ({', '.join(deps_faltantes)})...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", *deps_faltantes], check=True)
            print("✔ Dependencias Python instaladas exitosamente.")
        except Exception as e:
            print(f"⚠ No se pudo instalar automáticamente: {e}. Ejecuta 'pip install python-docx lxml'.")
    else:
        print("✔ Dependencias Python esenciales verificadas.")

    # 2. Vale linter
    v = _vale()
    if not v["disponible"]:
        sc = _scoop()
        if sc["disponible"]:
            print("📦 Vale no detectado. Instalando automáticamente con Scoop ('scoop install vale')...")
            try:
                subprocess.run(["scoop", "install", "vale"], shell=True, check=True)
                v = _vale()
                if v["disponible"]:
                    print(f"✔ Vale instalado exitosamente: {v['version']}")
                else:
                    print("⚠ Scoop completó el comando; reinicia la consola o verifica PATH si no se detecta de inmediato.")
            except Exception as e:
                print(f"⚠ Error instalando Vale vía Scoop: {e}. Ejecuta manualmente: scoop install vale")
        else:
            print("ℹ Vale no está instalado y Scoop no fue detectado en PATH.")
            print("  Para instalar Vale en Windows:")
            print("  1. Con Scoop (recomendado): scoop install vale")
            print("  2. Con Chocolatey: choco install vale")
            print("  3. Con Winget: winget install errata-ai.vale")
    else:
        print(f"✔ Vale disponible: {v['version']} ({v['ruta']})")

    # 3. Despliegue de estilos .vale.ini y styles/Monografia
    desplegado = desplegar_estilos_vale()
    if desplegado:
        print("✔ Estilos y reglas anti-patrones de IA (.vale.ini + styles/Monografia) desplegados.")
    print("-" * 55)


def diagnosticar() -> dict:
    # Asegura estilos en cwd si la skill está presente
    desplegar_estilos_vale()

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
        "vale": _vale(),
        "scoop": _scoop(),
        "estilos_vale_ok": (Path.cwd() / ".vale.ini").exists() and (Path.cwd() / "styles" / "Monografia").exists(),
        "tavily": _tvly(),
        "skills_companeras": {k: (str(v) if v else None) for k, v in skills.items()},
    }


def principal() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="Salida JSON legible por máquina")
    ap.add_argument("--setup", "--auto-install", action="store_true", dest="setup",
                    help="Auto-instalar dependencias faltantes y configurar Vale y estilos")
    args = ap.parse_args()

    if args.setup:
        autoconfigurar()

    d = diagnosticar()

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
    else:
        print("Max Academic Bolivia — diagnóstico de entorno")
        print("=" * 55)
        print(f"Python            : {d['python']} ({d['ejecutable']})")
        print(f"Skill             : {d['skill_root']}")
        print(f"Salida            : {d['output_dir']}")
        print(f"Plantilla         : {'OK' if d['plantilla_ok'] else 'FALTA'} — {d['plantilla']}")
        print(f"Logo              : {d['logo'] or 'no encontrado (la carátula usará un marcador)'}")
        print("-" * 55)
        for nombre, version in d["dependencias"].items():
            print(f"{nombre:<18}: {version or 'NO INSTALADO'}")
        
        vl = d["vale"]
        vl_desc = f"{vl['version']} ({vl['ruta']})" if vl["disponible"] else "NO INSTALADO (opcional recomendado: scoop install vale)"
        print(f"{'Vale (Linter IA)':<18}: {vl_desc}")
        print(f"{'Reglas Monografia':<18}: {'✔ Configurado (.vale.ini + styles/Monografia)' if d['estilos_vale_ok'] else 'Falta desplegar'}")

        tv = d["tavily"]
        tv_desc = tv['version'] or ('CLI instalado' if tv['ruta'] else ('TAVILY_API_KEY activa' if tv.get('api_key') else 'NO DISPONIBLE'))
        print(f"{'Tavily / tvly':<18}: {tv_desc}")
        print("-" * 55)
        print("Capacidades incorporadas (nativas en la skill):")
        print("  ✔ docx_utils        : Validación OOXML, extracción de texto y fusión de runs")
        print("  ✔ word_bibliography : XML Sources.xml para Word y formateo APA 7")
        print("  ✔ gestor_referencias: Catálogo referencias.json -> Markdown + Sources.xml")
        print("  ✔ buscar_fuentes    : Búsqueda académica Tavily (CLI / API REST) + evidencia")
        print("  ✔ vale_linter       : Eliminación determinista de tics de IA (guiones largos, muletillas)")
        print("-" * 55)
        print("Skills compañeras detectadas en el entorno (refuerzos opcionales):")
        for nombre, ruta in d["skills_companeras"].items():
            print(f"  {nombre:<20}: {ruta or 'no detectada'}")
        print("-" * 55)
        if d["dependencias"]["python-docx"]:
            print("✔ Esencial disponible. La generación institucional de Word funcionará.")
        else:
            print("✖ Falta python-docx: ejecuta con '--setup' o haz 'pip install python-docx'")
        if not vl["disponible"]:
            print("ℹ Vale no detectado: ejecuta con '--setup' para instalar vía Scoop o haz 'scoop install vale'.")
        if not tv["disponible"]:
            print("ℹ Sin Tavily (CLI o TAVILY_API_KEY): usa la búsqueda web nativa del agente (ver references/tavily_busqueda.md).")
        print("✔ La skill es 100% autocontenida y funciona en cualquier proyecto.")

    return 0 if d["dependencias"]["python-docx"] else 2


if __name__ == "__main__":
    raise SystemExit(principal())
