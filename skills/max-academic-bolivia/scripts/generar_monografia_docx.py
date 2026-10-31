"""
Compilador dinámico y agnóstico de documentos Word (.docx) para Monografías de Compilación
según las normas oficiales EIP-FINOR-UAGRM (corte 2026) y estilo APA 7.ª edición.

Diseño agnóstico y universal:
- CERO datos hardcodeados: funciona para cualquier tema (Redes, Ciberseguridad, Medicina,
  Derecho, Inteligencia Artificial, Agronomía, Educación, Finanzas, etc.).
- Compila directamente desde un archivo Markdown estructurado (por defecto output/monografia_completa.md).
- Extrae metadatos institucionales del Markdown o los recibe por parámetros CLI.
- Utiliza la plantilla limpia templates/apa7ma.docx para heredar estilos tipográficos,
  márgenes de 2.54 cm y encabezados multinivel automáticos.
- Aplica formato APA 7 estricto: carátula de 10/11 elementos, numeración romana en preliminares,
  reinicio en arábigos en el cuerpo, campo dinámico TOC, tablas APA 7 (sin líneas verticales)
  y referencias con sangría francesa e hipervínculos activos.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import docx
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import NOMBRE_DOCX, archivo_salida, logo as logo_actual, output_dir, plantilla  # noqa: E402
import docx_utils  # noqa: E402


# =========================================================================
# Utilidades de Formato XML y APA 7
# =========================================================================

def set_cell_border(cell, **kwargs):
    """Aplica bordes específicos a una celda XML."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = parse_xml(
                f'<{tag} {nsdecls("w")} w:val="{edge_data.get("val", "single")}" '
                f'w:sz="{edge_data.get("sz", 4)}" w:space="0" w:color="{edge_data.get("color", "auto")}"/>'
            )
            tcBorders.append(element)
    tcPr.append(tcBorders)


def set_table_apa_borders(table):
    """Aplica formato de tabla APA 7 (bordes superior, inferior y cabecera, sin líneas verticales)."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if r_idx == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

        for cell in row.cells:
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if r_idx == 0:
                set_cell_border(cell, top=dict(sz=8, val='single', color='000000'),
                                      bottom=dict(sz=6, val='single', color='000000'),
                                      left=dict(val='nil'), right=dict(val='nil'))
            elif r_idx == len(table.rows) - 1:
                set_cell_border(cell, bottom=dict(sz=8, val='single', color='000000'),
                                      left=dict(val='nil'), right=dict(val='nil'),
                                      top=dict(val='nil'))
            else:
                set_cell_border(cell, top=dict(val='nil'), bottom=dict(val='nil'),
                                      left=dict(val='nil'), right=dict(val='nil'))


def set_section_page_numbering(section, num_format="decimal", start_at=None):
    """Configura el formato y reinicio de numeración de página de una sección."""
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.insert_element_before(
            pgNumType,
            'w:cols', 'w:formProt', 'w:vAlign', 'w:noEndnote', 'w:titlePg',
            'w:textDirection', 'w:bidi', 'w:rtlGutter', 'w:docGrid',
            'w:printerSettings', 'w:sectPrChange'
        )
    pgNumType.set(qn('w:fmt'), num_format)
    if start_at is not None:
        pgNumType.set(qn('w:start'), str(start_at))


def configure_pagination(doc):
    """Deja un único campo PAGE en el pie de los preliminares; portada y cuerpo lo heredan o lo omiten."""
    secs = doc.sections
    for section in secs:
        section.header.is_linked_to_previous = True
        section.footer.is_linked_to_previous = True

    set_section_page_numbering(secs[0], num_format="decimal", start_at=1)
    if len(secs) > 1:
        set_section_page_numbering(secs[1], num_format="lowerRoman", start_at=2)
        prelim = secs[1]
        prelim.footer.is_linked_to_previous = False
        p = prelim.footer.paragraphs[0]
        p.text = ""
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run()
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)

        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))

        run._r.append(fldChar1)
        run._r.append(instrText)
        run._r.append(fldChar2)
        run._r.append(fldChar3)

    if len(secs) > 2:
        set_section_page_numbering(secs[2], num_format="decimal", start_at=1)
        body_sec = secs[2]
        body_sec.footer.is_linked_to_previous = False
        p_body = body_sec.footer.paragraphs[0]
        p_body.text = ""
        p_body.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run_b = p_body.add_run()
        run_b.font.name = 'Times New Roman'
        run_b.font.size = Pt(12)
        fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
        fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        run_b._r.append(fldChar1)
        run_b._r.append(instrText)
        run_b._r.append(fldChar2)
        run_b._r.append(fldChar3)

    prune_orphan_header_footer_parts(doc)


def prune_orphan_header_footer_parts(doc):
    """Elimina encabezados y pies que quedaron sin referencia tras reconfigurar secciones."""
    used = set()
    for sectPr in doc.element.body.iter(qn('w:sectPr')):
        for ref in list(sectPr.findall(qn('w:headerReference'))) + list(sectPr.findall(qn('w:footerReference'))):
            rid = ref.get(qn('r:id'))
            if rid:
                used.add(rid)
    for rid, rel in list(doc.part.rels.items()):
        if rel.reltype in (RT.HEADER, RT.FOOTER) and rid not in used:
            doc.part.drop_rel(rid)


def remove_template_toc(doc):
    """Elimina el índice precargado de la plantilla para que no duplique el TOC generado."""
    body = doc.element.body
    removed = 0
    for sdt in list(body.findall('.//' + qn('w:sdt'))):
        instr = "".join(t.text or "" for t in sdt.iter(qn('w:instrText')))
        if 'TOC' in instr:
            sdt.getparent().remove(sdt)
            removed += 1
    return removed


def disable_auto_numbering(paragraph):
    """Suprime la numeración automática heredada del estilo (p. ej. apéndices o referencias)."""
    numPr = paragraph._p.get_or_add_pPr().get_or_add_numPr()
    numPr.get_or_add_ilvl().set(qn('w:val'), '0')
    numPr.get_or_add_numId().set(qn('w:val'), '0')


def enable_update_fields_on_open(doc):
    """Configura el documento para que Microsoft Word actualice campos (TOC) al abrirse."""
    element = parse_xml(r'<w:updateFields %s w:val="true"/>' % nsdecls('w'))
    doc.settings.element.append(element)


def add_formatted_paragraph(doc, md_text, style='Normal', first_line_indent=0.5, line_spacing=2.0,
                            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=0):
    """Agrega un párrafo formateado procesando negritas (**texto**), cursivas (*texto*) y código (`texto`)."""
    p = doc.add_paragraph()
    try:
        p.style = doc.styles[style]
    except KeyError:
        p.style = doc.styles['Normal']
    p.paragraph_format.first_line_indent = Inches(first_line_indent)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = alignment

    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', md_text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**'):
            run = p.add_run(token[2:-2])
            run.bold = True
        elif token.startswith('`') and token.endswith('`'):
            run = p.add_run(token[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(10)
            continue
        elif token.startswith('*') and token.endswith('*'):
            run = p.add_run(token[1:-1])
            run.italic = True
        else:
            run = p.add_run(token)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    return p


def add_bullet_item(doc, bold_prefix, text, indent=0.5, hanging=-0.25):
    """Agrega un ítem de viñeta con formato APA/Times New Roman."""
    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.paragraph_format.left_indent = Inches(indent)
    p.paragraph_format.first_line_indent = Inches(hanging)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    r_bullet = p.add_run("• ")
    r_bullet.font.name = 'Times New Roman'
    r_bullet.font.size = Pt(12)

    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(12)
        r_bold.bold = True

    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', f" {text}" if bold_prefix else text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('`') and token.endswith('`'):
            r = p.add_run(token[1:-1])
            r.font.name = 'Consolas'
            r.font.size = Pt(10)
            continue
        if token.startswith('**') and token.endswith('**'):
            r = p.add_run(token[2:-2])
            r.bold = True
        elif token.startswith('*') and token.endswith('*'):
            r = p.add_run(token[1:-1])
            r.italic = True
        else:
            r = p.add_run(token)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
    return p


def add_reference_paragraph(doc, ref_text):
    """Agrega una referencia bibliográfica APA 7 con sangría francesa (0.5 in) e interlineado 2.0."""
    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|https?://\S+)', ref_text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**'):
            run = p.add_run(token[2:-2])
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        elif token.startswith('*') and token.endswith('*'):
            run = p.add_run(token[1:-1])
            run.italic = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        elif token.startswith('http://') or token.startswith('https://'):
            add_url_runs(p, token)
        else:
            run = p.add_run(token)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
    return p


def add_url_runs(paragraph, url):
    """Inserta una URL con salto controlado y formato de hipervínculo."""
    if len(url) > 65 and '&pid=' in url:
        head, tail = url.split('&pid=', 1)
        segments = [head, '&pid=' + tail]
    elif len(url) > 80 and '?' in url:
        head, tail = url.split('?', 1)
        segments = [head + '?', tail]
    else:
        segments = [url]

    for idx, segment in enumerate(segments):
        if idx:
            br = paragraph.add_run()
            br.add_break()
        run = paragraph.add_run(segment)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
        run.font.underline = True


def add_table_label(doc, table_num, table_title):
    """Inserta la etiqueta de tabla APA 7 en dos líneas: número en negrita y título en cursiva."""
    p_num = doc.add_paragraph()
    p_num.style = doc.styles['Normal']
    p_num.paragraph_format.space_before = Pt(12)
    p_num.paragraph_format.space_after = Pt(0)
    p_num.paragraph_format.line_spacing = 2.0
    r_num = p_num.add_run(table_num)
    r_num.bold = True
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(12)

    p_tit = doc.add_paragraph()
    p_tit.style = doc.styles['Normal']
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(6)
    p_tit.paragraph_format.line_spacing = 2.0
    r_tit = p_tit.add_run(table_title)
    r_tit.italic = True
    r_tit.font.name = 'Times New Roman'
    r_tit.font.size = Pt(12)


def add_table_note(doc, note_text, etiqueta="Nota."):
    """Inserta la nota al pie de tabla APA 7 ('Nota. ...')."""
    p_note = doc.add_paragraph()
    p_note.style = doc.styles['Normal']
    p_note.paragraph_format.space_before = Pt(4)
    p_note.paragraph_format.space_after = Pt(12)
    p_note.paragraph_format.line_spacing = 1.15
    r1 = p_note.add_run(etiqueta + " ")
    r1.italic = True
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(10)
    for token in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", note_text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            r = p_note.add_run(token[2:-2])
            r.bold = True
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            r = p_note.add_run(token[1:-1])
            r.italic = True
        else:
            r = p_note.add_run(token)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)


def add_toc_field(doc):
    """Inserta el campo dinámico de Tabla de Contenido (TOC) de Microsoft Word."""
    for style in doc.styles:
        if style.name and style.name.upper().startswith('TOC'):
            style.paragraph_format.line_spacing = 1.0
            style.paragraph_format.space_before = Pt(0)
            style.paragraph_format.space_after = Pt(0)

    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)

    run = p.add_run()
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))

    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


# =========================================================================
# Extracción Dinámica de Metadatos del Manuscrito
# =========================================================================

def extraer_metadatos(md_contenido: str, args=None) -> dict:
    """Extrae dinámicamente los metadatos institucionales del texto Markdown o aplica overrides."""
    lineas = md_contenido.splitlines()
    clean_lines = [re.sub(r'[*_`#]', '', l).strip() for l in lineas]

    meta = {
        "titulo": None,
        "programa": None,
        "mencion": None,
        "autor": None,
        "tutor": None,
        "gestion": "2026",
        "lugar": "Santa Cruz de la Sierra, Bolivia",
    }

    # 1. Título principal (primer encabezado # del documento)
    for l in lineas:
        l_str = l.strip()
        if l_str.startswith("# ") and not meta["titulo"]:
            candidato = l_str[2:].strip()
            if candidato.lower() not in ("resumen", "introducción", "ficha técnica de proyecto (p0)"):
                meta["titulo"] = candidato
                break

    # 2. Escaneo de líneas despojadas de formato
    for l in clean_lines:
        low = l.lower()
        if not meta["autor"] and low.startswith(('autor:', 'autora:', 'postgraduante:')):
            meta["autor"] = l.split(':', 1)[1].strip()
        elif not meta["tutor"] and low.startswith(('docente:', 'tutor:', 'docente guía / tutor:', 'docente guía/tutor:', 'docente tutor:')):
            meta["tutor"] = l.split(':', 1)[1].strip()
        elif not meta["programa"] and 'diplomado en' in low:
            idx = low.find('diplomado en')
            meta["programa"] = l[idx + len('diplomado en'):].strip()
        elif not meta["mencion"] and low.startswith(('mención:', 'mencion:')):
            meta["mencion"] = l.split(':', 1)[1].strip()
        elif re.search(r'\bgesti[oó]n\s*(\d{4})\b', low):
            meta["gestion"] = re.search(r'\bgesti[oó]n\s*(\d{4})\b', low).group(1)

    # 3. Overrides explícitos por CLI
    if args:
        if getattr(args, 'titulo', None):
            meta["titulo"] = args.titulo
        if getattr(args, 'programa', None):
            meta["programa"] = args.programa
        if getattr(args, 'autor', None):
            meta["autor"] = args.autor
        if getattr(args, 'tutor', None):
            meta["tutor"] = args.tutor
        if getattr(args, 'gestion', None):
            meta["gestion"] = args.gestion
        if getattr(args, 'lugar', None):
            meta["lugar"] = args.lugar

    # 4. Fallbacks limpios normativos (sin inventar datos ni asumir temas)
    if not meta["titulo"]:
        meta["titulo"] = "[TÍTULO DE LA MONOGRAFÍA]"
    if not meta["programa"]:
        meta["programa"] = "[NOMBRE DEL PROGRAMA O DIPLOMADO]"
    if not meta["autor"]:
        meta["autor"] = "[Nombre Completo del Postgraduante]"
    if not meta["tutor"]:
        meta["tutor"] = "[Nombre del Docente Guía o Tutor]"

    return meta


# =========================================================================
# Parser Dinámico de Secciones y Contenido Markdown
# =========================================================================

def parsear_bloques_markdown(md_contenido: str) -> list[dict]:
    """
    Convierte el manuscrito Markdown en una lista ordenada de bloques semánticos:
    - heading (nivel 1, 2, 3)
    - paragraph
    - bullet / sub_bullet
    - table (con etiqueta, título y notas asociadas)
    - reference
    """
    lineas = md_contenido.splitlines()
    bloques = []
    i = 0
    total = len(lineas)
    en_referencias = False

    while i < total:
        linea = lineas[i]
        stripped = linea.strip()

        # Separadores horizontales o líneas vacías
        if not stripped or stripped.startswith("---") or stripped.startswith("==="):
            i += 1
            continue

        # Encabezados Markdown
        if stripped.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if match:
                nivel = len(match.group(1))
                texto_enc = match.group(2).strip()

                # Detectar sección de referencias
                if "referencias" in texto_enc.lower():
                    en_referencias = True
                elif "apéndice" in texto_enc.lower() or "anexo" in texto_enc.lower():
                    en_referencias = False

                bloques.append({"tipo": "heading", "nivel": nivel, "texto": texto_enc})
                i += 1
                continue

        # Detección de Tabla Markdown
        if stripped.startswith("|") and stripped.endswith("|"):
            # Retroceder si había una etiqueta o título antes de la tabla
            tabla_num = ""
            tabla_titulo = ""
            if bloques and bloques[-1]["tipo"] == "paragraph":
                posible_tit = bloques.pop()["texto"]
                if bloques and bloques[-1]["tipo"] == "paragraph":
                    posible_lbl = bloques[-1]["texto"]
                    if re.match(r'^\*{0,2}Tabla\s+\d+\*{0,2}', posible_lbl, re.I):
                        tabla_num = re.sub(r'[*_]', '', bloques.pop()["texto"]).strip()
                        tabla_titulo = re.sub(r'[*_]', '', posible_tit).strip()
                    else:
                        bloques.append({"tipo": "paragraph", "texto": posible_tit})
                else:
                    bloques.append({"tipo": "paragraph", "texto": posible_tit})

            filas = []
            while i < total and lineas[i].strip().startswith("|") and lineas[i].strip().endswith("|"):
                f_raw = lineas[i].strip()
                # Omitir fila separadora |--|--|
                if not re.match(r'^\|(?:\s*:?-+:?\s*\|)+$', f_raw):
                    celdas = [c.strip() for c in f_raw[1:-1].split("|")]
                    filas.append(celdas)
                i += 1

            # Verificar si la siguiente línea es una Nota de tabla
            nota_texto = ""
            if i < total:
                prox = lineas[i].strip()
                if re.match(r'^\*{0,2}Nota[\.:]\*{0,2}', prox, re.I):
                    nota_texto = re.sub(r'^\*{0,2}Nota[\.:]\*{0,2}\s*', '', prox).rstrip('*_').strip()
                    i += 1

            bloques.append({
                "tipo": "table",
                "label": tabla_num,
                "title": tabla_titulo,
                "rows": filas,
                "note": nota_texto
            })
            continue

        # Viñetas y listas
        if re.match(r'^\s*([•\*\-]|\d+[\.\)])\s+', linea):
            indent_espacios = len(linea) - len(linea.lstrip(' '))
            texto_item = re.sub(r'^\s*([•\*\-]|\d+[\.\)])\s+', '', linea).strip()

            # Extraer prefijo en negrita si existe (ej. **OE1:**)
            bold_prefix = ""
            m_bold = re.match(r'^\*\*([^*]+)\*\*:?\s*(.*)$', texto_item)
            if m_bold:
                bold_prefix = m_bold.group(1) + ":"
                texto_item = m_bold.group(2).strip()

            tipo_lista = "sub_bullet" if indent_espacios >= 3 else "bullet"
            bloques.append({
                "tipo": tipo_lista,
                "bold_prefix": bold_prefix,
                "texto": texto_item
            })
            i += 1
            continue

        # Referencias (si estamos en la sección de referencias)
        if en_referencias:
            bloques.append({"tipo": "reference", "texto": stripped})
            i += 1
            continue

        # Párrafo regular (acumular líneas contiguas que no sean encabezados ni tablas)
        parr_lineas = [stripped]
        i += 1
        while i < total:
            sig = lineas[i].strip()
            if not sig or sig.startswith("#") or sig.startswith("|") or sig.startswith("---") or re.match(r'^\s*([•\*\-]|\d+[\.\)])\s+', lineas[i]):
                break
            parr_lineas.append(sig)
            i += 1

        bloques.append({"tipo": "paragraph", "texto": " ".join(parr_lineas)})

    return bloques


# =========================================================================
# Constructor del Documento Word Oficial
# =========================================================================

def compilar_monografia_docx(md_path: Path, docx_path: Path, overrides: dict = None, generar_revision: bool = True) -> Path:
    """Compila dinámicamente un manuscrito Markdown a DOCX bajo estándares EIP-FINOR y APA 7."""
    if not md_path.exists():
        raise FileNotFoundError(f"No se encontró el manuscrito Markdown en: {md_path}")

    md_contenido = md_path.read_text(encoding="utf-8")
    meta = extraer_metadatos(md_contenido, overrides)

    plantilla_base = plantilla()
    if not plantilla_base.exists():
        raise FileNotFoundError(f"No se encontró la plantilla oficial Word en: {plantilla_base}")

    print(f"Cargando plantilla institucional: {plantilla_base.name}")
    doc = docx.Document(str(plantilla_base))
    enable_update_fields_on_open(doc)

    # -------------------------------------------------------------------------
    # 1. CARÁTULA INSTITUCIONAL (Sección 0, 10/11 Elementos Normativos)
    # -------------------------------------------------------------------------
    print("Ensamblando Carátula Institucional agnóstica...")
    logo_file = logo_actual() or archivo_salida("logo.png")

    if len(doc.paragraphs) > 0:
        p0 = doc.paragraphs[0]
        p0.text = "UNIVERSIDAD AUTÓNOMA GABRIEL RENÉ MORENO"
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p0.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    if len(doc.paragraphs) > 1:
        p1 = doc.paragraphs[1]
        p1.text = "FACULTAD INTEGRAL DEL NORTE (FINOR)"
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p1.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    if len(doc.paragraphs) > 2:
        p2 = doc.paragraphs[2]
        p2.text = "ESCUELA INTEGRAL DE POSTGRADO (EIP)"
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p2.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    if len(doc.paragraphs) > 3:
        p3 = doc.paragraphs[3]
        p3.text = ""
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_before = Pt(6)
        p3.paragraph_format.space_after = Pt(12)
        if logo_file and Path(logo_file).exists():
            r_logo = p3.add_run()
            r_logo.add_picture(str(logo_file), width=Inches(1.8))
            print(f"✔ Logotipo institucional insertado: {Path(logo_file).name}")
        else:
            r_lbl = p3.add_run("[ LOGO INSTITUCIONAL UAGRM ]")
            r_lbl.font.name = 'Arial'
            r_lbl.font.size = Pt(10)
            r_lbl.italic = True

    if len(doc.paragraphs) > 4:
        p4 = doc.paragraphs[4]
        prog_txt = meta["programa"]
        p4.text = prog_txt if prog_txt.upper().startswith("DIPLOMADO EN") else f"Diplomado en {prog_txt}"
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p4.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    if len(doc.paragraphs) > 5:
        p5 = doc.paragraphs[5]
        p5.text = f"MENCIÓN: {meta['mencion'].upper()}" if meta.get("mencion") else ""
        p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p5.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = True

    if len(doc.paragraphs) > 6:
        p6 = doc.paragraphs[6]
        # Título en Title Case, sin punto final
        p6.text = meta["titulo"].rstrip(".")
        p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p6.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    if len(doc.paragraphs) > 7:
        p7 = doc.paragraphs[7]
        prog_clean = meta["programa"].replace("Diplomado en", "").replace("DIPLOMADO EN", "").strip()
        p7.text = f"Monografía de Compilación presentada para optar al título de Diplomado en {prog_clean}"
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p7.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    if len(doc.paragraphs) > 8:
        p8 = doc.paragraphs[8]
        p8.text = f"Postgraduante: {meta['autor']}"
        p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p8.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = True

    if len(doc.paragraphs) > 9:
        p9 = doc.paragraphs[9]
        p9.text = f"Docente Guía / Tutor: {meta['tutor']}"
        p9.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p9.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    if len(doc.paragraphs) > 10:
        p10 = doc.paragraphs[10]
        p10.text = f"{meta['lugar']}, Gestión {meta['gestion']}"
        p10.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p10.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    # Configuración de carátula (número invisible)
    sec_caratula = doc.sections[0]
    sec_caratula.different_first_page_header_footer = False
    set_section_page_numbering(sec_caratula, num_format="decimal", start_at=1)

    # Limpiar cualquier contenido restante de la plantilla
    remove_template_toc(doc)
    p_elements = [p._p for p in doc.paragraphs[11:]]
    for p_elem in p_elements:
        p_elem.getparent().remove(p_elem)

    # -------------------------------------------------------------------------
    # Parseo de Bloques del Manuscrito
    # -------------------------------------------------------------------------
    bloques = parsear_bloques_markdown(md_contenido)

    # Separar preliminares (Resumen y Palabras clave) del cuerpo principal
    resumen_bloques = []
    cuerpo_bloques = []
    en_resumen = False

    for b in bloques:
        if b["tipo"] == "heading" and "resumen" in b["texto"].lower():
            en_resumen = True
            continue
        elif b["tipo"] == "heading" and en_resumen:
            en_resumen = False
            cuerpo_bloques.append(b)
        elif en_resumen:
            resumen_bloques.append(b)
        elif not en_resumen and b["tipo"] == "heading" and b["texto"].lower() in (
            "ficha técnica de proyecto (p0)", "ficha de proyecto"
        ):
            # Omitir Ficha Técnica P0 del cuerpo formal del DOCX si viene en el markdown
            continue
        elif not en_resumen and b["tipo"] == "heading" and b["texto"] == meta["titulo"]:
            # Omitir el título de la carátula si ya fue colocado en portada
            continue
        else:
            cuerpo_bloques.append(b)

    # -------------------------------------------------------------------------
    # 2. PRELIMINARES: RESUMEN E ÍNDICE DE CONTENIDO (Sección 1, PAG-1)
    # -------------------------------------------------------------------------
    print("Construyendo Preliminares (Resumen, Palabras clave, Índice)...")
    sec_prelim = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_page_numbering(sec_prelim, num_format="lowerRoman", start_at=2)

    p_res_tit = doc.add_paragraph()
    p_res_tit.style = doc.styles['Normal']
    p_res_tit.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_res_tit.paragraph_format.space_before = Pt(18)
    p_res_tit.paragraph_format.space_after = Pt(18)
    r_res = p_res_tit.add_run("Resumen")
    r_res.font.name = 'Times New Roman'
    r_res.font.size = Pt(12)
    r_res.bold = True

    # Párrafo único de resumen
    res_textos = []
    kw_line = ""
    for b in resumen_bloques:
        t = b.get("texto", "")
        if re.search(r'palabras\s+clave\s*:', t, re.I):
            kw_line = t
        else:
            res_textos.append(t)

    res_parrafo_final = " ".join(res_textos) if res_textos else "El presente manuscrito aborda la compilación documental..."
    add_formatted_paragraph(
        doc,
        res_parrafo_final,
        style='Normal',
        first_line_indent=0.0,
        line_spacing=2.0,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    # Palabras clave
    if kw_line:
        m_kw = re.search(r'palabras\s+clave\s*:\s*(.*)$', kw_line, re.I)
        kw_val = m_kw.group(1).strip().rstrip(".") if m_kw else kw_line
    else:
        kw_val = "[Palabras clave no provistas]"

    p_kw = doc.add_paragraph()
    p_kw.style = doc.styles['Normal']
    p_kw.paragraph_format.first_line_indent = Inches(0.0)
    p_kw.paragraph_format.line_spacing = 2.0
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(0)
    p_kw.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kw_lbl = p_kw.add_run("Palabras clave: ")
    r_kw_lbl.italic = True
    r_kw_lbl.font.name = 'Times New Roman'
    r_kw_lbl.font.size = Pt(12)
    r_kw_v = p_kw.add_run(kw_val)
    r_kw_v.font.name = 'Times New Roman'
    r_kw_v.font.size = Pt(12)

    # Índice de contenido
    doc.add_page_break()
    p_idx_tit = doc.add_paragraph()
    p_idx_tit.style = doc.styles['Normal']
    p_idx_tit.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_idx_tit.paragraph_format.space_before = Pt(18)
    p_idx_tit.paragraph_format.space_after = Pt(18)
    r_idx = p_idx_tit.add_run("Índice de Contenido")
    r_idx.font.name = 'Times New Roman'
    r_idx.font.size = Pt(12)
    r_idx.bold = True

    add_toc_field(doc)

    # -------------------------------------------------------------------------
    # 3. CUERPO PRINCIPAL (Sección 2, PAG-2: Arábigos reiniciando en 1)
    # -------------------------------------------------------------------------
    print("Construyendo Cuerpo Principal dinámico...")
    sec_body = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_page_numbering(sec_body, num_format="decimal", start_at=1)
    configure_pagination(doc)

    for b in cuerpo_bloques:
        tipo = b["tipo"]

        if tipo == "heading":
            txt = b["texto"].strip()
            nivel = b["nivel"]

            # Si es Apéndice o Referencias, suprimir numeración automática
            es_apendice = txt.lower().startswith("apéndice") or txt.lower().startswith("anexo")
            es_referencias = "referencias" in txt.lower()

            if es_apendice:
                doc.add_page_break()
                p_head = doc.add_paragraph(txt, style='Heading 1')
                disable_auto_numbering(p_head)
            elif es_referencias:
                doc.add_page_break()
                p_head = doc.add_paragraph("Referencias", style='Heading 1')
                disable_auto_numbering(p_head)
            else:
                # Quitar numeración manual inicial (ej. '1. Introducción' -> 'Introducción')
                # para que el estilo Heading numerado de Word no duplique el número
                texto_limpio = re.sub(r'^\d+(\.\d+)*\s*[-–—.]?\s*', '', txt).strip()
                if not texto_limpio:
                    texto_limpio = txt

                if nivel == 1:
                    doc.add_paragraph(texto_limpio, style='Heading 1')
                elif nivel == 2:
                    doc.add_paragraph(texto_limpio, style='Heading 2')
                else:
                    doc.add_paragraph(texto_limpio, style='Heading 3')

        elif tipo == "paragraph":
            add_formatted_paragraph(doc, b["texto"])

        elif tipo == "bullet":
            add_bullet_item(doc, b.get("bold_prefix", ""), b["texto"], indent=0.5, hanging=-0.25)

        elif tipo == "sub_bullet":
            add_bullet_item(doc, b.get("bold_prefix", ""), b["texto"], indent=0.85, hanging=-0.25)

        elif tipo == "reference":
            add_reference_paragraph(doc, b["texto"])

        elif tipo == "table":
            if b.get("label"):
                add_table_label(doc, b["label"], b.get("title", ""))

            rows_data = b["rows"]
            if rows_data:
                n_rows = len(rows_data)
                n_cols = max(len(r) for r in rows_data)
                tbl = doc.add_table(rows=n_rows, cols=n_cols)
                tbl.autofit = True

                for r_idx, row in enumerate(tbl.rows):
                    r_vals = rows_data[r_idx]
                    for c_idx, cell in enumerate(row.cells):
                        val = r_vals[c_idx] if c_idx < len(r_vals) else ""
                        p_c = cell.paragraphs[0]
                        p_c.paragraph_format.line_spacing = 1.15
                        p_c.paragraph_format.space_before = Pt(2)
                        p_c.paragraph_format.space_after = Pt(2)
                        r_c = p_c.add_run(val)
                        r_c.font.name = 'Times New Roman'
                        r_c.font.size = Pt(9 if n_cols >= 6 else 10)
                        if r_idx == 0:
                            r_c.bold = True
                            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT

                set_table_apa_borders(tbl)

            if b.get("note"):
                add_table_note(doc, b["note"])

    # -------------------------------------------------------------------------
    # Guardado del Documento con Tolerancia a Fallos
    # -------------------------------------------------------------------------
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        doc.save(str(docx_path))
        print(f"✔ Documento Word generado con éxito en: {docx_path}")
        salida_final = docx_path
    except PermissionError:
        fallback = docx_path.with_name(docx_path.stem + "_actualizado.docx")
        doc.save(str(fallback))
        print(f"⚠ AVISO: '{docx_path.name}' está abierto en Word.")
        print(f"✔ Documento guardado como alternativa en: {fallback}")
        salida_final = fallback

    # Validación de integridad OOXML
    valido, errs = docx_utils.validar_docx(salida_final)
    if valido:
        print(f"✔ Validación OOXML: 100% íntegro y compatible con Word.")
    else:
        print(f"⚠ Advertencias OOXML detectadas: {errs}")

    # Generación de copia complementaria con Control de Cambios para el tutor
    if generar_revision:
        ruta_rev = salida_final.with_name(salida_final.stem + "_revision_tutor.docx")
        try:
            ok_rev = docx_utils.generar_version_revision(salida_final, ruta_rev, autor="Revisión EIP-FINOR-UAGRM")
            if ok_rev:
                print(f"✔ Versión con Control de Cambios generada para el tutor en: {ruta_rev}")
        except Exception as e:
            print(f"⚠ Aviso generando versión con control de cambios: {e}")

    return salida_final


# =========================================================================
# Punto de Entrada CLI
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compilador universal y dinámico de Markdown a Word (.docx) para monografías EIP-FINOR-UAGRM."
    )
    parser.add_argument("markdown", nargs="?", default=None, help="Ruta del archivo Markdown fuente (por defecto output/monografia_completa.md)")
    parser.add_argument("--docx", default=None, help="Ruta de destino del .docx generado")
    parser.add_argument("--titulo", default=None, help="Override del título de la monografía")
    parser.add_argument("--programa", default=None, help="Override del diplomado/programa")
    parser.add_argument("--autor", default=None, help="Override del postgraduante")
    parser.add_argument("--tutor", default=None, help="Override del docente guía o tutor")
    parser.add_argument("--gestion", default=None, help="Override del año de gestión (ej. 2026)")
    parser.add_argument("--lugar", default=None, help="Override del lugar (ej. Santa Cruz de la Sierra, Bolivia)")
    parser.add_argument("--sin-revision", action="store_true", help="No generar la versión complementaria con control de cambios")

    args = parser.parse_args()

    # Resolver archivo markdown fuente
    if args.markdown:
        md_file = Path(args.markdown)
    else:
        md_file = archivo_salida("monografia_completa.md")
        if not md_file.exists():
            # Buscar cualquier archivo .md en output/
            candidatos = list(output_dir(crear=False).glob("*.md"))
            if candidatos:
                md_file = candidatos[0]

    if not md_file.exists():
        print(f"✖ Error: No se encontró el archivo Markdown fuente en {md_file}.")
        print("  Asegúrate de que la monografía en Markdown esté generada antes de compilar a Word.")
        sys.exit(1)

    # Resolver ruta de salida
    if args.docx:
        target_docx = Path(args.docx)
    else:
        target_docx = archivo_salida(NOMBRE_DOCX)

    overrides = {
        "titulo": args.titulo,
        "programa": args.programa,
        "autor": args.autor,
        "tutor": args.tutor,
        "gestion": args.gestion,
        "lugar": args.lugar,
    }

    compilar_monografia_docx(md_file, target_docx, overrides=overrides, generar_revision=not args.sin_revision)


if __name__ == "__main__":
    main()
