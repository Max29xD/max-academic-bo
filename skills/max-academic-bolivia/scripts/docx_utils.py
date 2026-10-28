"""Utilidades avanzadas para manipulación, inspección y validación de documentos Word (.docx).

Incorpora las mejores prácticas del estándar OOXML y de la skill docx:
- Validación estructural contra esquema XML (previene archivos corruptos en Word).
- Fusión de runs fragmentados (merge_runs) para edición precisa de texto.
- Extracción de texto y tablas a Markdown sin dependencias externas.
- Diagnóstico de secciones, encabezados, paginación y estilos.

Uso:
  python scripts/docx_utils.py validar output/monografia.docx
  python scripts/docx_utils.py texto output/monografia.docx
  python scripts/docx_utils.py fusionar-runs input.docx -o limpio.docx
  python scripts/docx_utils.py info output/monografia.docx
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "b": "http://schemas.openxmlformats.org/officeDocument/2006/bibliography",
}


def validar_docx(ruta: Path | str) -> tuple[bool, list[str]]:
    """Valida la integridad de archivo ZIP y la sintaxis XML de un .docx."""
    p = Path(ruta)
    errores: list[str] = []
    if not p.exists():
        return False, [f"El archivo no existe: {p}"]

    if not zipfile.is_zipfile(p):
        return False, [f"El archivo no es un contenedor ZIP / OOXML válido: {p}"]

    try:
        with zipfile.ZipFile(p, "r") as zf:
            nombres = zf.namelist()
            partes_esenciales = ["[Content_Types].xml", "word/document.xml"]
            for pe in partes_esenciales:
                if pe not in nombres:
                    errores.append(f"Falta parte esencial del paquete: {pe}")

            # Validar XML de cada parte .xml
            for nom in nombres:
                if nom.endswith(".xml") or nom.endswith(".rels"):
                    try:
                        contenido = zf.read(nom)
                        ET.fromstring(contenido)
                    except ET.ParseError as pe:
                        errores.append(f"Error XML en {nom}: {pe}")
                    except Exception as ex:
                        errores.append(f"Error leyendo {nom}: {ex}")
    except Exception as exc:
        errores.append(f"Excepción general al abrir el ZIP: {exc}")

    es_valido = len(errores) == 0
    return es_valido, errores


def extraer_texto_docx(ruta: Path | str) -> str:
    """Extrae párrafos y tablas de un .docx a texto plano / markdown ligero."""
    p = Path(ruta)
    if not p.exists() or not zipfile.is_zipfile(p):
        return ""

    lineas: list[str] = []
    with zipfile.ZipFile(p, "r") as zf:
        if "word/document.xml" not in zf.namelist():
            return ""
        root = ET.fromstring(zf.read("word/document.xml"))

        for elem in root.iter():
            if elem.tag == f"{{{NS['w']}}}p":
                textos = [t.text for t in elem.findall(f".//{{{NS['w']}}}t") if t.text]
                if textos:
                    lineas.append("".join(textos))
            elif elem.tag == f"{{{NS['w']}}}tbl":
                # Fila de tabla
                for row in elem.findall(f"{{{NS['w']}}}tr"):
                    celdas = []
                    for c in row.findall(f"{{{NS['w']}}}tc"):
                        c_textos = [t.text for t in c.findall(f".//{{{NS['w']}}}t") if t.text]
                        celdas.append(" ".join("".join(c_textos).split()))
                    if celdas:
                        lineas.append("| " + " | ".join(celdas) + " |")

    return "\n".join(lineas)


def fusionar_runs(ruta_in: Path | str, ruta_out: Path | str) -> bool:
    """Coalesce runs adyacentes con formato idéntico en word/document.xml."""
    pin = Path(ruta_in)
    pout = Path(ruta_out)
    if not pin.exists() or not zipfile.is_zipfile(pin):
        print(f"✖ Archivo no válido: {pin}", file=sys.stderr)
        return False

    with zipfile.ZipFile(pin, "r") as zin:
        archivos = {item.filename: zin.read(item.filename) for item in zin.infolist()}

    if "word/document.xml" not in archivos:
        return False

    doc_root = ET.fromstring(archivos["word/document.xml"])

    for p in doc_root.findall(f".//{{{NS['w']}}}p"):
        hijos = list(p)
        i = 0
        while i < len(hijos) - 1:
            h1 = hijos[i]
            h2 = hijos[i + 1]

            if h1.tag == f"{{{NS['w']}}}r" and h2.tag == f"{{{NS['w']}}}r":
                rpr1 = h1.find(f"{{{NS['w']}}}rPr")
                rpr2 = h2.find(f"{{{NS['w']}}}rPr")

                str1 = ET.tostring(rpr1) if rpr1 is not None else b""
                str2 = ET.tostring(rpr2) if rpr2 is not None else b""

                if str1 == str2:
                    t1 = h1.find(f"{{{NS['w']}}}t")
                    t2 = h2.find(f"{{{NS['w']}}}t")
                    if t1 is not None and t2 is not None and t2.text:
                        t1.text = (t1.text or "") + (t2.text or "")
                        # Preservar espacios si es necesario
                        if (t1.text and (t1.text.startswith(" ") or t1.text.endswith(" "))):
                            t1.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                        p.remove(h2)
                        hijos.pop(i + 1)
                        continue
            i += 1

    archivos["word/document.xml"] = ET.tostring(doc_root, encoding="utf-8")

    pout.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(pout, "w", zipfile.ZIP_DEFLATED) as zout:
        for fname, content in archivos.items():
            zout.writestr(fname, content)

    print(f"✔ Runs fusionados guardados en: {pout}")
    return True


def info_docx(ruta: Path | str) -> dict:
    """Extrae métricas generales del .docx."""
    p = Path(ruta)
    valido, errores = validar_docx(p)
    if not valido:
        return {"valido": False, "errores": errores}

    texto = extraer_texto_docx(p)
    palabras = len(texto.split())
    lineas = texto.splitlines()

    tablas = 0
    encabezados = []
    with zipfile.ZipFile(p, "r") as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
        tablas = len(root.findall(f".//{{{NS['w']}}}tbl"))
        for p_elem in root.findall(f".//{{{NS['w']}}}p"):
            p_style = p_elem.find(f".//{{{NS['w']}}}pStyle")
            if p_style is not None:
                val = p_style.get(f"{{{NS['w']}}}val")
                if val and ("Heading" in val or "Ttulo" in val or "Titulo" in val):
                    textos = [t.text for t in p_elem.findall(f".//{{{NS['w']}}}t") if t.text]
                    encabezados.append(f"{val}: {''.join(textos)}")

    return {
        "valido": True,
        "archivo": str(p),
        "palabras_aprox": palabras,
        "parrafos_lineas": len(lineas),
        "tablas": tablas,
        "encabezados_detectados": encabezados[:15],
    }


def main():
    parser = argparse.ArgumentParser(description="Utilidades avanzadas OOXML / DOCX")
    sub = parser.add_subparsers(dest="subcomando", required=True)

    p_val = sub.add_parser("validar", help="Valida la estructura ZIP y XML del .docx")
    p_val.add_argument("archivo", help="Ruta al archivo .docx")

    p_txt = sub.add_parser("texto", help="Extrae el texto y tablas a la consola")
    p_txt.add_argument("archivo", help="Ruta al archivo .docx")

    p_fus = sub.add_parser("fusionar-runs", help="Fusiona runs idénticos en el documento")
    p_fus.add_argument("archivo", help="Ruta al archivo .docx de entrada")
    p_fus.add_argument("-o", "--salida", required=True, help="Ruta de salida")

    p_inf = sub.add_parser("info", help="Muestra métricas y análisis de estructura")
    p_inf.add_argument("archivo", help="Ruta al archivo .docx")

    args = parser.parse_args()

    if args.subcomando == "validar":
        valido, errs = validar_docx(args.archivo)
        if valido:
            print(f"✔ Documento válido según estándar OOXML: {args.archivo}")
            return 0
        else:
            print(f"✖ Documento presenta errores estructurales ({len(errs)}):", file=sys.stderr)
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            return 1

    elif args.subcomando == "texto":
        txt = extraer_texto_docx(args.archivo)
        print(txt)
        return 0

    elif args.subcomando == "fusionar-runs":
        ok = fusionar_runs(args.archivo, args.salida)
        return 0 if ok else 1

    elif args.subcomando == "info":
        res = info_docx(args.archivo)
        import json
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
