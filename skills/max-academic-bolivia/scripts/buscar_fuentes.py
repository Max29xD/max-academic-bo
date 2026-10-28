#!/usr/bin/env python3
"""Búsqueda reproducible de literatura académica con evidencia en disco (Tavily / Perplexity-style).

Capacidades:
1. Si `tvly` CLI está instalado: ejecuta `tvly search`, `research` o `extract`.
2. Si `tvly` no está pero existe la variable `TAVILY_API_KEY`: realiza las consultas
   directamente a la API REST oficial de Tavily (sin requerir dependencias externas).
3. Si ninguno está disponible: permite registrar búsquedas del agente o estructurar
   evidencia reproducible en `output/fuentes/` con aviso del plan B.

Uso:
  python scripts/buscar_fuentes.py "inclusión financiera Bolivia 2024" --tipo search
  python scripts/buscar_fuentes.py "regulación fintech Bolivia" --tipo research --modelo pro
  python scripts/buscar_fuentes.py --tipo extract --url https://www.bcb.gob.bo/...
  python scripts/buscar_fuentes.py --plantilla "consulta manual" --url https://...
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import output_dir  # noqa: E402


def _slug(texto: str, maximo: int = 50) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto[:maximo] or "consulta"


def _tvly_cli() -> str | None:
    return shutil.which("tvly")


def _api_key() -> str | None:
    return os.environ.get("TAVILY_API_KEY", "").strip() or None


def _consultar_api_tavily(endpoint: str, payload: dict, timeout: int = 60) -> dict:
    api_key = _api_key()
    if not api_key:
        raise ValueError("TAVILY_API_KEY no configurada.")
    payload["api_key"] = api_key
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.tavily.com/{endpoint}",
        data=data_bytes,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ejecutar_api_directa(args) -> dict:
    if args.tipo == "search":
        payload = {
            "query": args.consulta,
            "search_depth": args.profundidad if args.profundidad in ("basic", "advanced") else "advanced",
            "max_results": args.maximo,
        }
        if args.rango_tiempo:
            payload["time_range"] = args.rango_tiempo
        if args.tema:
            payload["topic"] = args.tema
        if args.dominios:
            payload["include_domains"] = args.dominios
        return _consultar_api_tavily("search", payload, timeout=args.timeout)

    elif args.tipo == "extract":
        payload = {
            "urls": args.url,
        }
        if args.consulta:
            payload["query"] = args.consulta
        return _consultar_api_tavily("extract", payload, timeout=args.timeout)

    elif args.tipo == "research":
        # Tavily API research endpoint o fallback a búsqueda avanzada profunda
        try:
            payload = {
                "input": args.consulta,
                "model": args.modelo,
            }
            return _consultar_api_tavily("research", payload, timeout=args.timeout)
        except urllib.error.HTTPError:
            # Fallback a search avanzado con contenido extendido
            payload = {
                "query": args.consulta,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": max(args.maximo, 10),
            }
            res = _consultar_api_tavily("search", payload, timeout=args.timeout)
            answer = res.get("answer", "")
            return {
                "report": answer,
                "content": answer,
                "sources": res.get("results", []),
                "modo_fallback": "search_advanced_with_answer",
            }


def _comando_tvly(args) -> list[str]:
    exe = _tvly_cli()
    if not exe:
        raise RuntimeError("tvly no disponible")
    cmd = [exe, args.tipo]
    if args.tipo == "extract":
        cmd.extend(args.url)
    else:
        cmd.append(args.consulta)
    if args.tipo == "search":
        cmd += ["--depth", args.profundidad, "--max-results", str(args.maximo), "--json"]
        if args.rango_tiempo:
            cmd += ["--time-range", args.rango_tiempo]
        if args.tema:
            cmd += ["--topic", args.tema]
        if args.dominios:
            cmd += ["--include-domains", ",".join(args.dominios)]
    elif args.tipo == "research":
        cmd += ["--model", args.modelo, "--citation-format", "apa", "--json"]
    elif args.tipo == "extract":
        cmd += ["--format", "markdown", "--json"]
        if args.consulta:
            cmd += ["--query", args.consulta, "--chunks-per-source", "3"]
    return cmd


def _resumen(tipo: str, data) -> list[str]:
    lineas: list[str] = []
    if tipo == "search" and isinstance(data, dict):
        results = data.get("results", [])
        lineas.append(f"Resultados encontrados: {len(results)}")
        for i, r in enumerate(results, 1):
            lineas.append(f"{i:>2}. {r.get('title', '(sin título)')}")
            lineas.append(f"    {r.get('url', '')}  [score {r.get('score', 'n/d')}]")
            content = r.get("content", "")
            if content:
                lineas.append(f"    Snippet: {content[:160]}…")
    elif tipo == "extract" and isinstance(data, dict):
        for r in data.get("results", []):
            lineas.append(f"• {r.get('url', '')} — {len(r.get('raw_content') or '')} caracteres extraídos")
    elif tipo == "research":
        texto = data.get("content") or data.get("report") or "" if isinstance(data, dict) else str(data)
        lineas.append(texto[:1200] + ("…" if len(texto) > 1200 else ""))
        fuentes = data.get("sources", []) if isinstance(data, dict) else []
        for s in fuentes[:10]:
            lineas.append(f"  - {s.get('title', '')}: {s.get('url', '')}")
    return lineas


def principal() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("consulta", nargs="?", default="", help="Consulta o tema")
    ap.add_argument("--tipo", choices=["search", "research", "extract"], default="search")
    ap.add_argument("--url", action="append", default=[], help="URL(s) para --tipo extract")
    ap.add_argument("--profundidad", choices=["ultra-fast", "fast", "basic", "advanced"], default="advanced")
    ap.add_argument("--maximo", type=int, default=10, help="Resultados máximos (search)")
    ap.add_argument("--rango-tiempo", help="day, week, month, year o rango YYYY-MM-DD..YYYY-MM-DD")
    ap.add_argument("--tema", choices=["general", "news", "finance"], help="Topic de Tavily")
    ap.add_argument("--dominios", nargs="*", help="Dominios incluidos (search)")
    ap.add_argument("--modelo", choices=["mini", "pro", "auto"], default="auto", help="Modelo (research)")
    ap.add_argument("--salida", help="Archivo JSON de evidencia (por defecto output/fuentes/…)")
    ap.add_argument("--timeout", type=int, default=900, help="Segundos máximos de espera")
    ap.add_argument("--plantilla", action="store_true", help="Genera plantilla de evidencia para registrar búsquedas del agente")
    args = ap.parse_args()

    if args.tipo == "extract" and not args.url:
        ap.error("--tipo extract requiere al menos un --url")
    if args.tipo != "extract" and not args.consulta and not args.plantilla:
        ap.error("falta la consulta")

    herramienta_usada = "desconocido"
    data = None

    if args.plantilla:
        herramienta_usada = "agente_manual"
        data = {
            "consulta": args.consulta or "Consulta realizada por el agente",
            "resultados": [
                {
                    "title": "Título del documento o sitio oficial",
                    "url": args.url[0] if args.url else "https://...",
                    "content": "Fragmento textual verificado en la fuente.",
                    "score": 1.0,
                    "verificado": True,
                }
            ],
        }
    elif _tvly_cli():
        herramienta_usada = "tvly_cli"
        cmd = _comando_tvly(args)
        print("▸ " + " ".join(cmd), file=sys.stderr)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
            if proc.returncode == 0:
                try:
                    data = json.loads(proc.stdout)
                except json.JSONDecodeError:
                    data = {"salida_cruda": proc.stdout}
            else:
                print(f"⚠ tvly falló con código {proc.returncode}. Probando API directa...", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"✖ tvly excedió {args.timeout}s.", file=sys.stderr)

    if data is None and _api_key():
        herramienta_usada = "tavily_api_directa"
        print("▸ Consultando API directa de Tavily (vía TAVILY_API_KEY)...", file=sys.stderr)
        try:
            data = _ejecutar_api_directa(args)
        except Exception as exc:
            print(f"✖ Error en API Tavily: {exc}", file=sys.stderr)

    if data is None:
        if not args.plantilla:
            print("✖ No se encontró `tvly` CLI ni `TAVILY_API_KEY` válida.", file=sys.stderr)
            print("  Opciones para habilitar Tavily:", file=sys.stderr)
            print("  1. Configura la API key: $env:TAVILY_API_KEY='tvly-...' (Windows) o export TAVILY_API_KEY=...", file=sys.stderr)
            print("  2. Instala tvly CLI: curl -fsSL https://cli.tavily.com/install.sh | bash", file=sys.stderr)
            print("  3. Plan B: utiliza la búsqueda web nativa del agente y guarda la evidencia con --plantilla", file=sys.stderr)
            print("  Ver references/tavily_busqueda.md e integraciones.md", file=sys.stderr)
            return 3

    slug_nombre = _slug(args.consulta or (args.url[0] if args.url else "evidencia"))
    destino = Path(args.salida) if args.salida else (
        output_dir() / "fuentes" / f"{dt.datetime.now():%Y%m%d-%H%M%S}-{args.tipo}-{slug_nombre}.json"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    evidencia = {
        "generado": dt.datetime.now(dt.timezone.utc).isoformat(),
        "herramienta": herramienta_usada,
        "tipo": args.tipo,
        "consulta": args.consulta or None,
        "urls": args.url or None,
        "parametros": {
            "profundidad": args.profundidad if args.tipo == "search" else None,
            "maximo": args.maximo if args.tipo == "search" else None,
            "rango_tiempo": args.rango_tiempo,
            "tema": args.tema,
            "modelo": args.modelo if args.tipo == "research" else None,
        },
        "resultado": data,
    }
    destino.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✔ Evidencia guardada en: {destino}")
    for linea in _resumen(args.tipo, data):
        print(linea)
    print("Recordatorio: Cita únicamente fuentes abiertas o verificadas; marca [VERIFICAR] las pendientes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
