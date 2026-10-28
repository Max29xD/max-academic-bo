"""Generador de fuentes bibliográficas en formato XML para Microsoft Word (Office Open XML Bibliography)
y formateo de referencias en estilo APA 7.

Compatible con: Word > Referencias > Administrar fuentes > Examinar (Manage Sources > Browse)
o reemplazo / adición a %APPDATA%\\Microsoft\\Bibliography\\Sources.xml
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rutas import archivo_salida, output_dir  # noqa: E402

NS_B = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
ET.register_namespace("b", NS_B)

SOURCE_TYPE_MAPPING = {
    "website": "WebSite",
    "web": "WebSite",
    "sitio": "WebSite",
    "pagina_web": "WebSite",
    "journal": "JournalArticle",
    "article": "JournalArticle",
    "journalarticle": "JournalArticle",
    "articulo": "JournalArticle",
    "revista": "JournalArticle",
    "book": "Book",
    "libro": "Book",
    "booksection": "BookSection",
    "capitulo": "BookSection",
    "chapter": "BookSection",
    "report": "Report",
    "informe": "Report",
    "document": "Report",
    "documento": "Report",
    "conference": "ConferenceProceedings",
    "tesis": "Thesis",
    "thesis": "Thesis",
}


def clean_tag(tag: str) -> str:
    """Genera un tag XML alfanumérico válido para Word."""
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", tag)
    return cleaned if cleaned else "Ref1"


def create_person_element(b_ns: str, first: str, last: str, middle: str = "") -> ET.Element:
    person = ET.Element(f"{{{b_ns}}}Person")
    if last:
        last_el = ET.SubElement(person, f"{{{b_ns}}}Last")
        last_el.text = str(last).strip()
    if first:
        first_el = ET.SubElement(person, f"{{{b_ns}}}First")
        first_el.text = str(first).strip()
    if middle:
        mid_el = ET.SubElement(person, f"{{{b_ns}}}Middle")
        mid_el.text = str(middle).strip()
    return person


def build_word_source(source: Dict[str, Any]) -> ET.Element:
    """Construye un elemento <b:Source> según el esquema de bibliografía de Microsoft Word."""
    src_type_raw = str(source.get("type") or source.get("tipo_documento") or "WebSite").lower()
    source_type = SOURCE_TYPE_MAPPING.get(src_type_raw, source.get("type", "WebSite"))

    b_source = ET.Element(f"{{{NS_B}}}Source")

    tag = source.get("tag")
    if not tag:
        authors = source.get("authors") or source.get("autores") or []
        last_name = "Fuente"
        if authors:
            if isinstance(authors[0], dict):
                last_name = authors[0].get("last", "Fuente")
            elif isinstance(authors[0], str):
                parts = authors[0].split()
                last_name = parts[-1] if parts else "Fuente"
        elif source.get("author_corporate") or source.get("institucion"):
            last_name = str(source.get("author_corporate") or source.get("institucion"))[:10]
        elif source.get("title") or source.get("titulo"):
            last_name = re.sub(r"\s+", "", str(source.get("title") or source.get("titulo"))[:8])

        year = source.get("year") or source.get("anio") or "s.f."
        tag = f"{clean_tag(last_name)}{year}"

    tag_el = ET.SubElement(b_source, f"{{{NS_B}}}Tag")
    tag_el.text = clean_tag(str(tag))

    type_el = ET.SubElement(b_source, f"{{{NS_B}}}SourceType")
    type_el.text = source_type

    # Autores
    autores_raw = source.get("authors") or source.get("autores")
    author_corp = source.get("author_corporate") or source.get("autores_institucionales") or source.get("autor_corporativo") or source.get("institucion")

    if not author_corp and isinstance(autores_raw, str):
        aut_str = autores_raw.strip()
        if any(term in aut_str.lower() for term in ["banco", "autoridad", "instituto", "ministerio", "fundación", "organización", "comisión", "asociación", "gaceta", "estado", "pci", "ibm", "owasp", "nist", "[", "cepal", "bid"]):
            author_corp = aut_str
            authors = []
        elif ";" in aut_str:
            authors = [a.strip() for a in aut_str.split(";")]
        elif " y " in aut_str or " & " in aut_str:
            parts = re.split(r"\s+(?:y|&)\s+", aut_str)
            authors = [p.strip() for p in parts]
        else:
            authors = [aut_str]
    elif isinstance(autores_raw, list):
        authors = autores_raw
    else:
        authors = []

    if authors or author_corp:
        b_author_outer = ET.SubElement(b_source, f"{{{NS_B}}}Author")
        b_author_inner = ET.SubElement(b_author_outer, f"{{{NS_B}}}Author")
        if author_corp:
            b_corp = ET.SubElement(b_author_inner, f"{{{NS_B}}}Corporate")
            b_corp.text = str(author_corp).strip()
        elif authors:
            b_namelist = ET.SubElement(b_author_inner, f"{{{NS_B}}}NameList")
            for aut in authors:
                if isinstance(aut, dict):
                    first = aut.get("first", "")
                    last = aut.get("last", "")
                    middle = aut.get("middle", "")
                elif isinstance(aut, str):
                    if "," in aut:
                        parts = aut.split(",", 1)
                        last = parts[0].strip()
                        first = parts[1].strip()
                    else:
                        parts = aut.strip().split()
                        last = parts[-1] if parts else ""
                        first = " ".join(parts[:-1]) if len(parts) > 1 else ""
                    middle = ""
                b_namelist.append(create_person_element(NS_B, first, last, middle))

    # Título
    title = source.get("title") or source.get("titulo")
    if title:
        title_el = ET.SubElement(b_source, f"{{{NS_B}}}Title")
        title_el.text = str(title).strip()

    # Año / Mes / Día
    year = source.get("year") or source.get("anio")
    if year:
        year_el = ET.SubElement(b_source, f"{{{NS_B}}}Year")
        year_el.text = str(year).strip()
    month = source.get("month") or source.get("mes")
    if month:
        month_el = ET.SubElement(b_source, f"{{{NS_B}}}Month")
        month_el.text = str(month).strip().zfill(2)
    day = source.get("day") or source.get("dia")
    if day:
        day_el = ET.SubElement(b_source, f"{{{NS_B}}}Day")
        day_el.text = str(day).strip().zfill(2)

    # URL / DOI
    url = source.get("url")
    if url:
        url_el = ET.SubElement(b_source, f"{{{NS_B}}}URL")
        url_el.text = str(url).strip()
    doi = source.get("doi")
    if doi:
        doi_el = ET.SubElement(b_source, f"{{{NS_B}}}DOI")
        doi_el.text = str(doi).strip()
        if not url:
            url_el = ET.SubElement(b_source, f"{{{NS_B}}}URL")
            clean_doi = str(doi).strip().replace("https://doi.org/", "")
            url_el.text = f"https://doi.org/{clean_doi}"

    # Campos específicos según SourceType
    if source_type in ("WebSite", "InternetSite"):
        site = source.get("site_name") or source.get("publication_title") or source.get("fuente_publicacion")
        if site:
            sitename_el = ET.SubElement(b_source, f"{{{NS_B}}}NameofWebSite")
            sitename_el.text = str(site).strip()
    elif source_type == "JournalArticle":
        jour = source.get("journal_name") or source.get("publication_title") or source.get("revista") or source.get("fuente_publicacion")
        if jour:
            jour_el = ET.SubElement(b_source, f"{{{NS_B}}}JournalName")
            jour_el.text = str(jour).strip()
        vol = source.get("volume") or source.get("volumen")
        if vol:
            vol_el = ET.SubElement(b_source, f"{{{NS_B}}}Volume")
            vol_el.text = str(vol).strip()
        iss = source.get("issue") or source.get("number") or source.get("numero")
        if iss:
            iss_el = ET.SubElement(b_source, f"{{{NS_B}}}Issue")
            iss_el.text = str(iss).strip()
        pages = source.get("pages") or source.get("paginas")
        if pages:
            pages_el = ET.SubElement(b_source, f"{{{NS_B}}}Pages")
            pages_el.text = str(pages).strip()
    elif source_type == "Book":
        pub = source.get("publisher") or source.get("editorial")
        if pub:
            pub_el = ET.SubElement(b_source, f"{{{NS_B}}}Publisher")
            pub_el.text = str(pub).strip()
        city = source.get("city") or source.get("ciudad")
        if city:
            city_el = ET.SubElement(b_source, f"{{{NS_B}}}City")
            city_el.text = str(city).strip()
        ed = source.get("edition") or source.get("edicion")
        if ed:
            ed_el = ET.SubElement(b_source, f"{{{NS_B}}}Edition")
            ed_el.text = str(ed).strip()
    elif source_type == "BookSection":
        bt = source.get("book_title") or source.get("libro")
        if bt:
            bt_el = ET.SubElement(b_source, f"{{{NS_B}}}BookTitle")
            bt_el.text = str(bt).strip()
        pub = source.get("publisher") or source.get("editorial")
        if pub:
            pub_el = ET.SubElement(b_source, f"{{{NS_B}}}Publisher")
            pub_el.text = str(pub).strip()
        pages = source.get("pages") or source.get("paginas")
        if pages:
            pages_el = ET.SubElement(b_source, f"{{{NS_B}}}Pages")
            pages_el.text = str(pages).strip()
    elif source_type == "Report":
        inst = source.get("institution") or source.get("publisher") or source.get("institucion")
        if inst:
            inst_el = ET.SubElement(b_source, f"{{{NS_B}}}Institution")
            inst_el.text = str(inst).strip()
        rn = source.get("report_number") or source.get("numero_informe")
        if rn:
            rn_el = ET.SubElement(b_source, f"{{{NS_B}}}ReportNumber")
            rn_el.text = str(rn).strip()

    return b_source


def generate_word_bibliography_xml(sources: List[Dict[str, Any]], output_filepath: Optional[str] = None) -> str:
    """Genera el XML en formato Microsoft Word (<b:Sources>) y opcionalmente lo guarda en disco."""
    def get_sort_key(s):
        authors = s.get("authors") or s.get("autores") or []
        if authors:
            if isinstance(authors[0], dict):
                return authors[0].get("last", "").lower()
            return str(authors[0]).lower()
        if s.get("author_corporate") or s.get("institucion"):
            return str(s.get("author_corporate") or s.get("institucion")).lower()
        return str(s.get("title") or s.get("titulo") or "").lower()

    sorted_sources = sorted(sources, key=get_sort_key)

    root = ET.Element(
        f"{{{NS_B}}}Sources",
        attrib={
            "SelectedStyle": "\\APASeventhEdition.xsl",
            "StyleName": "APA",
            "Version": "7",
            "xmlns": NS_B,
        },
    )

    for src in sorted_sources:
        root.append(build_word_source(src))

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    cleaned_lines = [line for line in pretty_xml.splitlines() if line.strip()]
    final_xml = "\n".join(cleaned_lines) + "\n"

    if output_filepath:
        ruta = Path(output_filepath).resolve()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(final_xml, encoding="utf-8")

    return final_xml


def format_apa7(source: Dict[str, Any]) -> str:
    """Genera la referencia formateada en texto plano siguiendo la norma APA 7ma edición."""
    autores_raw = source.get("authors") or source.get("autores")
    author_corp = source.get("author_corporate") or source.get("autores_institucionales") or source.get("autor_corporativo") or source.get("institucion")

    if not author_corp and isinstance(autores_raw, str):
        aut_str = autores_raw.strip()
        if any(term in aut_str.lower() for term in ["banco", "autoridad", "instituto", "ministerio", "fundación", "organización", "comisión", "asociación", "gaceta", "estado", "pci", "ibm", "owasp", "nist", "[", "cepal", "bid"]):
            author_corp = aut_str
            authors = []
        elif ";" in aut_str:
            authors = [a.strip() for a in aut_str.split(";")]
        elif " y " in aut_str or " & " in aut_str:
            parts = re.split(r"\s+(?:y|&)\s+", aut_str)
            authors = [p.strip() for p in parts]
        else:
            authors = [aut_str]
    elif isinstance(autores_raw, list):
        authors = autores_raw
    else:
        authors = []

    author_str = ""
    if authors:
        formatted_authors = []
        for a in authors:
            if isinstance(a, dict):
                last = a.get("last", "").strip()
                first = a.get("first", "").strip()
                initial = f"{first[0]}." if first else ""
                formatted_authors.append(f"{last}, {initial}".strip(","))
            elif isinstance(a, str):
                if "," in a:
                    parts = a.split(",", 1)
                    last = parts[0].strip()
                    first = parts[1].strip()
                    initial = f"{first[0]}." if first else ""
                    formatted_authors.append(f"{last}, {initial}".strip(","))
                else:
                    parts = a.strip().split()
                    last = parts[-1] if parts else ""
                    first = parts[0] if len(parts) > 1 else ""
                    initial = f"{first[0]}." if first else ""
                    formatted_authors.append(f"{last}, {initial}".strip(","))

        if len(formatted_authors) == 1:
            author_str = formatted_authors[0]
        elif len(formatted_authors) == 2:
            author_str = f"{formatted_authors[0]} y {formatted_authors[1]}"
        elif len(formatted_authors) > 2:
            author_str = ", ".join(formatted_authors[:-1]) + f", y {formatted_authors[-1]}"
    elif author_corp:
        author_str = str(author_corp).strip()

    year = source.get("year") or source.get("anio") or "s.f."
    month = source.get("month_name") or source.get("month") or source.get("mes")
    day = source.get("day") or source.get("dia")

    if month and day:
        date_str = f"({year}, {day} de {month})"
    elif month:
        date_str = f"({year}, {month})"
    else:
        date_str = f"({year})"

    title = str(source.get("title") or source.get("titulo") or "").strip()
    src_type = str(source.get("type") or source.get("tipo_documento") or "WebSite").lower()

    url = str(source.get("url") or "").strip()
    doi = str(source.get("doi") or "").strip()
    link = f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else url

    if src_type in ["website", "web", "blog", "internetsite"]:
        site = source.get("site_name") or source.get("publication_title") or source.get("fuente_publicacion", "")
        if author_str:
            ref = f"{author_str} {date_str}. {title}."
        else:
            ref = f"{title}. {date_str}."
        if site:
            ref += f" {site}."
        if link:
            ref += f" {link}"
    elif src_type in ["journalarticle", "journal", "article"]:
        journal = source.get("journal_name") or source.get("publication_title") or source.get("revista", "")
        vol = source.get("volume") or source.get("volumen", "")
        issue = source.get("issue") or source.get("number") or source.get("numero", "")
        pages = source.get("pages") or source.get("paginas", "")

        vol_issue = ""
        if vol and issue:
            vol_issue = f", {vol}({issue})"
        elif vol:
            vol_issue = f", {vol}"

        pages_str = f", {pages}" if pages else ""

        if author_str:
            ref = f"{author_str} {date_str}. {title}. *{journal}*{vol_issue}{pages_str}."
        else:
            ref = f"{title}. {date_str}. *{journal}*{vol_issue}{pages_str}."
        if link:
            ref += f" {link}"
    elif src_type in ["book", "libro"]:
        publisher = source.get("publisher") or source.get("editorial", "")
        pub_str = f" {publisher}." if publisher else ""
        if author_str:
            ref = f"{author_str} {date_str}. *{title}*.{pub_str}"
        else:
            ref = f"*{title}*. {date_str}.{pub_str}"
        if link:
            ref += f" {link}"
    elif src_type in ["report", "informe"]:
        inst = source.get("institution") or source.get("publisher") or source.get("institucion", "")
        rn = source.get("report_number") or source.get("numero_informe", "")
        rn_str = f" ({rn})" if rn else ""
        inst_str = f" {inst}." if inst else ""
        if author_str:
            ref = f"{author_str} {date_str}. *{title}*{rn_str}.{inst_str}"
        else:
            ref = f"*{title}*{rn_str}. {date_str}.{inst_str}"
        if link:
            ref += f" {link}"
    else:
        site = source.get("site_name") or source.get("publisher") or ""
        site_str = f" {site}." if site else ""
        if author_str:
            ref = f"{author_str} {date_str}. {title}.{site_str}"
        else:
            ref = f"{title}. {date_str}.{site_str}"
        if link:
            ref += f" {link}"

    return ref.strip()


def main():
    parser = argparse.ArgumentParser(description="Generar bibliografía en formato XML para Microsoft Word y APA 7")
    parser.add_argument("--input", "-i", help="Archivo JSON con la lista de fuentes (por defecto output/referencias.json)", required=False)
    parser.add_argument("--output", "-o", help="Archivo XML de salida (ej. Sources.xml)", default="Sources.xml")
    parser.add_argument("--print-apa", "-p", help="Imprimir referencias formateadas en APA 7 en consola", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else archivo_salida("referencias.json")
    if input_path.exists():
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                sources = data
            elif isinstance(data, dict):
                sources = data.get("fuentes") or data.get("sources") or data.get("referencias") or []
            else:
                sources = []
    else:
        print(f"ℹ No se encontró archivo de entrada en {input_path}. Usando ejemplo demostrativo.", file=sys.stderr)
        sources = [
            {
                "tag": "BCB2026",
                "type": "Report",
                "author_corporate": "Banco Central de Bolivia",
                "title": "Informe de política monetaria y sistema de pagos",
                "year": "2026",
                "institution": "BCB",
                "url": "https://www.bcb.gob.bo",
            }
        ]

    out_path = Path(args.output) if Path(args.output).is_absolute() else archivo_salida(args.output)
    xml_content = generate_word_bibliography_xml(sources, str(out_path))
    print(f"✔ Archivo XML generado exitosamente en: {out_path}")

    if args.print_apa:
        print("\nReferencias en formato APA 7:")
        print("=" * 60)
        for s in sources:
            print(format_apa7(s))


if __name__ == "__main__":
    main()
