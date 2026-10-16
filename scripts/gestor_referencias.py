#!/usr/bin/env python3
"""Gestor de referencias bibliográficas (APA 7.ª) para la monografía.

Es GENÉRICO: no trae fuentes incrustadas. Opera sobre `output/referencias.json`,
que el asistente construye con las fuentes REALES y verificadas de la sesión
(estado V de la MAB). Nunca inventa ni sobrescribe datos.

Subcomandos:
  --init              Crea output/referencias.json vacío (esquema documentado).
  --add '<json>'      Agrega una fuente al catálogo (objeto JSON o lista).
  --build             Compila output/referencias_bibliograficas.md y output/Sources.xml.
  --check             Valida el catálogo (campos, URLs/DOI, recencia, duplicados).

Campos de cada fuente (todos opcionales salvo id, autores/anio/titulo):
  id, tipo, autores, autores_cita, anio, titulo, fuente_publicacion,
  url, doi, pais, corte, datos_extraidos, formato_apa7

Si falta `formato_apa7`, se aproxima uno con `--auto-apa` (revisar antes de entregar).
"""
import argparse
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "vendor" / "word-bibliography"))
try:
    from word_bibliography import generate_word_bibliography_xml
except ImportError:  # pragma: no cover
    generate_word_bibliography_xml = None

REQUERIDOS = ["id", "anio", "titulo"]
TIPOS_WORD = {
    "articulo": "JournalArticle", "artículo": "JournalArticle", "journal": "JournalArticle",
    "libro": "Book", "book": "Book", "capitulo": "BookSection", "capítulo": "BookSection",
    "informe": "Report", "report": "Report", "regulatoria": "Report", "norma": "Report",
    "tesis": "Thesis", "thesis": "Thesis", "web": "WebSite", "sitio": "WebSite",
}


def _tipo_word(tipo: str) -> str:
    t = (tipo or "").lower()
    for k, v in TIPOS_WORD.items():
        if k in t:
            return v
    return "Report"


def _apa_aprox(f: dict) -> str:
    """Aproxima una referencia APA 7 desde los campos (revisar manualmente)."""
    autores = f.get("autores") or f.get("autores_cita") or "[Autor]"
    anio = f.get("anio") or "s. f."
    titulo = f.get("titulo") or "[Título]"
    fuente = f.get("fuente_publicacion") or ""
    url = f.get("url") or ""
    partes = [f"{autores} ({anio}). {titulo}."]
    if fuente:
        partes.append(f"*{fuente}*.")
    if url:
        partes.append(url)
    return " ".join(partes)


def leer_catalogo(data_file: Path):
    if not data_file.exists():
        print(f"✖ No existe {data_file}. Ejecuta primero: --init  (o --add ...)")
        sys.exit(2)
    with open(data_file, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):  # tolerar {"fuentes": [...]}
        data = data.get("fuentes", [])
    return data


def cmd_init(data_file: Path):
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if data_file.exists():
        print(f"ℹ Ya existe {data_file}; no se sobrescribe.")
        return
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    print(f"✔ Catálogo vacío creado en {data_file}. Agrega fuentes con --add '<json>'.")


def cmd_add(data_file: Path, nuevas):
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(nuevas, dict):
        nuevas = [nuevas]
    actuales = []
    if data_file.exists():
        with open(data_file, encoding="utf-8") as f:
            actuales = json.load(f)
        if isinstance(actuales, dict):
            actuales = actuales.get("fuentes", [])
    ids = {e.get("id") for e in actuales}
    agregadas = 0
    for n in nuevas:
        if n.get("id") in ids:
            print(f"⚠ ID duplicado, se omite: {n.get('id')}")
            continue
        actuales.append(n)
        agregadas += 1
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(actuales, f, ensure_ascii=False, indent=2)
    print(f"✔ {agregadas} fuente(s) agregada(s). Total: {len(actuales)}.")


def cmd_check(data_file: Path, year: int):
    fuentes = leer_catalogo(data_file)
    errores, avisos = [], []
    vistos = set()
    for i, f in enumerate(fuentes, 1):
        fid = f.get("id") or f"#{i}"
        for campo in REQUERIDOS:
            if not f.get(campo):
                errores.append(f"{fid}: falta el campo obligatorio '{campo}'.")
        if f.get("id") in vistos:
            errores.append(f"{fid}: ID duplicado.")
        vistos.add(f.get("id"))
        url = f.get("url") or ""
        if url and not re.match(r"^https?://", url):
            avisos.append(f"{fid}: la URL no usa http(s):// ({url[:40]}…).")
        if url and url.endswith("."):
            errores.append(f"{fid}: la URL/DOI termina en punto final (prohibido en APA 7).")
        if not f.get("formato_apa7"):
            avisos.append(f"{fid}: falta 'formato_apa7' (usa --auto-apa para aproximarlo).")
        if not f.get("pais"):
            avisos.append(f"{fid}: falta 'pais' (contexto geográfico).")
    anios = [int(f["anio"]) for f in fuentes if str(f.get("anio", "")).isdigit()]
    print("=" * 60)
    print(f"CATÁLOGO: {data_file} — {len(fuentes)} fuente(s)")
    if anios:
        lim = year - 5
        rec = sum(1 for a in anios if a >= lim)
        punta = sum(1 for a in anios if a >= year - 2)
        print(f"Recencia: {rec}/{len(anios)} ({100*rec/len(anios):.0f}%) en {lim}–{year} (meta ≥ 70%).")
        print(f"Vanguardia ({year-2}–{year}): {punta} fuente(s).")
    for e in errores:
        print(f"  ✖ {e}")
    for a in avisos:
        print(f"  ⚠ {a}")
    if not errores:
        print("  ✔ Sin errores objetivos.")
    if len(fuentes) < 5:
        print(f"  ✖ Solo {len(fuentes)} fuentes: el mínimo académico es 5 (meta 10–15).")
    print("=" * 60)
    return 1 if errores else 0


def cmd_build(data_file: Path, md_file: Path, xml_file: Path, auto_apa: bool):
    fuentes = leer_catalogo(data_file)
    if not fuentes:
        print("✖ El catálogo está vacío. Agrega fuentes reales antes de compilar.")
        sys.exit(2)
    if auto_apa:
        for f in fuentes:
            if not f.get("formato_apa7"):
                f["formato_apa7"] = _apa_aprox(f)

    def _clave_orden(f):
        # APA 7: orden alfabético por autor, luego por año. Nunca por la cadena
        # formateada completa (mala para autores compartidos).
        autor = (f.get("autores_cita") or f.get("autores") or "").lower()
        anio = str(f.get("anio", ""))
        return (autor, anio)

    ordenadas = sorted(fuentes, key=_clave_orden)

    md = [
        "# Registro de fuentes y referencias APA 7.ª",
        "## Monografía de compilación — EIP-FINOR-UAGRM",
        "",
        "> **Verificabilidad:** cada fuente fue consultada y validada en su fuente original. Cero invención bibliográfica.",
        "",
        "---",
        "",
        "### 1. Matriz de control de fuentes (MAB)",
        "",
        "| ID | Autor / Entidad | Año | Título | Tipo | Ámbito | Enlace |",
        "|:---:|---|:---:|---|---|:---:|:---:|",
    ]
    for f in ordenadas:
        url = f.get("url") or ""
        link = f"[ver]({url})" if url.startswith("http") else "—"
        titulo = (f.get("titulo") or "")[:60]
        md.append(f"| **{f.get('id','')}** | {f.get('autores_cita') or f.get('autores','')} | {f.get('anio','')} | {titulo} | {f.get('tipo','')} | {f.get('pais','')} | {link} |")

    md += ["", "---", "", "### 2. Fichas por fuente", ""]
    for f in ordenadas:
        md += [
            f"#### [{f.get('id','')}] {f.get('autores_cita') or f.get('autores','')} ({f.get('anio','')})",
            f"* **Título:** {f.get('titulo','')}",
            f"* **Tipo / ámbito:** {f.get('tipo','')} ({f.get('pais','')})",
            f"* **Editorial / entidad:** {f.get('fuente_publicacion','')}",
            f"* **Enlace:** {f.get('url','')}",
            f"* **Datos extraídos:** {f.get('datos_extraidos','')}",
            f"* **Referencia APA 7:** {f.get('formato_apa7','')}",
            "",
        ]

    md += ["---", "", "### 3. Referencias en APA 7.ª (listas para Word)", "",
           "*(orden alfabético, sangría francesa 1,27 cm)*", ""]
    for f in ordenadas:
        md.append((f.get("formato_apa7") or "") + "\n")

    md_file.parent.mkdir(parents=True, exist_ok=True)
    with open(md_file, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print(f"✔ Referencias Markdown en: {md_file}")

    if not generate_word_bibliography_xml:
        print("⚠ Módulo word-bibliography no disponible: se omitió Sources.xml.")
        return
    sources = []
    for f in ordenadas:
        src_type = _tipo_word(f.get("tipo", ""))
        url = f.get("url") or ""
        doi = f.get("doi") or ""
        if not doi and "doi.org/" in url:
            doi = url.split("doi.org/", 1)[1]
        item = {
            "tag": re.sub(r"[^A-Za-z0-9]", "", str(f.get("id", "Ref"))) or "Ref",
            "type": src_type,
            "title": f.get("titulo"),
            "year": str(f.get("anio", "")),
            "url": url,
            "doi": doi,
            "institution": f.get("fuente_publicacion") if src_type in ("Report", "Thesis") else None,
            "journal_name": f.get("fuente_publicacion") if src_type == "JournalArticle" else None,
            "site_name": f.get("fuente_publicacion") if src_type == "WebSite" else None,
            "publisher": f.get("fuente_publicacion") if src_type in ("Book", "BookSection") else None,
        }
        autores_raw = f.get("autores") or ""
        if re.search(r"\[.*?\]|^[A-ZÁÉÍÓÚ][\wáéíóú]+( \w+)+\.?\s*$", autores_raw) and "&" not in autores_raw:
            item["author_corporate"] = re.sub(r"\[.*?\]", "", autores_raw).strip()
        else:
            item["authors"] = [autores_raw] if autores_raw else []
        sources.append(item)
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    generate_word_bibliography_xml(sources, str(xml_file))
    print(f"✔ Sources.xml para Word en: {xml_file}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", default=str(BASE_DIR / "output"))
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--add", metavar="JSON")
    ap.add_argument("--add-file", metavar="RUTA", help="Archivo JSON (objeto o lista) con fuentes a agregar.")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--auto-apa", action="store_true", help="Aproxima formato_apa7 si falta (revisar).")
    ap.add_argument("--year", type=int, default=None)
    args = ap.parse_args()

    import datetime
    year = args.year or datetime.date.today().year
    outdir = Path(args.outdir)
    data_file = outdir / "referencias.json"

    if args.init:
        cmd_init(data_file)
    if args.add:
        cmd_add(data_file, json.loads(args.add))
    if args.add_file:
        cmd_add(data_file, json.loads(Path(args.add_file).read_text(encoding="utf-8")))
    if args.build:
        cmd_build(data_file, outdir / "referencias_bibliograficas.md", outdir / "Sources.xml", args.auto_apa)
    if args.check:
        sys.exit(cmd_check(data_file, year))
    if not (args.init or args.add or args.add_file or args.build or args.check):
        ap.print_help()


if __name__ == "__main__":
    main()
