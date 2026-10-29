#!/usr/bin/env python3
"""Genera consultas de búsqueda para una monografía de compilación con foco en Bolivia y corte temporal a Octubre 2026.

Entrada: grupos de conceptos (sinónimos separados por '|'; el primero es el término principal).
Salida (Markdown o JSON):
  1. Mapa de conceptos
  2. Cadenas booleanas (Scopus, Web of Science, Google Scholar, SciELO/Redalyc/Dialnet)
  3. Consultas web cortas por embudo geográfico L1..L5
  4. Consultas de actualidad reciente 2024–2026 (Corte Octubre 2026 / la más actualizada)
  5. Consultas site: para revistas, repositorios y fuentes estadísticas oficiales
  6. Plantilla de registro de búsqueda (Apéndice B)

Ejemplo:
  python generar_consultas.py \
    --grupo "comercio electrónico|e-commerce|comercio digital|ecommerce" \
    --grupo "pyme|mipyme|pequeñas y medianas empresas|SME" \
    --grupo "retail|comercio minorista|venta minorista" \
    --grupo "barreras|factores|adopción|facilitadores" \
    --desde 2021 --hasta 2026
"""
import argparse
import json

DEFAULT_GEO = {
    "L1": ["Santa Cruz de la Sierra", "Montero", "El Alto", "La Paz", "Cochabamba", "cruceño"],
    "L2": ["Santa Cruz", "La Paz", "Cochabamba", "Chuquisaca", "Tarija", "Oruro", "Potosí", "Beni", "Pando"],
    "L3": ["Bolivia", "boliviano", "Estado Plurinacional de Bolivia"],
    "L4": ["América Latina", "Comunidad Andina", "Latinoamérica"],
    "L5": [],
}

SITES = {
    "revistas": ["scielo.org.bo", "scielo.org", "redalyc.org", "dialnet.unirioja.es", "doaj.org"],
    "repositorios": [
        "uagrm.edu.bo", "umsa.bo", "ucb.edu.bo", "upb.edu", "upsa.edu.bo",
        "umss.edu.bo", "uajms.edu.bo", "usfx.bo", "univalle.edu",
    ],
    "oficiales": [
        "ine.gob.bo", "udape.gob.bo", "bcb.gob.bo", "asfi.gob.bo", "att.gob.bo",
        "agetic.gob.bo", "seprec.gob.bo", "gacetaoficialdebolivia.gob.bo",
    ],
    "organismos": ["cepal.org", "publications.iadb.org", "worldbank.org", "caf.com", "unctad.org"],
    "gremios": ["cainco.org.bo", "ibce.org.bo", "cedla.org", "inesad.edu.bo"],
}


def q(term):
    """Entrecomilla términos con espacios o guiones."""
    t = term.strip()
    return f'"{t}"' if (" " in t or "-" in t) else t


def or_block(terms):
    return "(" + " OR ".join(q(t) for t in terms) + ")"


def parse_groups(raw):
    groups = []
    for g in raw:
        terms = [t.strip() for t in g.split("|") if t.strip()]
        if terms:
            groups.append(terms)
    return groups


def boolean_strings(groups, geo_terms, desde, hasta):
    core = " AND ".join(or_block(g) for g in groups)
    geo = or_block(geo_terms) if geo_terms else ""
    out = {}
    with_geo = f"{core} AND {geo}" if geo else core
    out["Scopus (con geografía, 2021–2026)"] = f"TITLE-ABS-KEY ( {with_geo} ) AND PUBYEAR > {desde - 1} AND PUBYEAR < {hasta + 1}"
    out["Scopus (punta reciente 2024–2026)"] = f"TITLE-ABS-KEY ( {with_geo} ) AND PUBYEAR > 2023 AND PUBYEAR < {hasta + 1}"
    out["Scopus (marco teórico, sin geografía)"] = f"TITLE-ABS-KEY ( {core} ) AND PUBYEAR > {desde - 1} AND PUBYEAR < {hasta + 1}"
    out["Web of Science (con geografía)"] = f"TS=( {with_geo} ) AND PY=({desde}-{hasta})"
    out["Web of Science (punta reciente 2024–2026)"] = f"TS=( {with_geo} ) AND PY=(2024-{hasta})"
    out["Google Scholar (con geografía)"] = with_geo.replace(" AND ", " ") + f"  [filtrar desde {desde} y foco en 2024–{hasta}]"
    out["Genérica SciELO / Redalyc / Dialnet"] = with_geo + f" (2021–{hasta})"
    return out


def short_queries(groups, geo_levels):
    """Consultas web cortas: términos principales + variantes de sinónimos por nivel."""
    principals = [g[0] for g in groups]
    queries = {}
    for lvl, geos in geo_levels.items():
        qs = []
        geo_opts = geos if geos else [""]
        for geo in geo_opts[:3]:
            base = " ".join(q(p) for p in principals[:3])
            qs.append(f"{base} {q(geo) if geo else ''}".strip())
        # variantes con sinónimos del primer y segundo grupo
        for gi in range(min(2, len(groups))):
            for syn in groups[gi][1:3]:
                alt = list(principals[:3])
                alt[gi] = syn
                geo = geo_opts[0]
                qs.append(" ".join(q(p) for p in alt) + (f" {q(geo)}" if geo else ""))
        # deduplicar preservando orden
        seen, uniq = set(), []
        for s in qs:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        queries[lvl] = uniq
    return queries


def recency_queries(groups):
    """Consultas especializadas con delimitación estricta de actualidad a Octubre 2026."""
    principals = [q(g[0]) for g in groups[:3]]
    base = " ".join(principals)
    return [
        f"{base} Bolivia 2024..2026",
        f"{base} \"Santa Cruz\" 2024..2026",
        f"site:ine.gob.bo {base} 2024 OR 2025 OR 2026",
        f"site:ine.gob.bo \"censo 2024\" {base}",
        f"site:bcb.gob.bo {base} 2025 OR 2026",
        f"site:asfi.gob.bo {base} 2025 OR 2026",
        f"site:scielo.org.bo {base} 2024..2026",
        f"site:redalyc.org {base} Bolivia 2024..2026",
        f"site:cainco.org.bo {base} 2024..2026",
        f"site:cepal.org Bolivia {base} 2024..2026",
        f"{base} Bolivia \"2025\" OR \"2026\" filetype:pdf",
    ]


def site_queries(groups):
    p = [q(g[0]) for g in groups[:3]]
    base = " ".join(p)
    res = {}
    for fam, doms in SITES.items():
        lst = []
        for d in doms:
            extra = " Bolivia" if d.endswith(".org") or d in ("dialnet.unirioja.es", "worldbank.org", "caf.com") else ""
            lst.append(f"site:{d} {base}{extra}")
        res[fam] = lst
    res["pdf_boliviano"] = [f"{base} Bolivia filetype:pdf", f"{base} \"Santa Cruz\" filetype:pdf"]
    return res


def render_md(groups, geo_levels, desde, hasta, booleans, shorts, recents, sites):
    L = []
    L.append("# Plan de búsqueda generado — Foco en Bolivia y Actualidad a Octubre 2026\n")
    L.append("## 1. Mapa de conceptos y delimitación temporal\n")
    L.append("| Grupo | Término principal | Sinónimos / variantes |")
    L.append("|---|---|---|")
    for i, g in enumerate(groups, 1):
        L.append(f"| G{i} | {g[0]} | {', '.join(g[1:]) or '—'} |")
    L.append(f"\nPeríodo general de búsqueda: {desde}–{hasta} (Corte: Octubre 2026)\n")
    L.append("Prioridad de recencia (ACT-1/ACT-2): ≥ 70 % fuentes en 2021–2026 y literatura de vanguardia 2024–2026.\n")

    L.append("## 2. Cadenas booleanas (para bases académicas y Apéndice B)\n")
    for k, v in booleans.items():
        L.append(f"**{k}**\n```\n{v}\n```")

    L.append("\n## 3. Consultas de actualidad reciente 2024–2026 (Corte Octubre 2026)\n")
    L.append("*(Ejecutar para garantizar datos y estudios de vanguardia)*\n")
    for r in recents:
        L.append(f"- `{r}`")

    L.append("\n## 4. Consultas web cortas por embudo geográfico\n")
    for lvl, qs in shorts.items():
        L.append(f"**{lvl}** — {', '.join(geo_levels[lvl]) or 'sin restricción geográfica (teoría fundacional)'}")
        for s in qs:
            L.append(f"- `{s}`")
        L.append("")

    L.append("## 5. Consultas por sitio institucional y repositorios\n")
    for fam, qs in sites.items():
        L.append(f"**{fam}**")
        for s in qs:
            L.append(f"- `{s}`")
        L.append("")

    L.append("## 6. Plantilla de registro de búsqueda (Apéndice B)\n")
    L.append("| Fecha (Oct 2026) | Base / sitio | Cadena o consulta | Filtros | Nivel | Revisados | Pertinentes | Incluidas (IDs) | Motivo de exclusión |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grupo", action="append", required=True,
                    help="Grupo de conceptos: 'principal|sinónimo|sinónimo'. Repetir 2–5 veces.")
    ap.add_argument("--desde", type=int, default=2021, help="Año de inicio de ventana de recencia (por defecto 2021)")
    ap.add_argument("--hasta", type=int, default=2026, help="Año de corte temporal (por defecto 2026)")
    for lvl in DEFAULT_GEO:
        ap.add_argument(f"--{lvl.lower()}", help=f"Reemplaza términos del nivel {lvl} (separados por '|')")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    groups = parse_groups(args.grupo)
    if len(groups) < 2:
        ap.error("Se necesitan al menos 2 grupos de conceptos.")

    geo_levels = {}
    for lvl, default in DEFAULT_GEO.items():
        override = getattr(args, lvl.lower())
        geo_levels[lvl] = [t.strip() for t in override.split("|") if t.strip()] if override else default

    booleans = boolean_strings(groups, geo_levels["L3"], args.desde, args.hasta)
    shorts = short_queries(groups, geo_levels)
    recents = recency_queries(groups)
    sites = site_queries(groups)

    if args.json:
        print(json.dumps({
            "grupos": groups, "geo": geo_levels, "booleanas": booleans,
            "actualidad_2026": recents, "web_cortas": shorts, "por_sitio": sites
        }, ensure_ascii=False, indent=2))
    else:
        print(render_md(groups, geo_levels, args.desde, args.hasta, booleans, shorts, recents, sites))


if __name__ == "__main__":
    main()