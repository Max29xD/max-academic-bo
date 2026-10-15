"""
Generador de fuentes bibliográficas en formato XML para Microsoft Word (Office Open XML Bibliography)
y formateo de referencias en estilo APA 7.

Compatible con: Word > Referencias > Administrar fuentes > Examinar (Manage Sources > Browse)
o reemplazo / adición a %APPDATA%\\Microsoft\\Bibliography\\Sources.xml
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Any, Optional
import os
import re

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
    "thesis": "Thesis"
}

def clean_tag(tag: str) -> str:
    """Genera un tag XML alfanumérico válido para Word."""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', tag)
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
    """
    Construye un elemento <b:Source> según el esquema de bibliografía de Microsoft Word.
    """
    src_type_raw = source.get("type", "WebSite").lower()
    source_type = SOURCE_TYPE_MAPPING.get(src_type_raw, source.get("type", "WebSite"))

    b_source = ET.Element(f"{{{NS_B}}}Source")

    tag = source.get("tag")
    if not tag:
        authors = source.get("authors", [])
        last_name = "Fuente"
        if authors:
            if isinstance(authors[0], dict):
                last_name = authors[0].get("last", "Fuente")
            elif isinstance(authors[0], str):
                parts = authors[0].split()
                last_name = parts[-1] if parts else "Fuente"
        elif source.get("author_corporate"):
            last_name = source.get("author_corporate")[:10]
        elif source.get("title"):
            last_name = re.sub(r'\s+', '', source.get("title")[:8])

        year = source.get("year", "s.f.")
        tag = f"{clean_tag(last_name)}{year}"

    tag_el = ET.SubElement(b_source, f"{{{NS_B}}}Tag")
    tag_el.text = tag

    type_el = ET.SubElement(b_source, f"{{{NS_B}}}SourceType")
    type_el.text = source_type

    # Autores
    authors = source.get("authors", [])
    author_corp = source.get("author_corporate")

    if authors or author_corp:
        b_author_outer = ET.SubElement(b_source, f"{{{NS_B}}}Author")
        if author_corp:
            b_corp = ET.SubElement(b_author_outer, f"{{{NS_B}}}Corporate")
            b_corp.text = str(author_corp).strip()
        elif authors:
            b_author_inner = ET.SubElement(b_author_outer, f"{{{NS_B}}}Author")
            b_namelist = ET.SubElement(b_author_inner, f"{{{NS_B}}}NameList")
            for aut in authors:
                if isinstance(aut, dict):
                    first = aut.get("first", "")
                    last = aut.get("last", "")
                    middle = aut.get("middle", "")
                elif isinstance(aut, str):
                    # formato simple "Apellido, Nombre" o "Nombre Apellido"
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
    if source.get("title"):
        title_el = ET.SubElement(b_source, f"{{{NS_B}}}Title")
        title_el.text = str(source["title"]).strip()

    # Año / Mes / Día
    if source.get("year"):
        year_el = ET.SubElement(b_source, f"{{{NS_B}}}Year")
        year_el.text = str(source["year"]).strip()
    if source.get("month"):
        month_el = ET.SubElement(b_source, f"{{{NS_B}}}Month")
        month_el.text = str(source["month"]).strip().zfill(2)
    if source.get("day"):
        day_el = ET.SubElement(b_source, f"{{{NS_B}}}Day")
        day_el.text = str(source["day"]).strip().zfill(2)

    # URL / DOI
    if source.get("url"):
        url_el = ET.SubElement(b_source, f"{{{NS_B}}}URL")
        url_el.text = str(source["url"]).strip()
    if source.get("doi"):
        doi_el = ET.SubElement(b_source, f"{{{NS_B}}}DOI")
        doi_el.text = str(source["doi"]).strip()

    # Campos específicos según SourceType
    if source_type == "WebSite":
        if source.get("site_name") or source.get("publication_title"):
            sitename_el = ET.SubElement(b_source, f"{{{NS_B}}}NameofWebSite")
            sitename_el.text = str(source.get("site_name") or source.get("publication_title")).strip()
    elif source_type == "JournalArticle":
        if source.get("journal_name") or source.get("publication_title"):
            jour_el = ET.SubElement(b_source, f"{{{NS_B}}}JournalName")
            jour_el.text = str(source.get("journal_name") or source.get("publication_title")).strip()
        if source.get("volume"):
            vol_el = ET.SubElement(b_source, f"{{{NS_B}}}Volume")
            vol_el.text = str(source["volume"]).strip()
        if source.get("issue") or source.get("number"):
            iss_el = ET.SubElement(b_source, f"{{{NS_B}}}Issue")
            iss_el.text = str(source.get("issue") or source.get("number")).strip()
        if source.get("pages"):
            pages_el = ET.SubElement(b_source, f"{{{NS_B}}}Pages")
            pages_el.text = str(source["pages"]).strip()
    elif source_type == "Book":
        if source.get("publisher"):
            pub_el = ET.SubElement(b_source, f"{{{NS_B}}}Publisher")
            pub_el.text = str(source["publisher"]).strip()
        if source.get("city"):
            city_el = ET.SubElement(b_source, f"{{{NS_B}}}City")
            city_el.text = str(source["city"]).strip()
        if source.get("edition"):
            ed_el = ET.SubElement(b_source, f"{{{NS_B}}}Edition")
            ed_el.text = str(source["edition"]).strip()
    elif source_type == "BookSection":
        if source.get("book_title"):
            bt_el = ET.SubElement(b_source, f"{{{NS_B}}}BookTitle")
            bt_el.text = str(source["book_title"]).strip()
        if source.get("publisher"):
            pub_el = ET.SubElement(b_source, f"{{{NS_B}}}Publisher")
            pub_el.text = str(source["publisher"]).strip()
        if source.get("pages"):
            pages_el = ET.SubElement(b_source, f"{{{NS_B}}}Pages")
            pages_el.text = str(source["pages"]).strip()
    elif source_type == "Report":
        if source.get("institution") or source.get("publisher"):
            inst_el = ET.SubElement(b_source, f"{{{NS_B}}}Institution")
            inst_el.text = str(source.get("institution") or source.get("publisher")).strip()
        if source.get("report_number"):
            rn_el = ET.SubElement(b_source, f"{{{NS_B}}}ReportNumber")
            rn_el.text = str(source["report_number"]).strip()

    return b_source

def generate_word_bibliography_xml(sources: List[Dict[str, Any]], output_filepath: Optional[str] = None) -> str:
    """
    Genera el XML en formato Microsoft Word (<b:Sources>) y opcionalmente lo guarda en disco.
    """
    # Ordenar alfabéticamente por autor o título si no tiene autor
    def get_sort_key(s):
        authors = s.get("authors", [])
        if authors:
            if isinstance(authors[0], dict):
                return authors[0].get("last", "").lower()
            return str(authors[0]).lower()
        if s.get("author_corporate"):
            return str(s["author_corporate"]).lower()
        return str(s.get("title", "")).lower()

    sorted_sources = sorted(sources, key=get_sort_key)

    # Construir XML root
    root = ET.Element(f"{{{NS_B}}}Sources", attrib={
        "SelectedStyle": "",
        "xmlns": NS_B
    })

    for src in sorted_sources:
        root.append(build_word_source(src))

    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    # Limpiar posibles líneas vacías producidas por toprettyxml
    cleaned_lines = [line for line in pretty_xml.splitlines() if line.strip()]
    final_xml = "\n".join(cleaned_lines) + "\n"

    if output_filepath:
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(final_xml)

    return final_xml

def format_apa7(source: Dict[str, Any]) -> str:
    """
    Genera la referencia formateada en texto plano siguiendo la norma APA 7ma edición.
    """
    authors = source.get("authors", [])
    author_corp = source.get("author_corporate")
    
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
        author_str = author_corp.strip()

    # Fecha
    year = source.get("year", "s.f.")
    month = source.get("month_name") or source.get("month")
    day = source.get("day")
    
    if month and day:
        date_str = f"({year}, {day} de {month})"
    elif month:
        date_str = f"({year}, {month})"
    else:
        date_str = f"({year})"

    title = source.get("title", "").strip()
    src_type = source.get("type", "WebSite").lower()
    
    url = source.get("url", "").strip()
    doi = source.get("doi", "").strip()
    link = f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else url

    # Formatos según tipo
    if src_type in ["website", "web", "blog"]:
        site = source.get("site_name") or source.get("publication_title", "")
        if author_str:
            ref = f"{author_str} {date_str}. {title}."
        else:
            ref = f"{title}. {date_str}."
        if site:
            ref += f" {site}."
        if link:
            ref += f" {link}"
    elif src_type in ["journalarticle", "journal", "article"]:
        journal = source.get("journal_name") or source.get("publication_title", "")
        vol = source.get("volume", "")
        issue = source.get("issue") or source.get("number", "")
        pages = source.get("pages", "")
        
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
    elif src_type in ["book"]:
        publisher = source.get("publisher", "")
        pub_str = f" {publisher}." if publisher else ""
        if author_str:
            ref = f"{author_str} {date_str}. *{title}*.{pub_str}"
        else:
            ref = f"*{title}*. {date_str}.{pub_str}"
        if link:
            ref += f" {link}"
    elif src_type in ["report"]:
        inst = source.get("institution") or source.get("publisher", "")
        rn = source.get("report_number", "")
        rn_str = f" ({rn})" if rn else ""
        inst_str = f" {inst}." if inst else ""
        if author_str:
            ref = f"{author_str} {date_str}. *{title}*{rn_str}.{inst_str}"
        else:
            ref = f"*{title}*{rn_str}. {date_str}.{inst_str}"
        if link:
            ref += f" {link}"
    else:
        # Fallback genérico
        site = source.get("site_name") or source.get("publisher", "")
        site_str = f" {site}." if site else ""
        if author_str:
            ref = f"{author_str} {date_str}. {title}.{site_str}"
        else:
            ref = f"{title}. {date_str}.{site_str}"
        if link:
            ref += f" {link}"

    return ref.strip()
