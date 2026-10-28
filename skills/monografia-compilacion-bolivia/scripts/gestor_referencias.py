#!/usr/bin/env python3
"""Gestor del catálogo de fuentes: JSON → Markdown APA 7 → `Sources.xml` para Word.

Uso:
  python scripts/gestor_referencias.py --init      # crea output/referencias.json de ejemplo
  python scripts/gestor_referencias.py             # regenera .md y Sources.xml
  python scripts/gestor_referencias.py --solo-md   # no toca Word

El catálogo es la única fuente de verdad: si una referencia no está verificada y anotada
aquí, no debe aparecer en el documento. Campos mínimos: titulo, anio, url (o doi).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import actualizar_sources_xml as asx  # noqa: E402
from rutas import ASSETS_DIR, archivo_salida  # noqa: E402


def _datos() -> list[dict]:
    ruta = archivo_salida("referencias.json")
    if not ruta.exists():
        raise SystemExit(
            f"No existe {ruta}.\n"
            "Créalo con: python scripts/gestor_referencias.py --init\n"
            "o copia tu catálogo real antes de regenerar."
        )
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(datos, dict):
        datos = datos.get("fuentes") or datos.get("sources") or datos.get("referencias") or []
    if not isinstance(datos, list) or not datos:
        raise SystemExit(f"{ruta} no contiene una lista de fuentes.")
    return datos


def inicializar(forzar: bool = False) -> Path:
    destino = archivo_salida("referencias.json")
    if destino.exists() and not forzar:
        print(f"ℹ Ya existe {destino}; no se sobrescribe (usa --forzar para reemplazarlo).")
        return destino
    ejemplo = ASSETS_DIR / "ejemplo_referencias.json"
    if not ejemplo.exists():
        raise SystemExit(f"Falta el ejemplo incluido en la skill: {ejemplo}")
    destino.write_text(ejemplo.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"✔ Catálogo de ejemplo creado en: {destino}")
    print("  Reemplaza las fuentes de ejemplo por las tuyas, verificadas, antes de citar.")
    return destino


def _autor_legible(f: dict) -> str:
    if f.get("autores_cita"):
        return str(f["autores_cita"])
    autores = f.get("autores") or f.get("authors")
    if isinstance(autores, str):
        return autores
    if isinstance(autores, list) and autores:
        primero = autores[0]
        if isinstance(primero, dict):
            return str(primero.get("last") or primero.get("apellido") or primero.get("nombre") or "Anónimo")
        return str(primero)
    return str(f.get("autor_corporativo") or "Anónimo")


def _apa(f: dict) -> str:
    if f.get("formato_apa7"):
        return str(f["formato_apa7"]).strip()
    # Construcción mínima cuando no hay cadena APA explícita.
    autor = _autor_legible(f)
    anio = f.get("anio") or f.get("year") or "s. f."
    titulo = f.get("titulo") or f.get("title") or "(sin título)"
    url = f.get("url") or ""
    if f.get("doi") and not str(f["doi"]).startswith("http"):
        url = f"https://doi.org/{str(f['doi']).lstrip('doi:').strip()}"
    return f"{autor}. ({anio}). *{titulo}*. {url}".strip()


def generar_markdown(fuentes: list[dict]) -> Path:
    lineas = [
        "# Registro de fuentes y referencias APA 7.ª",
        "",
        "> Generado desde `referencias.json`. Cada entrada debe haber sido abierta y verificada",
        "> en su fuente original. Las dudas se marcan `[VERIFICAR]`; no se inventan metadatos.",
        "",
        "---",
        "",
        "## 1. Control de fuentes (base para la MAB)",
        "",
        "| ID | Autor / Entidad | Año | Título | Tipo | Ámbito | Enlace |",
        "|:---:|---|:---:|---|---|:---:|---|",
    ]
    for i, f in enumerate(fuentes, 1):
        fid = f.get("id") or f"S{i:02d}"
        anio = f.get("anio") or f.get("year") or "s. f."
        titulo = str(f.get("titulo") or f.get("title") or "(sin título)")
        tipo = f.get("tipo") or f.get("tipo_documento") or "—"
        ambito = f.get("pais") or f.get("ambito") or "—"
        url = str(f.get("url") or "")
        enlace = f"[Ver fuente]({url})" if url.startswith("http") else (url or "—")
        lineas.append(
            f"| **{fid}** | {_autor_legible(f)} | {anio} | *{titulo[:60]}* | {tipo} | {ambito} | {enlace} |"
        )

    lineas += ["", "---", "", "## 2. Fichas de detalle", ""]
    for i, f in enumerate(fuentes, 1):
        fid = f.get("id") or f"S{i:02d}"
        lineas += [
            f"### [{fid}] {_autor_legible(f)} ({f.get('anio') or f.get('year') or 's. f.'})",
            f"- **Título:** {f.get('titulo') or f.get('title') or '(sin título)'}",
            f"- **Tipo:** {f.get('tipo') or f.get('tipo_documento') or '—'}",
            f"- **Publicación:** {f.get('fuente_publicacion') or f.get('revista') or f.get('editorial') or '—'}",
        ]
        if f.get("url"):
            lineas.append(f"- **URL:** [{f['url']}]({f['url']})")
        if f.get("doi"):
            lineas.append(f"- **DOI:** {f['doi']}")
        if f.get("datos_extraidos"):
            lineas.append(f"- **Datos extraídos:** {f['datos_extraidos']}")
        if f.get("verificado"):
            lineas.append(f"- **Verificado:** {f['verificado']}")
        lineas += ["- **APA 7:**", f"  > {_apa(f)}", ""]

    lineas += ["---", "", "## 3. Lista de referencias (APA 7.ª, orden alfabético)", ""]
    for f in sorted(fuentes, key=lambda x: _apa(x).lower()):
        lineas.append(f"{_apa(f)}\n")

    destino = archivo_salida("referencias_bibliograficas.md")
    destino.write_text("\n".join(lineas), encoding="utf-8")
    print(f"✔ Markdown APA 7 generado en: {destino}")
    return destino


def generar_word(fuentes: list[dict], solo_xml: bool = True, sync_global: bool = False) -> Path:
    xml_bytes = asx.build_xml(fuentes)
    destino = asx.update_sources_xml(xml_bytes, sync_global=sync_global)
    if not solo_xml:
        asx.embed_in_docx(xml_bytes)
    return destino


def principal() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", action="store_true", help="Crear output/referencias.json desde el ejemplo")
    ap.add_argument("--forzar", action="store_true", help="Con --init, sobrescribir el catálogo existente")
    ap.add_argument("--solo-md", action="store_true", help="Generar solo el Markdown, sin Sources.xml")
    ap.add_argument("--incrustar", action="store_true", help="Incrustar la bibliografía en el DOCX si existe")
    ap.add_argument("--sync-word-global", action="store_true", help="Actualizar la lista maestra global de Word")
    args = ap.parse_args()

    if args.init:
        inicializar(args.forzar)

    fuentes = _datos()
    generar_markdown(fuentes)
    if not args.solo_md:
        generar_word(fuentes, solo_xml=not args.incrustar, sync_global=args.sync_word_global)
    print(f"✔ {len(fuentes)} fuentes procesadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
