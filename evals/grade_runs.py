#!/usr/bin/env python3
"""Califica las corridas de `evals/iteration-N` y escribe grading.json por corrida.

No sustituye la revisión humana: automatiza lo objetivo (archivos, XML, conteos,
marcadores) y deja evidencia textual para que el revisor juzgue lo cualitativo.

Uso:
  python evals/grade_runs.py evals/iteration-1
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"b": "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"}
CONFIGS = ("with_skill", "old_skill")
EVAL_DIRS = {
    1: "eval-1-cimientos",
    2: "eval-2-bibliografia",
    3: "eval-3-auditoria",
}


def _texto(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _citar(evidencia: str, limite: int = 240) -> str:
    limpio = " ".join(str(evidencia).split())
    return limpio[:limite] + ("…" if len(limpio) > limite else "")


def _titulo(md: str) -> str:
    for linea in md.splitlines():
        if linea.strip().startswith("#"):
            return linea.lstrip("#").strip()
    m = re.search(r"(?im)^\s*t[ií]tulo\s*[:\-]\s*(.+)$", md)
    return m.group(1).strip() if m else ""


def _secciones(md: str) -> list[str]:
    return [l.lstrip("#").strip().lower() for l in md.splitlines() if l.strip().startswith("#")]


def eval_1(out: Path) -> list[tuple[str, bool, str]]:
    archivo = out / "cimientos.md"
    md = _texto(archivo)
    bajo = md.lower()
    titulo = _titulo(md)
    palabras = len(re.findall(r"\b[\wáéíóúñü]+\b", titulo, re.I))
    secciones = _secciones(md)

    preguntas = [l for l in md.splitlines() if "?" in l or "¿" in l]
    pregunta = " ".join(preguntas)
    dicotomica = bool(re.search(r"¿\s*(es|son|existe|existen|puede|pueden|hay|tiene|tienen)\b", pregunta, re.I))
    oes = len(re.findall(r"(?i)\bOE\s*\d|objetivo\s+espec[ií]fico\s*\d", md))
    bloom = re.findall(r"(?i)\b(analizar|examinar|evaluar|sintetizar|determinar|comparar|caracterizar|identificar|describir)\b", md)
    campo = re.findall(r"(?i)\b(encuestar|entrevistar|medir|aplicar\s+instrumento|trabajo\s+de\s+campo)\b", md)
    mab = bool(re.search(r"(?i)ap[eé]ndice\s+a|matriz\s+de\s+an[aá]lisis", md))
    premadurez = any(s in {"introducción", "introduccion", "índice", "indice", "referencias"} for s in secciones)
    urls = re.findall(r"https?://\S+", md)
    marcas = len(re.findall(r"\[VERIFICAR\]", md, re.I))
    citas = len(re.findall(r"\(\s*[A-ZÁÉÍÓÚ][^)]{2,60},\s*(19|20)\d{2}", md))

    return [
        ("El archivo cimientos.md existe en la carpeta de salida.", archivo.exists(), str(archivo)),
        ("El titulo tiene 20 palabras o menos y no termina en punto.", bool(titulo) and palabras <= 20 and not titulo.rstrip().endswith("."), f"titulo={titulo!r}; palabras={palabras}"),
        ("El titulo identifica fenomeno, sujeto/sector, lugar (Santa Cruz/Bolivia) y periodo 2021-2026.", bool(re.search(r"(?i)bolivia|santa\s+cruz", titulo)) and bool(re.search(r"(202[1-6]|per[ií]odo)", titulo, re.I)), f"titulo={titulo!r}"),
        ("El planteamiento sigue la piramide invertida: contexto global, contexto Bolivia y brecha (GAP).", all(bool(re.search(p, md, re.I)) for p in [r"global|internacional|cepal|bid|banco mundial", r"bolivia|santa\s+cruz", r"brecha|gap|sin embargo|no obstante|vac[ií]o"]), _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)global|bolivia|brecha|gap", l))[:400])),
        ("La formulacion es una sola pregunta abierta, no dicotomica.", len(preguntas) == 1 and not dicotomica, f"preguntas={len(preguntas)}; dicotomica={dicotomica}; {_citar(pregunta)}"),
        ("Incluye un objetivo general y entre 3 y 5 objetivos especificos.", bool(re.search(r"(?i)objetivo\s+general", md)) and 3 <= oes <= 5, f"OE detectados={oes}"),
        ("Los objetivos usan verbos cognitivos superiores de Bloom y evitan verbos de trabajo de campo.", len(set(v.lower() for v in bloom)) >= 2 and not campo, f"bloom={sorted(set(v.lower() for v in bloom))}; campo={campo}"),
        ("Incluye la MAB como Apendice A.", mab, _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)ap[eé]ndice\s+a|matriz\s+de", l)))),
        ("No incluye Introduccion, Indice ni lista final de Referencias (premadurez).", not premadurez, f"secciones={secciones}"),
        ("Ninguna cita o cifra inventada: cada dato tiene URL/DOI verificable o marca [VERIFICAR].", bool(urls) or marcas > 0 or citas == 0, f"urls={len(urls)}; citas={citas}; [VERIFICAR]={marcas}"),
        ("El enfoque territorial es Bolivia/Santa Cruz, no un caso extranjero.", bool(re.search(r"(?i)bolivia|santa\s+cruz", md)), f"menciones Bolivia={len(re.findall(r'(?i)bolivia', md))}"),
    ]


def eval_2(out: Path) -> list[tuple[str, bool, str]]:
    req = out / "referencias.json"
    md = out / "referencias_bibliograficas.md"
    xml = out / "Sources.xml"
    datos = []
    if req.exists():
        try:
            datos = json.loads(req.read_text(encoding="utf-8"))
            if isinstance(datos, dict):
                datos = datos.get("fuentes") or datos.get("sources") or datos.get("referencias") or []
        except Exception:
            datos = []

    srcs = []
    error_xml = ""
    if xml.exists():
        try:
            srcs = ET.parse(xml).getroot().findall("b:Source", NS)
        except Exception as exc:  # noqa: BLE001
            error_xml = str(exc)

    def campo(s, nombre):
        return s.findtext(f"b:{nombre}", namespaces=NS)

    tipos = {campo(s, "SourceType") for s in srcs}
    tags = [campo(s, "Tag") for s in srcs]
    oblig = {n: all(campo(s, n) for s in srcs) for n in ("Tag", "SourceType", "Title", "Year", "URL")}
    md_txt = _texto(md)
    lineas = [l.strip() for l in md_txt.splitlines() if l.strip() and not l.strip().startswith(("#", ">", "-", "|", "*"))]
    ordenadas = sorted(lineas, key=str.lower) == lineas and len(lineas) >= 3

    return [
        ("Existen los tres archivos: referencias.json, referencias_bibliograficas.md y Sources.xml.", req.exists() and md.exists() and xml.exists(), f"{req.exists()},{md.exists()},{xml.exists()}"),
        ("Sources.xml es XML bien formado y contiene exactamente 3 b:Source.", not error_xml and len(srcs) == 3, f"error={error_xml}; sources={len(srcs)}"),
        ("Cada b:Source tiene Tag, SourceType, Title, Year y URL.", all(oblig.values()), json.dumps(oblig)),
        ("Los SourceType son validos y adecuados: Report, InternetSite y JournalArticle.", tipos == {"Report", "InternetSite", "JournalArticle"}, f"tipos={sorted(tipos)}"),
        ("Los tags son unicos.", len(tags) == len(set(tags)) and all(tags), f"tags={tags}"),
        ("El Markdown contiene las 3 referencias en orden alfabetico.", md_txt.lower().count("http") >= 3 and ordenadas, f"lineas={len(lineas)}; ordenadas={ordenadas}"),
        ("El articulo usa JournalArticle con revista, volumen y numero.", any(campo(s, "SourceType") == "JournalArticle" and campo(s, "JournalName") and campo(s, "Volume") and campo(s, "Issue") for s in srcs), f"journal={[campo(s,'JournalName') for s in srcs if campo(s,'SourceType')=='JournalArticle']}"),
        ("No hay fuentes adicionales ni inventadas.", len(datos) == 3 and len(srcs) == 3, f"json={len(datos)}; xml={len(srcs)}"),
        ("El DOI aparece como URL https://doi.org/...", any("doi.org/10.65924" in (campo(s, "URL") or "") for s in srcs), f"urls={[campo(s,'URL') for s in srcs]}"),
    ]


def eval_3(out: Path) -> list[tuple[str, bool, str]]:
    archivo = out / "auditoria.md"
    md = _texto(archivo)
    bajo = md.lower()

    ids = {i for i in ("TIT", "PRO", "OBJ", "REV", "TER", "DIS", "CON", "INT", "RES", "REF", "CAR", "PAG", "FOR", "IND", "APE", "ACT", "GEO") if re.search(rf"\b{i}\b", md)}
    correcciones = len(re.findall(r"(?i)correcci[oó]n|reemplaz|sustitu|elimin|cambiar|debe\s+decir|reescrib", md))

    return [
        ("El informe auditoria.md existe.", archivo.exists(), str(archivo)),
        ("Detecta el titulo entre comillas y con punto final.", bool(re.search(r"(?i)comilla", md)) and bool(re.search(r"(?i)punto\s+final|punto\b", md)) and bool(re.search(r"(?i)t[ií]tulo", md)), _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)comilla|punto", l)))),
        ("Detecta el uso de 'Bibliografia' y exige 'Referencias' (o su exclusion en Cimientos).", "bibliograf" in bajo and "referencias" in bajo, _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)bibliograf|referencias", l)))),
        ("Detecta la primera persona ('Yo analice', 'veremos').", bool(re.search(r"(?i)primera\s+persona|yo\s+analic|veremos", md)), _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)primera\s+persona|yo|veremos", l)))),
        ("Detecta datos de 2019 fuera de la ventana 2021-2026.", "2019" in md and bool(re.search(r"(?i)202[1-6]|ventana|recencia|actual", md)), _citar(" | ".join(l for l in md.splitlines() if "2019" in l or re.search(r"(?i)202[1-6]|ventana", l)))),
        ("Detecta la ausencia de fuentes/citas verificables.", bool(re.search(r"(?i)(sin|no\s+hay|falta|ausencia)[^.]{0,60}(fuente|cita|referencia)", md)) or bool(re.search(r"(?i)cita[s]?\s+verificable", md)), _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)fuente|cita", l)))),
        ("Detecta la ausencia de MAB/Apendice A en Cimientos.", bool(re.search(r"(?i)mab|matriz\s+de\s+an[aá]lisis|ap[eé]ndice\s+a", md)), _citar(" | ".join(l for l in md.splitlines() if re.search(r"(?i)mab|matriz|ap[eé]ndice", l)))),
        ("Cada hallazgo cita un ID normativo (TIT, PRO, REV, REF, APE, GEO...).", len(ids) >= 3, f"ids={sorted(ids)}"),
        ("Propone correcciones concretas, no genericas.", correcciones >= 3, f"correcciones={correcciones}"),
        ("No declara cumplimientos inexistentes.", not re.search(r"(?i)0\s+incumplimientos|todo\s+cumple|sin\s+observaciones|100\s*%\s*cumple", md), "sin frases de cumplimiento absoluto"),
    ]


CHECKS = {1: eval_1, 2: eval_2, 3: eval_3}


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python evals/grade_runs.py evals/iteration-1")
        return 2
    iter_dir = Path(sys.argv[1]).resolve()

    for eval_id, nombre in EVAL_DIRS.items():
        for config in CONFIGS:
            out = iter_dir / nombre / config / "outputs"
            if not out.is_dir():
                print(f"⚠ Falta {out}")
                continue
            checks = CHECKS[eval_id](out)
            expectations = [{"text": t, "passed": bool(p), "evidence": _citar(e)} for t, p, e in checks]
            passed = sum(1 for e in expectations if e["passed"])
            total = len(expectations)
            grading = {
                "expectations": expectations,
                "summary": {
                    "passed": passed,
                    "failed": total - passed,
                    "total": total,
                    "pass_rate": round(passed / total, 4) if total else 0.0,
                },
            }
            destino = iter_dir / nombre / config / "grading.json"
            destino.write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{nombre}/{config}: {passed}/{total} ({grading['summary']['pass_rate']:.0%})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
