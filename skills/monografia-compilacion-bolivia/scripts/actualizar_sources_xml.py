"""Genera `Sources.xml` (Office Open XML Bibliography) desde `referencias.json`.

Word lo importa con **Referencias → Administrar fuentes → Examinar**. También puede
incrustarse en un `.docx` existente para que la bibliografía aparezca activa.

Diseño:
- Lee el catálogo del proyecto (`output/referencias.json` por defecto), no datos fijos.
- Acepta el esquema legado (autores/anio/titulo/fuente_publicacion/url) y el esquema
  estructurado (autores[], tipo_documento, revista, volumen, etc.).
- No toca la lista maestra global de Word salvo que se pida con `--sync-word-global`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import zipfile
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import NOMBRE_DOCX, archivo_salida, output_dir  # noqa: E402

NS_B = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
ET.register_namespace("b", NS_B)

TIPOS_VALIDOS = {
    "ArticleInAPeriodical",
    "Book",
    "BookSection",
    "JournalArticle",
    "ConferenceProceedings",
    "Report",
    "SoundRecording",
    "Performance",
    "Art",
    "DocumentFromInternetSite",
    "InternetSite",
    "Film",
    "Interview",
    "Patent",
    "ElectronicSource",
    "Case",
    "Misc",
}


def _texto(valor) -> str | None:
    if valor is None:
        return None
    valor = str(valor).strip()
    return valor or None


def _inferir_tipo(fuente: dict) -> str:
    explicito = _texto(fuente.get("tipo_documento") or fuente.get("source_type") or fuente.get("type"))
    if explicito:
        for tipo in TIPOS_VALIDOS:
            if tipo.lower() == explicito.lower():
                return tipo
    # "Artículo científico", "Informe oficial", "Nota de prensa"…
    pistas_texto = (explicito or _texto(fuente.get("tipo")) or "").lower()
    if pistas_texto:
        pistas = {
            "journal": "JournalArticle",
            "artículo": "JournalArticle",
            "articulo": "JournalArticle",
            "revista": "JournalArticle",
            "libro": "Book",
            "capítulo": "BookSection",
            "capitulo": "BookSection",
            "conferencia": "ConferenceProceedings",
            "prensa": "InternetSite",
            "nota": "InternetSite",
            "web": "InternetSite",
            "sitio": "InternetSite",
            "informe": "Report",
            "reporte": "Report",
            "norma": "Report",
            "regulatoria": "Report",
            "oficial": "Report",
        }
        bajo = pistas_texto
        for pista, tipo in pistas.items():
            if pista in bajo:
                return tipo
    if fuente.get("revista") or fuente.get("journal_name"):
        return "JournalArticle"
    if fuente.get("editorial") and not fuente.get("institucion"):
        return "Book"
    return "DocumentFromInternetSite"


def _partir_nombre(nombre: str) -> dict:
    """Convierte 'Apellido, N.' o 'Nombre Apellido' a {last, first}."""
    nombre = nombre.strip().rstrip(".")
    if "," in nombre:
        apellido, resto = nombre.split(",", 1)
        return {"last": apellido.strip(), "first": resto.strip()}
    partes = nombre.split()
    if len(partes) == 1:
        return {"last": partes[0], "first": ""}
    return {"last": " ".join(partes[-2:]), "first": " ".join(partes[:-2])}


def _autores(fuente: dict):
    """Devuelve ('corporativo', texto) o ('personas', [ {last, first} ])."""
    corporativo = _texto(
        fuente.get("autor_corporativo") or fuente.get("author_corporate") or fuente.get("institucion_autora")
    )
    if corporativo:
        return "corporativo", corporativo

    autores = fuente.get("autores") or fuente.get("authors")
    if isinstance(autores, list) and autores:
        if all(isinstance(a, dict) for a in autores):
            normalizados = []
            for a in autores:
                if a.get("last") or a.get("apellido"):
                    normalizados.append(
                        {
                            "last": _texto(a.get("last") or a.get("apellido")) or "",
                            "first": _texto(a.get("first") or a.get("nombre")) or "",
                        }
                    )
                elif a.get("nombre"):
                    normalizados.append(_partir_nombre(a["nombre"]))
            if normalizados:
                return "personas", normalizados
        elif all(isinstance(a, str) for a in autores):
            return "personas", [_partir_nombre(a) for a in autores if a.strip()]

    if isinstance(autores, str) and autores.strip():
        # El esquema legado guarda a veces una entidad ("ASFI") y a veces una lista.
        if "," in autores or len(autores.split()) <= 3:
            return "personas", [_partir_nombre(autores)]
        return "corporativo", autores.strip()

    return None, None


def normalizar(fuente: dict, indice: int) -> dict:
    """Mapea una entrada del catálogo a los campos del esquema de Word."""
    tipo = _inferir_tipo(fuente)
    titulo = _texto(fuente.get("titulo") or fuente.get("title")) or f"Fuente {indice}"
    anio = _texto(fuente.get("anio") or fuente.get("year")) or "s. f."
    clase, autores = _autores(fuente)

    if clase == "corporativo":
        autor_display = autores
    elif clase == "personas" and autores:
        autor_display = autores[0]["last"]
    else:
        autor_display = _texto(fuente.get("autores_cita")) or "Anónimo"

    url = _texto(fuente.get("url"))
    doi = _texto(fuente.get("doi"))
    if doi and not doi.lower().startswith("http"):
        url = f"https://doi.org/{doi.lstrip('doi:').strip()}"
    elif doi and not url:
        url = doi

    return {
        "tag": f"{autor_display}, {anio}",
        "type": tipo,
        "clase_autor": clase,
        "autores": autores,
        "title": titulo,
        "year": anio,
        "month": _texto(fuente.get("mes") or fuente.get("month")),
        "day": _texto(fuente.get("dia") or fuente.get("day")),
        "journal_name": _texto(fuente.get("revista") or fuente.get("journal_name") or fuente.get("publicacion")),
        "volume": _texto(fuente.get("volumen") or fuente.get("volume")),
        "issue": _texto(fuente.get("numero") or fuente.get("issue")),
        "pages": _texto(fuente.get("paginas") or fuente.get("pages")),
        "institution": _texto(fuente.get("institucion") or fuente.get("fuente_publicacion")),
        "publisher": _texto(fuente.get("editorial") or fuente.get("publisher")),
        "city": _texto(fuente.get("ciudad") or fuente.get("city")),
        "edition": _texto(fuente.get("edicion") or fuente.get("edition")),
        "site_name": _texto(fuente.get("sitio_web") or fuente.get("site_name") or fuente.get("fuente_publicacion")),
        "url": url,
    }


def cargar_fuentes(ruta: Path | None = None) -> list[dict]:
    ruta = ruta or archivo_salida("referencias.json")
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el catálogo: {ruta}\n"
            "Crea uno con: python scripts/gestor_referencias.py --init"
        )
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if isinstance(datos, dict):
        datos = datos.get("fuentes") or datos.get("sources") or datos.get("referencias") or []
    if not isinstance(datos, list) or not datos:
        raise ValueError(f"El catálogo {ruta} no contiene una lista de fuentes.")
    return datos


def build_xml(fuentes: list[dict] | None = None) -> bytes:
    fuentes = fuentes if fuentes is not None else cargar_fuentes()
    normalizadas = [normalizar(f, i) for i, f in enumerate(fuentes, 1)]

    # Word exige etiquetas únicas: "Autor, Año" puede repetirse.
    vistos: dict[str, int] = {}
    for fuente in normalizadas:
        base = fuente["tag"]
        vistos[base] = vistos.get(base, 0) + 1
        if vistos[base] > 1:
            letra = chr(ord("a") + vistos[base] - 1)
            fuente["tag"] = f"{base}{letra}"

    root = ET.Element(
        f"{{{NS_B}}}Sources",
        {
            "SelectedStyle": "\\APASeventhEdition.xsl",
            "StyleName": "APA 7ma Edición",
            "Version": "7",
        },
    )

    orden = [
        "Tag",
        "SourceType",
        "Author",
        "Title",
        "Year",
        "Month",
        "Day",
        "JournalName",
        "Volume",
        "Issue",
        "Pages",
        "Institution",
        "Publisher",
        "City",
        "Edition",
        "InternetSiteTitle",
        "URL",
    ]

    for s in normalizadas:
        src = ET.SubElement(root, f"{{{NS_B}}}Source")
        campos: dict[str, str] = {
            "Tag": s["tag"],
            "SourceType": s["type"],
            "Title": s["title"],
            "Year": s["year"],
            "JournalName": s["journal_name"],
            "Volume": s["volume"],
            "Issue": s["issue"],
            "Pages": s["pages"],
            "Institution": s["institution"],
            "Publisher": s["publisher"],
            "City": s["city"],
            "Edition": s["edition"],
            "InternetSiteTitle": s["site_name"] if s["type"] in ("InternetSite", "DocumentFromInternetSite") else None,
            "URL": s["url"],
            "Month": s["month"],
            "Day": s["day"],
        }
        for nombre in orden:
            if nombre == "Author":
                if s["clase_autor"] == "corporativo":
                    outer = ET.SubElement(src, f"{{{NS_B}}}{nombre}")
                    inner = ET.SubElement(outer, f"{{{NS_B}}}Author")
                    corp = ET.SubElement(inner, f"{{{NS_B}}}Corporate")
                    corp.text = s["autores"]
                elif s["clase_autor"] == "personas" and s["autores"]:
                    outer = ET.SubElement(src, f"{{{NS_B}}}{nombre}")
                    inner = ET.SubElement(outer, f"{{{NS_B}}}Author")
                    lista = ET.SubElement(inner, f"{{{NS_B}}}NameList")
                    for persona in s["autores"]:
                        p = ET.SubElement(lista, f"{{{NS_B}}}Person")
                        last = ET.SubElement(p, f"{{{NS_B}}}Last")
                        last.text = persona["last"]
                        first = ET.SubElement(p, f"{{{NS_B}}}First")
                        first.text = persona["first"]
                continue
            valor = campos.get(nombre)
            if valor:
                ET.SubElement(src, f"{{{NS_B}}}{nombre}").text = str(valor)

    rough = ET.tostring(root, encoding="utf-8")
    return minidom.parseString(rough).toprettyxml(indent="  ", encoding="utf-8")


def update_sources_xml(xml_bytes: bytes, destino: Path | None = None, sync_global: bool = False) -> Path:
    destino = destino or archivo_salida("Sources.xml")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(xml_bytes)
    print(f"✔ Sources.xml guardado en: {destino}")

    if sync_global:
        global_dir = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Bibliography"))
        if global_dir.is_dir():
            try:
                (global_dir / "Sources.xml").write_bytes(xml_bytes)
                print(f"✔ Lista maestra global de Word actualizada: {global_dir / 'Sources.xml'}")
            except Exception as exc:  # noqa: BLE001
                print(f"⚠ No se pudo actualizar la lista global de Word: {exc}")
        else:
            print("ℹ No se encontró %APPDATA%\\Microsoft\\Bibliography; se omite la lista global.")
    return destino


def embed_in_docx(xml_bytes: bytes, docx_file: Path | None = None) -> bool:
    docx_file = docx_file or archivo_salida(NOMBRE_DOCX)
    if not docx_file.exists():
        print(f"ℹ No hay DOCX para incrustar ({docx_file}). Sources.xml queda listo para importar.")
        return False

    temp_dir = Path(tempfile.mkdtemp(prefix="monografia-docx-"))
    try:
        with zipfile.ZipFile(docx_file, "r") as z_in:
            z_in.extractall(temp_dir)

        objetivo = None
        for item in temp_dir.glob("customXml/item*.xml"):
            contenido = item.read_text(encoding="utf-8", errors="ignore")
            if NS_B in contenido:
                objetivo = item
                break

        if not objetivo:
            print("ℹ El DOCX no contiene una parte de bibliografía en customXml; no se incrusta.")
            return False

        objetivo.write_bytes(xml_bytes)
        temporal = temp_dir / "_monografia_tmp.docx"
        with zipfile.ZipFile(temporal, "w", zipfile.ZIP_DEFLATED) as z_out:
            for raiz, _, archivos in os.walk(temp_dir):
                for nombre in archivos:
                    ruta = Path(raiz) / nombre
                    if ruta == temporal:
                        continue
                    z_out.write(ruta, ruta.relative_to(temp_dir))

        shutil.copy2(temporal, docx_file)
        print(f"✔ Bibliografía incrustada en el DOCX: {docx_file}")
        return True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def principal() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--catalogo", type=Path, help="referencias.json (por defecto output/referencias.json)")
    ap.add_argument("--salida", type=Path, help="Sources.xml de salida")
    ap.add_argument("--docx", type=Path, help="DOCX donde incrustar la bibliografía")
    ap.add_argument("--sync-word-global", action="store_true", help="Actualizar también la lista maestra de Word")
    args = ap.parse_args()

    fuentes = cargar_fuentes(args.catalogo)
    xml_bytes = build_xml(fuentes)
    update_sources_xml(xml_bytes, args.salida, args.sync_word_global)
    embed_in_docx(xml_bytes, args.docx)
    print(f"✔ {len(fuentes)} fuentes procesadas desde {args.catalogo or archivo_salida('referencias.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
