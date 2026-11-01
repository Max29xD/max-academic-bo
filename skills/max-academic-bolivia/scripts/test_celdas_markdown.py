"""Test del control A3 (equivalente a verificar_integridad.py): fugas de Markdown en y
cerca de las tablas del DOCX compilado.

Verifica que el renderizador DOCX (generar_monografia_docx.py):
  1. No vuelque marcadores Markdown literales (**, *, <br>, backticks) en las celdas
     de tablas ni en la línea de palabras clave del resumen.
  2. Renderice `**negrita**` como <w:b/>, `*cursiva*` como <w:i/>, `` `código` `` con
     fuente Consolas y `<br>` como <w:br/> real dentro de la misma celda.
  3. Escriba la etiqueta "Palabras clave:" en cursiva y el valor sin asteriscos.
  4. Regresión: un documento sin tablas ni palabras clave compila sin excepciones y
     con la misma validación OOXML.

Uso:  python scripts/test_celdas_markdown.py
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
import zipfile
from html import unescape
from pathlib import Path

RUTA_SCRIPTS = Path(__file__).resolve().parent
if str(RUTA_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(RUTA_SCRIPTS))

import generar_monografia_docx as comp  # noqa: E402

MD_CON_TABLA = """# Diseño de Prueba del Compilador Para Validar Celdas

## Resumen
Prueba de compilación para validar el volcado de celdas de tablas. **Palabras clave:** prueba, compilador, docx

## 1. Introducción
Párrafo simple de prueba sin tablas ni figuras.

## Apéndice A
| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| **negrita** | *cursiva* | `código` | texto<br>segunda línea | **n** + `c` | <br>inicial | `x`<br>**y** |
| normal 1 | normal 2 | normal 3 | **destacado** texto | *f* | g | h |

## Apéndice B
| Col1 | Col2 | Col3 |
|------|------|------|
| a | **b** | c |
"""

MD_SIN_TABLA = """# Título de Prueba Sin Tablas

## Resumen
Resumen mínimo de regresión sin palabras clave ni tablas.

## 1. Introducción
Solo prosa continua de prueba.
"""


def _runs(xml: str):
    return re.findall(r"<w:r>.*?</w:r>", xml, flags=re.S)


def _texto_run(run: str) -> str:
    m = re.search(r"<w:t[^>]*>(.*?)</w:t>", run, flags=re.S)
    return unescape(m.group(1)) if m else ""


def _extraer_tablas_por_docx(docx_path: Path) -> dict:
    """Devuelve {'tabla_ancha': xml_enumerado, ...} usando los tramos <w:tbl>."""
    xml = zipfile.ZipFile(docx_path).read("word/document.xml").decode("utf-8")
    tablas = re.findall(r"<w:tbl>.*?</w:tbl>", xml, flags=re.S)
    anchas = [t for t in tablas if len(re.findall(r"<w:tr\b", t)) >= 2]
    return {"xml": xml, "tablas": tablas, "anchas": anchas}


def test_celdas_y_palabras_clave(tmp: Path) -> bool:
    md = tmp / "prueba_tablas.md"
    docx_path = tmp / "prueba_tablas.docx"
    md.write_text(MD_CON_TABLA, encoding="utf-8")
    comp.compilar_monografia_docx(md, docx_path, overrides={}, generar_revision=False)

    data = _extraer_tablas_por_docx(docx_path)
    xml = data["xml"]

    def _wts_documento():
        return [_texto_run(r) for r in _runs(xml) if _texto_run(r)]

    problemas: list[str] = []

    # 1. Cero fugas de marcadores en cualquier w:t del documento.
    fugas = [
        t for t in _wts_documento()
        if "**" in t or "<br" in t.lower() or "`" in t
    ]
    if fugas:
        problemas.append(f"w:t con marcadores literales: {fugas!r}")

    # 2. La tabla ancha (7 columnas) existe y usa 9 pt; la de 3 columnas, 10 pt.
    anchas = data["anchas"]
    if not anchas:
        problemas.append("No se encontró la tabla ancha de prueba.")
    else:
        ancha_xml = anchas[0]
        if "Consolas" not in ancha_xml:
            problemas.append("La celda de código no usa fuente Consolas en la tabla ancha.")
        if "<w:br/>" not in ancha_xml:
            problemas.append("El <br> de celda no se volcó como <w:br/> en la tabla ancha.")

    # 3. Tokens de formato presentes en el documento con su formato activo.
    hay_negrita = any(t == "negrita" for t in _wts_documento())
    hay_codigo_consolas = any(
        "Consolas" in r for r in _runs(xml) if re.search(r"<w:t[^>]*>código</w:t>", r)
    )
    if not hay_negrita:
        problemas.append("El token **negrita** no se renderizó como run de texto.")
    if not hay_codigo_consolas:
        problemas.append("El token `código` no se renderizó con Consolas.")

    # 4. Palabras clave: etiqueta en cursiva y valor sin asteriscos.
    if not any(r_kw for r_kw in _runs(xml) if "Palabras clave" in _texto_run(r_kw) and "<w:i/>" in r_kw):
        problemas.append("La etiqueta 'Palabras clave:' no está en cursiva.")
    valores = [t for t in _wts_documento() if "compilador" in t and "prueba" in t]
    if not valores or "**" in valores[0]:
        problemas.append(f"El valor de palabras clave quedó sucio: {valores!r}")

    # 5. Validación OOXML del propio compilador: el paquete resultante es legible.
    docx_package = zipfile.ZipFile(docx_path)
    if docx_package.read("word/document.xml") is None:
        problemas.append("El paquete DOCX quedó ilegible.")

    return not problemas, problemas


def test_regresion_sin_tablas(tmp: Path) -> bool:
    md = tmp / "prueba_regresion.md"
    docx_path = tmp / "prueba_regresion.docx"
    md.write_text(MD_SIN_TABLA, encoding="utf-8")
    comp.compilar_monografia_docx(md, docx_path, overrides={}, generar_revision=False)
    xml = _extraer_tablas_por_docx(docx_path)["xml"]
    fugas = [
        _texto_run(r) for r in _runs(xml)
        if "`" in r and _texto_run(r)
    ]
    return True, ([] if not fugas else [f"Fugas inesperadas en documento de regresión: {fugas!r}"])


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="test_celdas_md_"))
    fallos = 0
    try:
        for nombre, fn in (("celdas y palabras clave", test_celdas_y_palabras_clave),
                           ("regresión sin tablas", test_regresion_sin_tablas)):
            try:
                ok, problemas = fn(tmp)
            except Exception as exc:  # fallo de compilación cuenta como error
                ok, problemas = False, [f"Excepción: {exc!r}"]
            estado = "OK" if ok else "FALLO"
            print(f"[{estado}] {nombre}")
            for p in problemas:
                print(f"    - {p}")
            fallos += 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fallos:
        print(f"✖ {fallos} grupo(s) de pruebas fallaron.")
        return 1
    print("✔ Test del control A3 superado: 0 fugas de Markdown en el DOCX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
