#!/usr/bin/env python3
"""Diagnóstico y configuración obligatoria de capacidades de la skill.

Uso:
  python scripts/verificar_entorno.py [--json] [--setup]

Informa y configura:
- Python y dependencias críticas (python-docx, lxml, tavily-cli).
- Estado de autenticación de Tavily (CLI `tvly` o TAVILY_API_KEY).
- Linter de prosa y anti-patrones de IA: Vale (con Scoop / PATH).
- Configuración y reglas estilísticas de Vale (.vale.ini + styles/Monografia).
- Skills compañeras instaladas (docx, word-bibliography, tavily-*).
- Rutas efectivas de salida, plantilla y logo.

Política de parada estricta (Gatekeeper):
Códigos de salida:
  0 = Todo lo esencial está verificado y autenticado.
  2 = Falta un prerrequisito obligatorio (python-docx o autenticación de Tavily).
      SE DETIENE LA EJECUCIÓN hasta que se configure.
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
    api_key_env = bool(os.environ.get("TAVILY_API_KEY", "").strip())
    config_file = Path.home() / ".tavily" / "config.json"
    config_has_key = False
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                config_has_key = bool(data.get("api_key") or data.get("token"))
        except Exception:
            pass

    auth_ok = False
    version = None
    if exe:
        try:
            res = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10)
            version = (res.stdout or res.stderr).strip().splitlines()[0]
        except Exception:
            pass
        try:
            res = subprocess.run([exe, "auth", "--json"], capture_output=True, text=True, timeout=8)
            if res.returncode == 0:
                auth_data = json.loads(res.stdout)
                auth_ok = bool(auth_data.get("authenticated", False))
        except Exception:
            pass
    elif api_key_env:
        auth_ok = True

    if not auth_ok and config_has_key:
        auth_ok = True

    return {
        "disponible": bool(exe or api_key_env or config_has_key),
        "autenticado": auth_ok,
        "ruta": exe,
        "version": version,
        "api_key_env": api_key_env,
        "config_file": config_has_key,
    }


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
    """Instala dependencias esenciales de Python (python-docx, lxml, tavily-cli), Vale (vía Scoop) y despliega estilos."""
    print("\n[Auto-Configuración y Verificación de Herramientas]")
    print("-" * 58)
    
    # 1. Dependencias Python
    deps_faltantes = []
    if not _version_paquete("docx"):
        deps_faltantes.append("python-docx")
    if not _version_paquete("lxml"):
        deps_faltantes.append("lxml")
    if not shutil.which("tvly"):
        deps_faltantes.append("tavily-cli")

    if deps_faltantes:
        print(f"📦 Instalando paquetes faltantes: {', '.join(deps_faltantes)}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", *deps_faltantes], check=True)
            print("✔ Paquetes instalados exitosamente.")
        except Exception as e:
            print(f"⚠ Error instalando paquetes: {e}. Ejecuta: pip install python-docx lxml tavily-cli")
    else:
        print("✔ Dependencias Python esenciales y Tavily CLI verificadas.")

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
                    print("⚠ Scoop completó el comando; reinicia la consola o verifica PATH si no se detecta.")
            except Exception as e:
                print(f"⚠ Error instalando Vale vía Scoop: {e}. Ejecuta: scoop install vale")
        else:
            print("ℹ Vale no detectado en PATH. Instalación sugerida:")
            print("  - Con Scoop: scoop install vale")
            print("  - Con Winget: winget install errata-ai.vale")
            print("  - Con Choco:  choco install vale")
    else:
        print(f"✔ Vale disponible: {v['version']} ({v['ruta']})")

    # 3. Despliegue de estilos .vale.ini y styles/Monografia
    desplegado = desplegar_estilos_vale()
    if desplegado:
        print("✔ Reglas y estilos de Vale (.vale.ini + styles/Monografia) desplegados.")
    print("-" * 58)


def diagnosticar() -> dict:
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
                    help="Auto-instalar dependencias faltantes y configurar herramientas")
    args = ap.parse_args()

    if args.setup:
        autoconfigurar()

    d = diagnosticar()

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        docx_ok = bool(d["dependencias"]["python-docx"])
        tvly_ok = bool(d["tavily"]["autenticado"])
        return 0 if (docx_ok and tvly_ok) else 2

    print("Max Academic Bolivia — Diagnóstico de Entorno y Prerrequisitos")
    print("=" * 62)
    print(f"Python            : {d['python']} ({d['ejecutable']})")
    print(f"Skill             : {d['skill_root']}")
    print(f"Salida            : {d['output_dir']}")
    print(f"Plantilla Word    : {'✔ OK' if d['plantilla_ok'] else '✖ FALTA'} — {d['plantilla']}")
    print(f"Logo Institucional: {d['logo'] or 'no encontrado (la carátula usará un marcador)'}")
    print("-" * 62)
    
    for nombre, version in d["dependencias"].items():
        estado = f"✔ {version}" if version else "✖ NO INSTALADO (Obligatorio)"
        print(f"{nombre:<18}: {estado}")

    tv = d["tavily"]
    if tv["autenticado"]:
        tv_estado = f"✔ Autenticado y Operativo ({tv['version'] or 'tvly'})"
    elif tv["disponible"]:
        tv_estado = "⚠ Instalado pero NO Autenticado (Falta API key)"
    else:
        tv_estado = "✖ NO INSTALADO NI CONFIGURADO (Obligatorio)"
    print(f"{'Tavily (Búsqueda)':<18}: {tv_estado}")

    vl = d["vale"]
    vl_desc = f"✔ {vl['version']}" if vl["disponible"] else "ℹ No instalado (Recomendado: scoop install vale)"
    print(f"{'Vale (Linter IA)':<18}: {vl_desc}")
    print(f"{'Reglas Monografía':<18}: {'✔ .vale.ini + styles/Monografia OK' if d['estilos_vale_ok'] else '⚠ Falta desplegar'}")
    print("-" * 62)
    
    docx_ok = bool(d["dependencias"]["python-docx"])
    tvly_ok = bool(tv["autenticado"])

    if docx_ok and tvly_ok:
        print("✔ TODOS LOS PRERREQUISITOS OBLIGATORIOS ESTÁN VERIFICADOS.")
        print("  Puede continuar con la investigación y redacción con total garantía metodológica.")
        print("=" * 62)
        return 0

    print("\n" + "!" * 62)
    print("⛔ PARADA OBLIGATORIA (GATEKEEPER): PRERREQUISITOS INCOMPLETOS")
    print("!" * 62)
    print("Para garantizar el rigor académico y la regla de CERO INVENCIÓN,")
    print("NO SE DEBE CONTINUAR sin las herramientas verificadas.")
    print("\nAcciones requeridas para corregir:")

    if not docx_ok:
        print("  1. Instalar dependencias Python:")
        print("     pip install python-docx lxml")
    
    if not tv["disponible"]:
        print("  2. Instalar Tavily CLI:")
        print("     pip install tavily-cli")

    if not tvly_ok:
        print("  3. Autenticar Tavily (obligatorio para rastreo de fuentes indexadas):")
        print("     Ejecuta: tvly login --api-key <TU_API_KEY>")
        print("     O define la variable de entorno:")
        print("       - PowerShell:  $env:TAVILY_API_KEY=\"tvly-...\"")
        print("       - CMD:         set TAVILY_API_KEY=tvly-...")
        print("       - Bash/Linux:  export TAVILY_API_KEY=\"tvly-...\"")
        print("     * Si no tienes clave, solicítala o pídele al asistente que la configure por ti.")

    print("\nO ejecuta el comando de auto-reparación:")
    print("     python scripts/verificar_entorno.py --setup")
    print("!" * 62 + "\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(principal())
