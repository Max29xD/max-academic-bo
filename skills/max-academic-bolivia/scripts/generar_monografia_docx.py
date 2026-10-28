"""
Generador del documento Word (.docx) para la Monografía de Compilación EIP-FINOR-UAGRM
basado en la plantilla oficial templates/apa7ma.docx y el texto auditado de output/monografia_completa.md.

Reglas Metodológicas Estrictas (Guía EIP-FINOR-UAGRM 2026 y Normas APA 7.ª edición):
1. CAR · Carátula Institucional: 10 elementos normativos en Arial 14/12 pt, logotipo oficial centrado (assets/logo.png),
   página 'i' con numeración oculta (different_first_page_header_footer = True).
2. PAG · Paginación:
   - Preliminares (Resumen, Palabras clave, Índice): números romanos en minúscula (ii, iii...) en encabezado superior derecho.
   - Cuerpo Principal (a partir de 1. Introducción): reinicia en números arábigos (1, 2, 3...) en encabezado superior derecho.
3. FOR-7 · Títulos en Word: los estilos de título Heading 1 y Heading 2 de la plantilla cuentan con numeración automática;
   los textos de encabezado se insertan sin números manuales ('Introducción', 'Planteamiento del Problema', etc.).
4. FOR-8 · Tablas APA 7: Número en primera línea negrita ('Tabla 1'), título descriptivo en segunda línea cursiva a doble espacio,
   bordes superior, de cabecera e inferior (sin líneas verticales), nota al pie ('Nota.').
5. REF-1..3 · Referencias: Sangría francesa de 1.27 cm (0.5 pulg), interlineado 2.0, títulos en cursiva e hipervínculos activos.
6. APE-3 · Apéndices: Apéndice A con la Matriz de Análisis Bibliográfico (MAB) de 16 fuentes verificadas y Apéndice B con el protocolo de búsqueda.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rutas import NOMBRE_DOCX, archivo_salida, logo as logo_actual, plantilla

TEMPLATE_PATH = plantilla()
OUTPUT_PATH = archivo_salida(NOMBRE_DOCX)
OUTPUT_FALLBACK_PATH = archivo_salida("monografia_compilacion_bolivia_actualizada.docx")
LOGO_PATH = logo_actual() or archivo_salida("logo.png")
SOURCE_MD_PATH = archivo_salida("monografia_completa.md")


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
    set_section_page_numbering(secs[1], num_format="lowerRoman", start_at=2)
    set_section_page_numbering(secs[2], num_format="decimal", start_at=1)

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
    if removed:
        print(f"✔ Índice precargado de la plantilla eliminado ({removed} bloque/s).")


def disable_auto_numbering(paragraph):
    """Suprime la numeración automática heredada del estilo (p. ej. apéndices)."""
    numPr = paragraph._p.get_or_add_pPr().get_or_add_numPr()
    numPr.get_or_add_ilvl().set(qn('w:val'), '0')
    numPr.get_or_add_numId().set(qn('w:val'), '0')


def enable_update_fields_on_open(doc):
    """Configura el documento para que Microsoft Word actualice campos (TOC) al abrirse."""
    element = parse_xml(r'<w:updateFields %s w:val="true"/>' % nsdecls('w'))
    doc.settings.element.append(element)


def add_formatted_paragraph(doc, md_text, style='Normal', first_line_indent=0.5, line_spacing=2.0,
                            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=0):
    """Agrega un párrafo formateado procesando negritas (**texto**) y cursivas (*texto*)."""
    p = doc.add_paragraph()
    p.style = doc.styles[style]
    p.paragraph_format.first_line_indent = Inches(first_line_indent)
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = alignment

    # Regex que separa tokens con negrita, cursiva o código en línea
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


def add_bullet_item(doc, bold_prefix, text):
    """Agrega un ítem de viñeta con formato APA/Times New Roman."""
    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    r_bullet = p.add_run("• ")
    r_bullet.font.name = 'Times New Roman'
    r_bullet.font.size = Pt(12)

    r_bold = p.add_run(bold_prefix)
    r_bold.font.name = 'Times New Roman'
    r_bold.font.size = Pt(12)
    r_bold.bold = True

    # Parse formatting inside bullet text
    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', f" {text}")
    for token in tokens:
        if not token:
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


def add_sub_bullet(doc, md_text):
    """Viñeta de segundo nivel con sangría francesa; el código en línea se compone en Consolas."""
    p = doc.add_paragraph()
    p.style = doc.styles['Normal']
    p.paragraph_format.left_indent = Inches(0.85)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.line_spacing = 2.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    texto = md_text[2:] if md_text.startswith("• ") else md_text
    # Las ecuaciones de búsqueda no se justifican: el espaciado monoespaciado las deforma.
    monoespaciado = "`" in texto
    p.paragraph_format.alignment = (WD_ALIGN_PARAGRAPH.LEFT if monoespaciado
                                   else WD_ALIGN_PARAGRAPH.JUSTIFY)

    r_bullet = p.add_run("• ")
    r_bullet.font.name = 'Times New Roman'
    r_bullet.font.size = Pt(12)

    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', texto)
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
    """Inserta una URL en dos tramos con salto controlado, para que el PID no quede huérfano."""
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


def build_monografia_docx(modo="completa"):
    """
    Construye el documento Word oficial para la Monografía de Compilación EIP-FINOR-UAGRM.
    modo: 'completa' (monografía íntegra con todos los acápites, preliminares y apéndices)
    """
    print(f"Cargando plantilla base: {TEMPLATE_PATH}")
    doc = docx.Document(str(TEMPLATE_PATH))
    enable_update_fields_on_open(doc)

    # =========================================================================
    # 1. CARÁTULA INSTITUCIONAL EIP-FINOR (Sección 0, CAR-1..4)
    # =========================================================================
    print("Configurando Carátula Institucional con logo oficial...")
    # Párrafo 0: Institución
    if len(doc.paragraphs) > 0:
        p0 = doc.paragraphs[0]
        p0.text = "UNIVERSIDAD AUTÓNOMA GABRIEL RENÉ MORENO"
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p0.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    # Párrafo 1: Facultad
    if len(doc.paragraphs) > 1:
        p1 = doc.paragraphs[1]
        p1.text = "FACULTAD INTEGRAL DEL NORTE (FINOR)"
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p1.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    # Párrafo 2: Escuela de Postgrado
    if len(doc.paragraphs) > 2:
        p2 = doc.paragraphs[2]
        p2.text = "ESCUELA INTEGRAL DE POSTGRADO (EIP)"
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p2.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    # Párrafo 3: Logo oficial UAGRM (sustituye el marcador [ LOGO INSTITUCIONAL UAGRM ])
    if len(doc.paragraphs) > 3:
        p3 = doc.paragraphs[3]
        p3.text = ""
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_before = Pt(6)
        p3.paragraph_format.space_after = Pt(12)
        if LOGO_PATH.exists():
            r_logo = p3.add_run()
            r_logo.add_picture(str(LOGO_PATH), width=Inches(1.8))
            print(f"✔ Logo institucional insertado exitosamente: {LOGO_PATH.name}")
        else:
            print(f"⚠ Logo no encontrado en: {LOGO_PATH}")

    # Párrafo 4: Programa
    if len(doc.paragraphs) > 4:
        p4 = doc.paragraphs[4]
        p4.text = "Diplomado en Administración de Bases de Datos y Redes"
        p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p4.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    # Párrafo 5: Mención (se limpia para mantener sobriedad)
    if len(doc.paragraphs) > 5:
        p5 = doc.paragraphs[5]
        p5.text = ""

    # Párrafo 6: Título de la monografía (TIT-5: Title Case, Arial 14 pt, negrita, centrado, sin punto final)
    if len(doc.paragraphs) > 6:
        p6 = doc.paragraphs[6]
        p6.text = "Gestión del Riesgo Tecnológico y Seguridad de Bases de Datos en Entidades Financieras de Bolivia (2021–2026)"
        p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p6.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(14)
            r.bold = True

    # Párrafo 7: Modalidad de grado
    if len(doc.paragraphs) > 7:
        p7 = doc.paragraphs[7]
        p7.text = "Monografía de Compilación presentada para optar al título de Diplomado en Administración de Bases de Datos y Redes"
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p7.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    # Párrafo 8: Autor
    if len(doc.paragraphs) > 8:
        p8 = doc.paragraphs[8]
        p8.text = "Postgraduante: Marcos Leandro Bonilla Borges"
        p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p8.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = True

    # Párrafo 9: Tutor / Guía
    if len(doc.paragraphs) > 9:
        p9 = doc.paragraphs[9]
        p9.text = "Docente Guía / Tutor: Coordinación de Postgrado EIP-FINOR"
        p9.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p9.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    # Párrafo 10: Lugar y Gestión
    if len(doc.paragraphs) > 10:
        p10 = doc.paragraphs[10]
        p10.text = "Santa Cruz de la Sierra, Bolivia, Gestión 2026"
        p10.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p10.runs:
            r.font.name = 'Arial'
            r.font.size = Pt(12)
            r.bold = False

    # Configuración de página de la Carátula (CAR-3: número invisible)
    sec_caratula = doc.sections[0]
    sec_caratula.different_first_page_header_footer = False
    set_section_page_numbering(sec_caratula, num_format="decimal", start_at=1)

    # Eliminar el índice precargado de la plantilla (W1) y el contenido de muestra
    remove_template_toc(doc)
    p_elements = [p._p for p in doc.paragraphs[11:]]
    for p_elem in p_elements:
        p_elem.getparent().remove(p_elem)

    # =========================================================================
    # 2. PRELIMINARES: RESUMEN E ÍNDICE DE CONTENIDO (Sección 1, PAG-1)
    # =========================================================================
    print("Construyendo Sección de Preliminares (Resumen, Palabras clave, Índice)...")
    sec_prelim = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_page_numbering(sec_prelim, num_format="lowerRoman", start_at=2)

    # RESUMEN (RES-1..6): Encabezado centrado negrita sin número automático
    p_res_tit = doc.add_paragraph()
    p_res_tit.style = doc.styles['Normal']
    p_res_tit.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_res_tit.paragraph_format.space_before = Pt(18)
    p_res_tit.paragraph_format.space_after = Pt(18)
    r_res = p_res_tit.add_run("Resumen")
    r_res.font.name = 'Times New Roman'
    r_res.font.size = Pt(12)
    r_res.bold = True

    # Párrafo único de resumen (sin sangría de primera línea, RES-2, interlineado 2.0)
    add_formatted_paragraph(
        doc,
        "La presente monografía de compilación analiza la gestión del riesgo tecnológico y los mecanismos de seguridad aplicados a las bases de datos relacionales en las entidades de intermediación financiera de Bolivia durante el período 2021–2026. La investigación aborda los desafíos operativos derivados de la acelerada adopción de pagos electrónicos en el país, donde la concentración de servicios en la plaza bancaria de Santa Cruz de la Sierra y la alta intensidad transaccional demandan infraestructuras de datos resilientes frente a ciberamenazas y accesos no autorizados. El estudio adoptó un enfoque cualitativo de tipo documental, con diseño no experimental y alcance descriptivo-comparativo, aplicando una revisión sistemática sobre un corpus de dieciséis fuentes académicas y regulatorias verificadas en repositorios oficiales y bases indexadas. Los hallazgos evidencian que las principales amenazas contra los motores de bases de datos corresponden a fallas de control de acceso, configuraciones inseguras e inyecciones de código, mitigables mediante arquitecturas de defensa en profundidad. Se constató que el marco regulatorio boliviano establece directrices obligatorias sobre gestión del riesgo tecnológico, custodia de pistas de auditoría inalterables y planes de continuidad; no obstante, persiste una marcada asimetría en la capacidad técnica de implementación entre bancos corporativos y entidades cooperativas. Asimismo, se determinó que el Cifrado Transparente de Datos (TDE) y el monitoreo continuo de transacciones representan controles indispensables cuya penalización en el rendimiento computacional resulta perfectamente asumible en plataformas contemporáneas. Se concluye que la estabilidad operativa y la confianza en el sistema financiero boliviano demandan superar el cumplimiento meramente documental de la normativa, consolidando prácticas estrictas de menor privilegio administrativo, replicación geográfica comprobada y acortamiento de los umbrales de recuperación ante incidentes.",
        style='Normal',
        first_line_indent=0.0,
        line_spacing=2.0,
        alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    )

    # Palabras clave (RES-5: cursiva en la etiqueta, 5 términos, sin punto final)
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
    r_kw_val = p_kw.add_run("riesgo tecnológico, bases de datos relacionales, seguridad de la información, cifrado de datos, resiliencia operativa")
    r_kw_val.font.name = 'Times New Roman'
    r_kw_val.font.size = Pt(12)

    # ÍNDICE DE CONTENIDO (IND-1..3)
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

    # =========================================================================
    # 3. CUERPO PRINCIPAL (Sección 2, PAG-2: arábigos reiniciando en 1)
    # =========================================================================
    print("Construyendo Cuerpo Principal (Capítulos 1 a 8)...")
    sec_body = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_page_numbering(sec_body, num_format="decimal", start_at=1)
    configure_pagination(doc)

    # -------------------------------------------------------------------------
    # 1. INTRODUCCIÓN (INT-1..5)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Introducción", style='Heading 1')

    add_formatted_paragraph(
        doc,
        "En el ámbito financiero global, la acelerada digitalización de los servicios bancarios ha situado a las bases de datos relacionales en el centro de las operaciones financieras, convirtiéndolas en los activos más sensibles frente a las amenazas informáticas. De acuerdo con el Fondo Monetario Internacional [FMI] (2024), el sector financiero se encuentra expuesto de manera desproporcionada a los ciberataques, lo que constituye un riesgo latente para la estabilidad macrofinanciera y la confianza pública en las redes de pago. Asimismo, las evaluaciones de impacto económico señalan que la industria financiera registró un costo promedio de filtración de datos de USD 6,08 millones durante 2024, situándose un 22 % por encima de la media global intersectorial y con un ciclo medio de identificación y contención de 258 días, que se eleva a 292 días cuando el vector de acceso fueron credenciales robadas (IBM Security, 2024). En este entorno, donde se gestionan saldos, historiales de transferencias e identidades de los cuentahabientes, la protección de la información exige superar las defensas perimetrales convencionales e instaurar controles criptográficos y de acceso avanzados en el propio motor de almacenamiento."
    )
    add_formatted_paragraph(
        doc,
        "En el Estado Plurinacional de Bolivia, esta problemática adquiere una relevancia técnica y operativa prioritaria debido a la rápida expansión de los medios electrónicos de pago. Conforme a los registros oficiales del BCB (2026), el sistema financiero registró durante la gestión 2025 un récord histórico de 892 millones de operaciones mediante códigos QR interoperables, con un crecimiento del 131 % respecto al año previo, movilizando un valor anual equivalente a Bs 357.747 millones con una intensidad transaccional de 1.697 pagos por minuto. Esta transformación en los hábitos transaccionales, favorecida por la gratuidad normativa y la penetración de billeteras digitales (Zimeri David & Saucedo Cuellar, 2025), ha incrementado sustancialmente la carga de concurrencia y la superficie de exposición en los servidores de las entidades de intermediación financiera. Dicha concentración operativa se manifiesta de forma directa en el departamento de Santa Cruz de la Sierra, el cual concentra el 41 % de la cartera de créditos nacional con más de Bs 93.424 millones (ASFI, 2025a), albergando la principal infraestructura de procesamiento del país bajo un contexto marcado por la rotación de talento técnico y asimetrías operativas entre grandes bancos y entidades cooperativas."
    )
    add_formatted_paragraph(
        doc,
        "A pesar de la trascendencia de este proceso, existe una marcada escasez de investigaciones científicas en el medio local: mientras el marco regulatorio nacional articulado por la Ley N.º 393 (2013), la Recopilación de Normas para Servicios Financieros (ASFI, 2018) y la Circular ASFI/885/2025 (ASFI, 2025b) impone mandatos taxativos sobre gestión de riesgo tecnológico, pistas de auditoría y continuidad operativa, son reducidos los estudios empíricos arbitrados que analicen la efectividad técnica y el estado real de implementación de dichos controles en los motores de bases de datos locales. Esta distancia entre la prescripción reglamentaria y la práctica técnica cotidiana expone a las entidades a vulnerabilidades de fraude interno, inyección SQL e interrupciones imprevistas del servicio. Por consiguiente, se justifica plenamente una investigación monográfica de compilación que sistematice la literatura técnica, examine las exigencias normativas vigentes y formule directrices aplicadas para administradores de bases de datos, auditores de sistemas y oficiales de seguridad."
    )
    add_formatted_paragraph(
        doc,
        "Bajo esta fundamentación, el presente trabajo tiene como objetivo general analizar la gestión del riesgo tecnológico y los mecanismos de seguridad aplicados a las bases de datos relacionales en las entidades financieras de Bolivia durante el período 2021–2026, a través de una revisión documental sistemática de la literatura técnica y la normativa regulatoria vigente, para proponer directrices de mitigación frente a incidentes operativos y amenazas cibernéticas. Para dar cumplimiento a dicho propósito, la investigación se articuló en cuatro objetivos específicos orientados a: (a) identificar los vectores de amenaza y vulnerabilidades críticas en motores relacionales, (b) examinar el marco regulatorio emitido por la ASFI, (c) comparar los modelos técnicos de seguridad lógica, cifrado en reposo y auditoría continua, y (d) evaluar las estrategias de continuidad operativa, replicación y planes de recuperación ante desastres (DRP)."
    )
    add_formatted_paragraph(
        doc,
        "El documento se organiza en ocho secciones: tras esta Introducción (sección 1), la sección 2 presenta el Planteamiento del Problema a través del análisis contextual y formula la pregunta de investigación; la sección 3 establece los Objetivos de la Investigación y la matriz de consistencia metodológica; la sección 4 expone la Revisión de la Literatura articulada en cuatro ejes temáticos, evaluando consensos y vacíos de conocimiento; la sección 5 precisa la Definición de Términos y Conceptos clave; la sección 6 desarrolla la Discusión crítica sobre las controversias teóricas y sus implicaciones para el entorno local; la sección 7 sintetiza las Conclusiones correspondientes a los objetivos específicos y general; y la sección 8 reúne las Referencias bibliográficas bajo normas APA 7.ª edición, complementadas por los Apéndices metodológicos de rigor."
    )

    # -------------------------------------------------------------------------
    # 2. PLANTEAMIENTO DEL PROBLEMA (PRO-1..8)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Planteamiento del Problema", style='Heading 1')
    doc.add_paragraph("Presentación del Problema", style='Heading 2')

    add_formatted_paragraph(
        doc,
        "En el ámbito global, la digitalización acelerada de los servicios financieros ha reconfigurado la arquitectura tecnológica de la banca, situando a las bases de datos relacionales entre los activos de mayor valor patrimonial y criticidad operativa. En su análisis sobre riesgo cibernético, el FMI (2024) advierte que el sector financiero experimenta una exposición desproporcionada ante ciberamenazas, cuyos incidentes de gran magnitud pueden comprometer la estabilidad macrofinanciera, la confianza ciudadana y la continuidad de las redes de pago. En consonancia, los estudios de seguridad indican que el costo promedio de una filtración de datos en la industria financiera ascendió a USD 6,08 millones durante 2024, cifra que se situó un 22 % sobre el promedio intersectorial de USD 4,88 millones ; el ciclo medio de identificación y contención de la brecha alcanzó los 258 días y llegó a 292 días cuando el acceso se produjo mediante credenciales robadas (IBM Security, 2024). En este escenario de alta sensibilidad transaccional, los esquemas de seguridad perimetral convencionales resultan insuficientes si el núcleo de almacenamiento carece de controles internos y criptográficos rigurosos."
    )
    add_formatted_paragraph(
        doc,
        "En el contexto regional, el informe de madurez en ciberseguridad elaborado por el Banco Interamericano de Desarrollo y la Organización de los Estados Americanos, en colaboración con el Global Cyber Security Capacity Centre de la Universidad de Oxford, constata avances en la región entre 2020 y 2025 tras evaluar a 30 países, aunque señala persistentes limitaciones de recursos, formación técnica especializada y coordinación institucional (Porrúa et al., 2025). Estos condicionamientos regionales se reflejan con mayor intensidad en intermediarios medianos y entidades cooperativas, generando demoras en la actualización de parches, en la administración estricta de cuentas privilegiadas de administración (DBA) y en la detección oportuna de anomalías transaccionales o inyecciones de código."
    )
    add_formatted_paragraph(
        doc,
        "En el caso de Bolivia, el fenómeno ha cobrado una urgencia evidente debido a la rápida masificación de los instrumentos de pago digital. Conforme al Informe de Vigilancia del Sistema de Pagos 2025 del BCB (2026), durante la gestión 2025 el sistema financiero registró un récord de 892 millones de transferencias mediante códigos QR interoperables, lo que significó un aumento del 131 % frente al año previo y un valor anual transado de Bs 357.747 millones. Esta dinámica produjo una intensidad de hasta 1.697 pagos por minuto (28 por segundo) y una tasa de 229 operaciones electrónicas anuales por habitante, ampliando la carga de procesamiento y la superficie de exposición sobre las bases de datos bancarias. La literatura científica nacional caracteriza este proceso como una transformación estructural del sistema de pagos, originada por la interoperabilidad del estándar QR, la gratuidad regulatoria y el uso masivo de billeteras digitales, con repercusiones directas sobre la resiliencia tecnológica de las instituciones (Zimeri David & Saucedo Cuellar, 2025)."
    )
    add_formatted_paragraph(
        doc,
        "A escala departamental, Santa Cruz de la Sierra constituye la principal plaza económica y financiera del país al concentrar el 41 % de la cartera de créditos nacional, representativa de Bs 93.424 millones al 31 de julio de 2025 (ASFI, 2025a). En esta plaza operan las principales entidades de banca múltiple y entidades de ahorro y crédito, además de albergar infraestructuras tecnológicas que canalizan la mayor parte del flujo transaccional nacional. El medio financiero cruceño afronta, asimismo, una recurrente rotación de especialistas en seguridad de datos y disparidades operativas entre la banca mayor y las cooperativas regionales, elevando la probabilidad de contingencias técnicas sobre sus repositorios centrales."
    )
    add_formatted_paragraph(
        doc,
        "La brecha operativa y de seguridad en el sistema financiero boliviano responde a factores institucionales y técnicos: se manifiesta en la distancia entre los requerimientos normativos de la ASFI (disponibilidad continua del servicio, mínimo privilegio administrativo, registro inalterable de auditoría y resguardo del secreto bancario) y las prácticas descritas en los informes sectoriales, en los que un número considerable de entidades mantiene revisiones manuales o periódicas que dejan ventanas de vulnerabilidad ante accesos indebidos. Al tratarse de una investigación cualitativa de compilación documental, sin mediciones de campo directas, esta brecha se caracteriza conceptualmente a partir de la contrastación documental de los ejes temáticos, sin formular estimaciones aritméticas singulares."
    )
    add_formatted_paragraph(
        doc,
        "Desde el punto de vista teórico y metodológico, la literatura especializada señala que las causas primordiales de tales vulnerabilidades comprenden la gestión de motores de bases de datos heredados (*legacy systems*) vinculados a nuevos servicios digitales, la resistencia a implementar esquemas de Cifrado Transparente de Datos (TDE) por presunciones de pérdida de rendimiento transaccional, y la reducida adopción de herramientas de monitoreo de actividad de bases de datos (DAM) en tiempo real. Esta situación expone a las entidades a contingencias de fraude interno, interrupciones no planificadas de servicio y eventuales responsabilidades regulatorias."
    )
    add_formatted_paragraph(
        doc,
        "En consecuencia, se fundamenta la realización de una investigación monográfica de compilación documental orientada a sistematizar los marcos metodológicos de gestión de riesgo tecnológico y las mejores prácticas de seguridad en bases de datos relacionales, contrastándolos con las disposiciones vigentes en Bolivia. El estudio asume un enfoque cualitativo, de tipo documental, con diseño no experimental y alcance descriptivo-comparativo, guiado por el método analítico-sintético y sin hipótesis, empleando las estadísticas oficiales como fuentes secundarias de contexto. Este esfuerzo busca articular un marco referencial útil para administradores de bases de datos, oficiales de seguridad y auditores de sistemas en el sector financiero nacional."
    )

    doc.add_paragraph("Formulación del Problema", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "¿De qué manera los mecanismos de gestión del riesgo tecnológico y las directrices normativas de la ASFI determinan la seguridad, integridad y resiliencia de las bases de datos relacionales en las entidades de intermediación financiera de Bolivia durante el período 2021–2026, según la literatura científica y técnica disponible?"
    )

    # -------------------------------------------------------------------------
    # 3. OBJETIVOS DE INVESTIGACIÓN (OBJ-1..8)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Objetivos de Investigación", style='Heading 1')

    doc.add_paragraph("Objetivo General", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "Analizar la gestión del riesgo tecnológico y los mecanismos de seguridad aplicados a las bases de datos relacionales en las entidades financieras de Bolivia durante el período 2021–2026, a través de una revisión documental sistemática de la literatura técnica y la normativa regulatoria vigente, para proponer directrices de mitigación frente a incidentes operativos y amenazas cibernéticas."
    )

    doc.add_paragraph("Objetivos Específicos", style='Heading 2')
    add_bullet_item(doc, "OE1:", "Identificar los principales vectores de amenaza, vulnerabilidades y fallas operativas que afectan a los sistemas gestores de bases de datos relacionales en el entorno financiero contemporáneo.")
    add_bullet_item(doc, "OE2:", "Examinar el marco regulatorio emitido por la Autoridad de Supervisión del Sistema Financiero (ASFI) respecto a la gestión de riesgo tecnológico, control de accesos, trazabilidad y resguardo de datos sensibles en Bolivia.")
    add_bullet_item(doc, "OE3:", "Comparar los modelos técnicos de seguridad lógica, mecanismos de cifrado (en reposo y en tránsito) y arquitecturas de auditoría continua implementados en motores de bases de datos corporativos.")
    add_bullet_item(doc, "OE4:", "Evaluar las estrategias de continuidad operativa, esquemas de replicación y protocolos de respaldo/recuperación ante desastres (DRP) orientados a garantizar la alta disponibilidad de los datos en el sistema financiero boliviano.")

    # TABLA 1 (APA 7, FOR-8)
    add_table_label(doc, "Tabla 1", "Matriz de Consistencia Metodológica y Articulación de Objetivos")

    table1_data = [
        ["Pregunta de Investigación", "Objetivo de Investigación", "Eje Temático Previsto", "Conclusión Prevista"],
        [
            "¿De qué manera la gestión del riesgo tecnológico y las directrices de la ASFI determinan la seguridad y resiliencia de las BD en Bolivia (2021–2026)?",
            "Analizar la gestión del riesgo tecnológico y los mecanismos de seguridad en bases de datos del sector financiero boliviano (2021–2026).",
            "Revisión Integral",
            "Conclusión integradora general sobre madurez y resiliencia de las bases de datos bancarias en Bolivia."
        ],
        [
            "¿Cuáles son las principales amenazas y vulnerabilidades que comprometen los motores de BD en el sector financiero?",
            "OE1: Identificar los principales vectores de amenaza y vulnerabilidades en bases de datos relacionales financieras.",
            "Eje 1: Vectores de ataque, inyección SQL y vulnerabilidades críticas en BD bancarias.",
            "Diagnóstico de las vulnerabilidades críticas más frecuentes en motores relacionales bancarios."
        ],
        [
            "¿Qué controles y exigencias técnico-legales impone la normativa boliviana de la ASFI?",
            "OE2: Examinar el marco regulatorio de la ASFI sobre riesgo tecnológico y resguardo de datos en Bolivia.",
            "Eje 2: Normativa ASFI: Circular 885/2025 (Reglamento para Empresas de Tecnología Financiera) y marco vigente de gestión de riesgo operativo y seguridad de la información.",
            "Caracterización de las exigencias normativas obligatorias y brechas de cumplimiento local."
        ],
        [
            "¿Qué modelos técnicos de cifrado y auditoría garantizan la confidencialidad e integridad de las BD?",
            "OE3: Comparar modelos de seguridad lógica, cifrado (TDE, TLS) y auditoría continua en bases de datos.",
            "Eje 3: Cifrado en reposo/tránsito, control de roles (RBAC) y auditoría continua de transacciones.",
            "Determinación de la efectividad técnica del cifrado y auditoría continua frente al fraude interno."
        ],
        [
            "¿Cómo se estructuran los planes de contingencia y respaldos ante fallas catastróficas o ciberataques?",
            "OE4: Evaluar estrategias de continuidad operativa, replicación y planes de recuperación ante desastres (DRP).",
            "Eje 4: Alta disponibilidad, políticas de backup (RTO/RPO) y resiliencia ante incidentes en Bolivia.",
            "Pautas clave de contingencia y resiliencia para garantizar disponibilidad 24/7 de las BD."
        ]
    ]

    tbl1 = doc.add_table(rows=len(table1_data), cols=4)
    tbl1.autofit = False
    tbl1_widths = [Inches(1.6), Inches(1.8), Inches(1.5), Inches(1.6)]
    for r_idx, row in enumerate(tbl1.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = tbl1_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(table1_data[r_idx][c_idx])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)
            if r_idx == 0:
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_table_apa_borders(tbl1)
    add_table_note(doc, "Elaboración propia basada en la Guía Metodológica de Monografía de Compilación (EIP-FINOR-UAGRM, 2026).")

    # -------------------------------------------------------------------------
    # 4. REVISIÓN DE LA LITERATURA (REV-1..13)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Revisión de la Literatura", style='Heading 1')

    # Eje 1
    doc.add_paragraph("Eje 1: Vectores de Amenaza y Vulnerabilidad en Bases de Datos Financieras", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "La literatura técnica coincide en que la seguridad de una base de datos financiera no se ve vulnerada por un único factor, sino por la interacción simultánea entre fallas en el control de acceso, configuraciones inseguras y la explotación directa de la capa de datos. En su evaluación técnica, el OWASP Top 10:2025 sitúa el control de acceso insuficiente (A01), la configuración incorrecta de seguridad (A02) y los fallos de inyección, especialmente la inyección SQL (A05), entre los riesgos de aplicación más críticos del período, los cuales impactan directamente en el repositorio transaccional al permitir la lectura, modificación o eliminación no autorizada de registros (Open Web Application Security Project [OWASP], 2025). Por su parte, la perspectiva económica complementa dicha taxonomía: para la industria financiera internacional, el costo medio de una filtración alcanza USD 6,08 millones, superando el promedio intersectorial, con el agravante de que el compromiso de credenciales figura entre las vías de acceso más recurrentes, situando a los usuarios con privilegios elevados, especialmente al administrador de base de datos, en una posición de alta sensibilidad operativa (IBM Security, 2024). La aparente divergencia entre ambas fuentes se explica en el plano metodológico: OWASP clasifica vectores a partir de auditorías y pruebas en aplicaciones de producción, mientras que IBM Security cuantifica las repercusiones económicas sobre incidentes reportados por industria. Lejos de resultar contradictorias, una delimita las vías de vulneración técnica y la otra dimensiona su impacto patrimonial. En consecuencia, esta investigación adopta la taxonomía de OWASP como marco técnico de diagnóstico y las métricas de IBM Security para fundamentar la priorización de controles e inversiones en seguridad. Para Bolivia, donde el ecosistema de pagos procesó en un año reciente cerca de 892 millones de operaciones QR y hasta 1.697 transacciones digitales por minuto (BCB, 2026), la implicación es directa: un motor de base de datos comprometido escala de incidente técnico a riesgo sistémico en cuestión de minutos."
    )
    add_formatted_paragraph(
        doc,
        "Una segunda línea de la literatura demuestra que la detección automatizada de ataques a bases de datos es viable más allá de los proveedores globales. En un estudio latinoamericano revisado por pares, Añasco Loor et al. aplicaron técnicas de minería de datos a la detección de ataques de inyección SQL sobre sistemas de bases de datos, orientando su propuesta a mejorar la identificación oportuna de intrusiones en entornos con recursos limitados (Añasco Loor et al., 2023). Esta evidencia contrasta con la postura preventiva y arquitectónica de OWASP (2025), que prioriza corregir la vulnerabilidad en origen mediante validación de entradas, diseño seguro y configuración adecuada, antes que detectarla en ejecución. La diferencia se explica por el objeto de análisis: OWASP sintetiza patrones observados en aplicaciones de producción, mientras el estudio ecuatoriano es de naturaleza instrumental y experimental, orientado a datasets y clasificadores; ambos coinciden, sin embargo, en que la capa de datos es el objetivo terminal del atacante. Se sostiene en este trabajo que la detección automatizada es una condición necesaria pero no suficiente, que debe operar como segunda línea de defensa tras la higiene arquitectónica y la administración adecuada de configuraciones. La implicación para el sistema financiero boliviano es favorable: este enfoque analítico resulta aplicable en entidades cooperativas y medianas mediante herramientas abiertas, complementando las exigencias de monitoreo y alerta temprana que la normativa procura instaurar en las instituciones con infraestructura técnica propia."
    )
    add_formatted_paragraph(
        doc,
        "Finalmente, la literatura regional advierte que la exposición de Bolivia no se distingue por vectores exóticos sino por capacidad de respuesta desigual. El análisis regional de Porrúa et al. (2025) caracteriza la ciberseguridad latinoamericana como un problema de brechas estructurales institucionales, tecnológicas y de talento, más que de desconocimiento de las amenazas, con legislación en avance pero ejecución heterogénea entre países y entre tipos de entidad. Esta observación dialoga con la evaluación del FMI (2024), que advierte que el riesgo cibernético recae de manera desproporcionada en el sector financiero por la centralización de datos sensibles y la interconexión creciente de servicios. La concordancia entre ambos es razonable por construcción comparativa: ambos trabajan con agregados regionales y ambos concluyen que el eslabón débil es la capacidad institucional; difieren, en cambio, en su énfasis analítico: el FMI focaliza la estabilidad macrofinanciera, mientras que Porrúa et al. priorizan las capacidades de gobernanza. La postura aquí sostenida es que, en un mercado de escala moderada pero con un crecimiento acelerado de pagos digitales como el boliviano, las brechas de talento documentadas en la región se profundizan en cooperativas y entidades medianas, donde los especialistas técnicos son escasos y la rotación es continua. De ahí que la prioridad en plazas estratégicas como Santa Cruz no radique en identificar amenazas desconocidas, sino en cerrar la distancia existente entre los riesgos ya tipificados por la literatura y la capacidad técnica local para gestionarlos eficazmente."
    )

    # Eje 2
    doc.add_paragraph("Eje 2: Marco Regulatorio Boliviano del Riesgo Tecnológico", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "El ordenamiento boliviano aborda el riesgo tecnológico en tres niveles normativos escalonados que, leídos en conjunto, muestran una prescripción completa pero de grano distinto. En la base, la Ley N.º 393 de Servicios Financieros (2013) instituye al Estado como rector del sistema financiero, consagra la protección del público usuario y la confidencialidad de la información de los clientes, y responsabiliza a las entidades por la solvencia, seguridad y continuidad de sus servicios; con ello convierte la gestión del riesgo tecnológico en obligación legal derivada, no en práctica voluntaria (Ley N.º 393, 2013). A nivel reglamentario, la Recopilación de Normas para Servicios Financieros define el riesgo tecnológico como la posibilidad de sufrir pérdidas por caídas o fallos en los sistemas informáticos o en la transmisión de datos, componente del riesgo operativo que debe gestionarse junto con los riesgos legal y de procesos, e impone instrumentos concretos: manual de procedimientos, identificación y evaluación de riesgos, registro de eventos de pérdida, plan de continuidad del negocio, identificación de procesos críticos y contralor por parte de la unidad de auditoría interna (ASFI, 2018). Metodológicamente ambas normas se complementan: la ley fija principios y la reglamentación los operacionaliza; la divergencia aparente entre amplitud y detalle es, en realidad, la arquitectura prevista de subordinación normativa. La postura de esta monografía es que el nivel reglamentario es la pieza decisiva para las bases de datos, porque es donde el riesgo tecnológico recibe definición operativa y controles verificables. Para Santa Cruz, concentradora del principal parque de entidades de intermediación financiera del país, la implicación es que todo servidor de producción de una entidad supervisada opera ya bajo mandato expreso de gestión, continuidad y auditoría."
    )
    add_formatted_paragraph(
        doc,
        "En el tercer nivel regulatorio, la Circular ASFI/885/2025 para entidades fintech demuestra que el regulador ha traducido la exigencia general en controles técnicos verificables en la era digital. Su texto condiciona la habilitación y operación al despliegue de controles de seguridad de la información sobre infraestructura propia o de terceros: gestión de accesos por confidencialidad, pistas de auditoría protegidas, segregación de ambientes, gestión de cambios, respaldo comprobado y planes de continuidad, entre otros (ASFI, 2025b). Contrastivamente, mientras el Título V de la RNSF razona en términos de gestión de riesgo (identificación, evaluación, control y reporte), la Circular 885/2025 razona en términos de lista de verificación técnica por sistema; la diferencia de grano se explica porque aquella dirige a todo el sistema financiero y esta se dictó para captadoras nacidas 100 % digitales, cuya única razón de ser es la tecnología. Ambos cuerpos coinciden, no obstante, en que la capa de datos es objeto directo de la obligación regulatoria y no un activo implícito. La postura crítica es que el marco boliviano es nominalmente completo al integrar ley, reglamento y circular técnica, pero su eficacia depende de capacidad de verificación del supervisor y de madurez de cumplimiento de las entidades, dimensión en la que la literatura regional marca rezago (Porrúa et al., 2025). La implicación práctica para las entidades cruceñas es doble: aplicar la Circular 885/2025 como referencia técnica aunque no sean fintech, y documentar su cumplimiento, porque el riesgo tecnológico ya está, desde 2013, dentro del perímetro de supervisión."
    )
    add_formatted_paragraph(
        doc,
        "Un ángulo menos discutido de la literatura es el papel que el propio ordenamiento asigna a la auditoría interna como garante del ciclo. El Título V reserva una sección específica al contralor de la unidad de auditoría interna sobre la gestión de riesgo operativo, incluyendo la revisión del registro de eventos y del plan de continuidad (ASFI, 2018), mandato que la Circular 885/2025 replica en la verificación de controles de seguridad (ASFI, 2025b) y que se alinea con el estándar internacional de seguridad de tarjetas, que exige evidencia regular de cumplimiento control por control (PCI SSC, 2024). La convergencia entre una normativa doméstica y un estándar contractual internacional sugiere que la auditoría continua dejó de ser buena práctica para convertirse en requisito cruzado; la divergencia reside en la periodicidad de evaluación: anual y por muestreo en el estándar, frente a la continuidad exigida en la operación diaria de la entidad. La postura de esta monografía es que Bolivia cuenta con el andamiaje necesario para exigir auditoría de bases de datos, pero carece aún de literatura empírica nacional sobre cómo se ejecuta ese mandato en la práctica, vacío que se retoma en el cierre de esta revisión. Para el sistema financiero cruceño, la implicación es que la función de auditoría de sistemas, y no únicamente la de tecnología de la información, necesita consolidarse como línea de defensa formal en todas las entidades, no únicamente en las bancarias grandes."
    )

    # Eje 3
    doc.add_paragraph("Eje 3: Controles Lógicos: Cifrado, Control de Acceso y Auditoría", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "En la capa técnica, la literatura de estándares coincide en un triángulo de control integrado por cifrado en reposo y en tránsito, menor privilegio y auditoría protegida, aunque difiere en cómo justificarlo. El PCI DSS v4.0.1, estándar contractual del ecosistema de tarjetas, hace obligatorio el cifrado criptográfico fuerte para el número de tarjeta almacenado, la gestión segmentada de claves criptográficas y la rotación periódica de credenciales, entre otros controles auditables (PCI SSC, 2024). OWASP, desde su panorama de riesgos de aplicación 2025, sitúa las fallas criptográficas (A04) y el control de acceso insuficiente (A01) entre las categorías de mayor relevancia, señalando que la ausencia de cifrado o de un diseño de accesos correcto convierte cualquier anomalía de aplicación en posibilidad de lectura masiva de datos personales y financieros (OWASP, 2025). El contraste entre ambas perspectivas resulta instructivo: el PCI DSS prescribe qué controles implementar y cómo validarlos ante procesos de auditoría, mientras que OWASP explica las vías por las cuales su omisión compromete el sistema. Metodológicamente, uno es una norma técnica de verificación y el otro una taxonomía empírica de riesgos. Se sostiene aquí que ambos enfoques deben articularse de forma complementaria: el estándar internacional define los requerimientos auditables y la taxonomía de amenazas justifica técnicamente la criticidad de cada salvaguarda frente a vectores de ataque contemporáneos. Para Bolivia, donde el comercio digitalizado crece a tasas superiores a la media regional (BCB, 2026), la implicación es que toda base de datos que respalde pagos debería tratar el cifrado en reposo y la revisión periódica de privilegios como controles de arranque, no como proyecto futuro."
    )
    add_formatted_paragraph(
        doc,
        "La evaluación técnica del cifrado en reposo cuenta con respaldo experimental que dimensiona su impacto computacional. En un estudio arbitrado en *Journal of Big Data*, Madyatmadja et al. evaluaron el comportamiento del Cifrado Transparente de Datos (TDE) sobre la fiabilidad y eficiencia de SQL Server, aportando criterios empíricos para sopesar la relación entre protección y rendimiento en bases de datos en producción (Madyatmadja et al., 2021). Esta evidencia empírica contrasta con la prescripción normativa del PCI DSS: mientras el estándar ordena cifrar sin profundizar en costos computacionales, el estudio examina los efectos de su implementación práctica; la diferencia obedece a las distintas audiencias a las que se dirigen, contraponiendo el cumplimiento regulatorio frente a la administración técnica de bases de datos. Se sostiene aquí que el TDE resulta plenamente viable en entidades financieras si su adopción se evalúa a partir de mediciones técnicas bajo cargas propias, superando la simple réplica de prácticas corporativas. El aporte metodológico del estudio citado radica en demostrar que la penalización de rendimiento es medible, predecible y técnicamente gestionable, más que en formular una tasa fija de sobrecarga computacional. Para las entidades bolivianas, con bases de datos de tamaño moderado pero alta criticidad, la implicación es que el argumento del rendimiento no puede seguir usándose como excusa para postergar la adopción de esquemas criptográficos."
    )
    add_formatted_paragraph(
        doc,
        "En el tercer vértice del triángulo, correspondiente a la auditoría de base de datos, es donde la literatura normativa y la técnica culminan en un sólido consenso operativo. La regulación boliviana exige pistas de auditoría protegidas y restricción de utilitarios de administración en las entidades tecnológicas financieras (ASFI, 2025b), la RNSF añade el contralor por la unidad de auditoría interna del registro de eventos del riesgo operativo (ASFI, 2018), y OWASP (2025) incorpora en su lista de riesgos las fallas de registro y alerta de seguridad (A09), es decir, la incapacidad de detectar una intrusión por falta de cobertura de eventos. La convergencia de fuentes de naturaleza tan diversa (regulación doméstica, estándar contractual y taxonomía de riesgo) se explica porque las tres responden a un aprendizaje común: la mayor parte de las filtraciones en bases de datos fueron detectables de forma temprana en registros que no fueron examinados oportunamente o que carecían de protección adecuada. La divergencia reside en el nivel de especificidad: ninguna de las fuentes obliga nominalmente a una herramienta de monitoreo de actividad de base de datos (DAM), con lo cual queda a criterio técnico de la entidad implementar con SIEM, auditoría nativa del motor o soluciones dedicadas. La postura de esta monografía es que la convergencia regulatorio-técnica es suficiente para declarar la auditoría continua de BD como control mínimo; la implementación debe ser proporcional al tamaño de la entidad. Para las cooperativas cruceñas, la traducción práctica es que el costo marginal de activar la auditoría nativa del motor es pequeño frente al costo reputacional y regulatorio de no detectar un acceso indebido hasta semanas después."
    )

    # Eje 4
    doc.add_paragraph("Eje 4: Continuidad Operativa, Respaldo y Recuperación ante Desastres", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "La continuidad del negocio es el cuarto pilar de la gestión del riesgo tecnológico y el de mayor tradición normativa. El marco referencial internacional clásico, NIST SP 800-34 Rev. 1, estructura el plan de continuidad como un ciclo de siete etapas, abarcando desde el análisis de impacto hasta la recuperación y la reanudación operativa, y define las métricas fundacionales del diseño: objetivos de recuperación (RTO) y objetivos de punto de recuperación (RPO) que acotan cuánto tiempo de inactividad y cuánta pérdida de datos tolera cada proceso crítico (National Institute of Standards and Technology [NIST], 2010). En el plano nacional, el RNSF adopta la misma lógica al imponer el plan de continuidad del negocio como documento obligatorio que permite restaurar funciones críticas ante un evento de riesgo operativo, además de identificar procesos y sistemas críticos (ASFI, 2018). La concordancia es esperable porque la norma boliviana fue inspirada en los estándares internacionales de gestión de riesgo; la diferencia de alcance entre una prescripción genérica y una metodología de implementación obedece a su distinto destinatario: uno guía a profesionales de continuidad, la otra regula a todas las entidades supervisadas. La postura de esta monografía es que el RTO/RPO es el puente traducible entre norma y arquitectura: ninguna decisión de replicación, respaldo o nube debería aprobarse sin esos dos números por proceso crítico. Para el sistema financiero con operación continua en Bolivia, con picos de 1.697 pagos digitales por minuto registrados a 2025 (BCB, 2026), la implicación es que cualquier ventana de inactividad prolongada ya no es tolerable por diseño del negocio, antes incluso de que el regulador la sancione."
    )
    add_formatted_paragraph(
        doc,
        "La literatura técnica reciente muestra que la ingeniería de recuperación avanzó más rápido que la métrica clásica. Unnava demostró que, en arquitecturas de microservicios, la recuperación ante desastres en tiempo real mediante instantáneas coordinadas acorta el RTO tradicional hasta niveles de recuperación prácticamente instantánea para servicios transaccionales críticos, desplazando el paradigma de restauración post-evento hacia uno de continuidad ininterrumpida (Unnava, 2025). Este avance contrasta con las prácticas generalizadas que aún planifican en ventanas de horas, bajo el paradigma formalizado por NIST en 2010; la divergencia se explica por la brecha tecnológica entre generaciones: el RTO clásico presupone centros de datos propios y respaldos diferidos, mientras las entidades fintech, y en general las organizaciones nacidas en la nube, pueden elegir arquitecturas donde el failover es automático. Ambas fuentes, la clásica y la actual, coinciden sin embargo en la lógica de fondo: la continuidad no es un producto que se compra sino una capacidad que se diseña, se prueba y se mantiene. La postura de esta monografía es que el sistema financiero boliviano admite hoy un espectro gradual de madurez, extendido desde el respaldo periódico verificado hasta la conmutación por error casi instantánea, por lo que cada entidad debe posicionarse explícitamente en ese espectro conforme a su RTO/RPO y su apetito de riesgo. Para Santa Cruz, sede del grueso del ecosistema de pagos QR del país, la implicación es estratégica: la entidad que ofrezca continuidad superior comercializa directamente confianza."
    )
    add_formatted_paragraph(
        doc,
        "La pieza más antigua y a la vez más pertinente para el contexto boliviano es la replicación de datos como mecanismo. En un antecedente local ya clásico, Colquehuanca estudió la implementación de modelos heurísticos de replicación en bases de datos, mostrando cómo la sincronización diferida entre sedes sostiene la operación cuando un nodo falla, con control del retardo de propagación (Colquehuanca Javieri, 2015). Este antecedente técnico contrasta productivamente con la solución de instantáneas de Unnava (2025): la replicación asíncrona es viable con infraestructura modesta y geografía difícil como la boliviana, mientras la recuperación instantánea exige plataformas modernas y coste operativo continuo; la diferencia no es de calidad sino de presupuesto y madurez tecnológica. Ambas convergen, no obstante, en un principio que esta monografía eleva a tesis: la copia de respaldo que nunca fue restaurada bajo prueba no acredita continuidad, solo papeleo. Ese principio está presente también en la exigencia regulatoria boliviana de respaldo comprobado (ASFI, 2025b) y en la práctica del sector de tarjetas, que audita la eficacia de la respuesta ante incidentes (PCI SSC, 2024). La conclusión parcial del eje es que Bolivia cuenta con normativa, antecedente técnico local y avances internacionales suficientes para fijar controles de continuidad proporcionalmente ambiciosos, quedando como tarea propia de cada entidad definir su posición en el espectro de madurez."
    )

    # Síntesis
    doc.add_paragraph("Síntesis de Cierre de la Revisión", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "La literatura revisada (2021–2026 en su mayoría, con fuentes fundacionales y normativa vigente) permite precisar tres consensos, dos controversias y un vacío central de conocimiento que fundamenta esta investigación."
    )
    add_formatted_paragraph(
        doc,
        "**Consensos.** Primero, la capa de datos es el blanco terminal de casi todas las clases de riesgo relevantes: la taxonomía de riesgos de aplicación 2025 (OWASP, 2025), las métricas de costo de filtraciones en el sector financiero (IBM Security, 2024) y los análisis macro-financieros (FMI, 2024) apuntan, desde lenguajes distintos, al mismo repositorio transaccional. Segundo, la tríada de cifrado, menor privilegio y auditoría continua es reconocida simultáneamente por el estándar contractual internacional (PCI SSC, 2024), la regulación boliviana (ASFI, 2018, 2025b) y la literatura técnica empírica (Madyatmadja et al., 2021), lo que habilita a declararla control mínimo incluso para entidades medianas. Tercero, el riesgo tecnológico quedó definitivamente incorporado al riesgo operativo supervisado en Bolivia: la definición reglamentaria (ASFI, 2018), la obligación legal de continuidad (Ley N.º 393, 2013) y la circular técnica más reciente (ASFI, 2025b) forman una cadena normativa sin eslabones verosimilmente impugnables."
    )
    add_formatted_paragraph(
        doc,
        "**Controversias.** La primera es el nivel adecuado de prescripción: los estándares internacionales ordenan controles con especificación exacta, mientras la regulación boliviana fija obligaciones de resultado, y la literatura regional (Porrúa et al., 2025) muestra que en América Latina el problema está más en la ejecución y verificación que en la letra; cómo cerrar esa brecha de implementación en entidades de baja capacidad técnica no está resuelto. La segunda es el ritmo tecnológico de la continuidad: la métrica clásica RTO/RPO (NIST, 2010) y las soluciones de recuperación instantánea (Unnava, 2025) conviven en un gradiente de adopción aún pendiente de mapear en mercados emergentes, donde el antecedente local apunta a soluciones de replicación más austeras (Colquehuanca Javieri, 2015)."
    )
    add_formatted_paragraph(
        doc,
        "**Vacíos de conocimiento.** El vacío central, verificado por contraste entre fuentes, es la casi completa ausencia de estudios empíricos bolivianos arbitrados sobre seguridad y gestión de riesgo de bases de datos en entidades financieras: la producción nacional disponible se limita a análisis del ecosistema de pagos y de la economía digital (BCB, 2026; Zimeri David & Saucedo Cuellar, 2025) y a un antecedente técnico sobre replicación anterior al auge QR (Colquehuanca Javieri, 2015), ninguno de los cuales aborda la intersección entre ciberdefensa, bases de datos y regulación financiera boliviana que este trabajo examina. Un vacío secundario es la ausencia de evidencia local sobre la brecha de cumplimiento efectivo entre los controles prescritos y los operados, en términos comparables a la brecha documentada a escala regional, lo cual impide dimensionar el riesgo residual real del sistema. Sobre ambos vacíos se construye la conclusión de esta monografía: caracterizar el estado de gestión del riesgo tecnológico en las entidades financieras bolivianas (2021–2026) a partir de la triangulación entre norma vigente, literatura técnica y datos públicos del supervisor y del banco central, aportando una base organizada para la investigación empírica futura."
    )

    # -------------------------------------------------------------------------
    # 5. DEFINICIÓN DE TÉRMINOS Y CONCEPTOS (TER-1..5)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Definición de Términos y Conceptos", style='Heading 1')

    add_formatted_paragraph(
        doc,
        "A continuación se presentan los conceptos teóricos y técnicos clave que estructuran la presente investigación documental. Cada definición se sustenta en fuentes especializadas de referencia, se delimita en su aplicación al contexto de las entidades de intermediación financiera de Bolivia y se diferencia conceptualmente respecto a nociones afines:"
    )

    terminos = [
        ("Riesgo tecnológico", "La Autoridad de Supervisión del Sistema Financiero (ASFI, 2018) define el riesgo tecnológico como la posibilidad de experimentar pérdidas económicas originadas por caídas, vulnerabilidades o fallos en los sistemas informáticos, aplicaciones o en la transmisión electrónica de datos. En esta investigación, el concepto se delimita a las amenazas operativas y ciberataques dirigidos contra motores de bases de datos relacionales en entidades financieras de Bolivia. Se distingue del riesgo operativo general porque atañe exclusivamente a la infraestructura digital y al procesamiento de datos, y no a errores humanos o procedimientos manuales administrativos."),
        ("Inyección SQL", "El Open Web Application Security Project (OWASP, 2025) define la inyección SQL como una clase crítica de falla de seguridad en la cual datos no confiables ingresados por el usuario son interpretados como comandos de consulta por el motor de base de datos relacional. En esta monografía, se aplica como el principal vector de vulnerabilidad externa sobre plataformas bancarias y pagos QR en Bolivia. Se diferencia del control de acceso roto en que este último abusa de privilegios existentes, mientras que la inyección subvierte la lógica de consulta para extraer o alterar datos no autorizados."),
        ("Cifrado de datos en reposo (TDE)", "El PCI Security Standards Council (2024) conceptualiza el cifrado en reposo como el mecanismo criptográfico que vuelve ilegibles los datos de cuentas almacenados físicamente en tablas, archivos de datos y respaldos. En la presente monografía, se delimita al Cifrado Transparente de Datos (TDE) aplicado a motores transaccionales del sistema financiero boliviano para resguardar la confidencialidad de los saldos y transacciones. Se distingue del cifrado en tránsito, dado que protege los archivos almacenados en almacenamiento persistente frente a filtraciones de disco, y no paquetes durante su transmisión por redes."),
        ("Control de acceso basado en roles (RBAC)", "OWASP (2025) define el control de acceso como la imposición de directrices de seguridad que impiden que los usuarios actúen fuera de los permisos asignados. En esta investigación, se operacionaliza bajo el modelo RBAC (*Role-Based Access Control*), restringiendo estrictamente los privilegios de los administradores de base de datos (DBAs) y servicios transaccionales en bancos bolivianos bajo el principio de mínimo privilegio. Se distingue de la autenticación porque esta última únicamente verifica la identidad del usuario, mientras que el control de acceso define qué acciones específicas puede ejecutar sobre los esquemas y tablas."),
        ("Auditoría continua de base de datos", "La Autoridad de Supervisión del Sistema Financiero (ASFI, 2025b) prescribe las pistas de auditoría protegidas como el registro inalterable y cronológico de accesos, modificaciones y transacciones ejecutadas en sistemas de información. En este estudio, se delimita a la captura y monitoreo sistemático de eventos DDL y DML sobre bases de datos bancarias en Bolivia. Se distingue de la auditoría tradicional periódica en que esta última se realiza mediante muestreos diferidos en el tiempo, mientras que la auditoría continua inspecciona eventos en tiempo real o casi real alertando anomalías de manera preventiva."),
        ("Objetivo de tiempo de recuperación (RTO)", "El National Institute of Standards and Technology (NIST, 2010) define el RTO (*Recovery Time Objective*) como el período máximo tolerable durante el cual un sistema de información puede permanecer inactivo tras un desastre o incidente antes de causar un daño inaceptable al negocio. En esta investigación, se aplica a los tiempos de restauración de motores de bases de datos de pago e intermediación financiera en Bolivia. Se distingue del RPO porque el RTO cuantifica la duración admisible de interrupción del servicio, mientras que el RPO mide la pérdida de información transaccional permitida."),
        ("Objetivo de punto de recuperación (RPO)", "NIST (2010) define el RPO (*Recovery Point Objective*) como el volumen máximo admisible de pérdida de datos ante una contingencia, medido en tiempo de transacciones no recuperables. En el contexto de la banca y fintechs en Bolivia, se delimita a la cota máxima de transacciones financieras o registros de saldos que pueden perderse entre el último respaldo o replicación y la caída del motor. Se diferencia del RTO porque no cuantifica el tiempo transcurrido hasta reiniciar operaciones, sino la vigencia y pérdida aceptable del conjunto de datos."),
        ("Replicación asíncrona de base de datos", "Colquehuanca Javieri (2015) conceptualiza la replicación asíncrona como la técnica de propagación diferida de operaciones desde una base de datos principal hacia uno o más nodos réplica, donde la confirmación de la transacción local no queda bloqueada por la sincronización remota. En esta monografía, se delimita a la arquitectura de contingencia geográfica utilizada por entidades financieras en Bolivia para resguardar la disponibilidad entre sedes. Se distingue de la replicación síncrona en que no penaliza la latencia transaccional primaria de pagos masivos, asumiendo un margen controlado de RPO.")
    ]

    for term_title, term_def in terminos:
        add_formatted_paragraph(
            doc,
            f"**{term_title}:** {term_def}",
            style='Normal',
            first_line_indent=0.5,
            line_spacing=2.0,
            alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
        )

    # -------------------------------------------------------------------------
    # 6. DISCUSIÓN (DIS-1..5)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Discusión", style='Heading 1')

    doc.add_paragraph("Apertura y Cumplimiento de la Pregunta Motora y el Objetivo General", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "La presente investigación documental tuvo como propósito central analizar la gestión del riesgo tecnológico y los mecanismos de seguridad aplicados a las bases de datos relacionales en las entidades financieras de Bolivia durante el período 2021–2026, orientándose a dilucidar de qué manera las directrices de la ASFI y las mejores prácticas internacionales determinan la integridad y resiliencia de la infraestructura de datos. Tras la sistematización y triangulación de la literatura técnica y regulatoria, es posible afirmar que la revisión sistemática respondió a la pregunta motora y al objetivo general formulado. La evidencia examinada demuestra que la seguridad de las bases de datos financieras en el entorno boliviano no depende de controles aislados ni de soluciones perimetrales convencionales, sino de una articulación estructural en tres dimensiones interdependientes: el cumplimiento de las directrices obligatorias emanadas de la regulación supervisada (ASFI, 2018, 2025b; Ley N.º 393, 2013), la adopción rigurosa de controles criptográficos y de acceso en la capa de datos (OWASP, 2025; PCI SSC, 2024), y el diseño de planes de contingencia operacional orientados a la alta disponibilidad (NIST, 2010; Unnava, 2025). En este sentido, la literatura evidencia que el riesgo tecnológico se ha transformado en el principal factor de vulnerabilidad operativa para el sistema financiero boliviano, impulsado por el notable crecimiento del volumen transaccional digital documentado por el BCB (2026)."
    )

    doc.add_paragraph("Análisis Comparativo: Confrontación Crítica, Convergencias y Divergencias", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "El contraste analítico entre los cuerpos teóricos y normativos revisados revela convergencias sustantivas respecto a la criticidad de los activos de datos, pero expone marcadas divergencias epistemológicas y metodológicas en cuanto a los enfoques de mitigación y evaluación del rendimiento."
    )
    add_formatted_paragraph(
        doc,
        "En primer lugar, respecto a los vectores de amenaza, se constata una convergencia técnica entre la taxonomía de fallas de aplicación de OWASP (2025) y los estudios de impacto financiero global (FMI, 2024; IBM Security, 2024). Ambas vertientes coinciden en señalar que las brechas de control de acceso y las inyecciones SQL constituyen las vías primordiales mediante las cuales se comprometen los repositorios transaccionales. No obstante, surge una divergencia conceptual: mientras OWASP (2025) aborda el fenómeno desde una óptica puramente preventiva y de diseño arquitectónico seguro, IBM Security (2024) y el FMI (2024) evalúan el problema desde sus repercusiones macroeconómicas y financieras, al situar el costo promedio de las filtraciones bancarias en USD 6,08 millones, con un ciclo de identificación y contención de 258 días, que se eleva a 292 días cuando el acceso se produjo mediante credenciales robadas. Por su parte, la literatura experimental regional representada por Añasco Loor et al. (2023) introduce un enfoque complementario al demostrar la viabilidad de detectar inyecciones SQL mediante algoritmos de minería de datos en ejecución; dicha perspectiva contrasta con la rigidez de las listas de chequeo normativas, lo que demuestra que la protección de bases de datos demanda combinar higiene estricta de código con modelos dinámicos de detección temprana adaptables a presupuestos restringidos."
    )
    add_formatted_paragraph(
        doc,
        "En segundo término, en el ámbito de los controles lógicos y el cifrado, se evidencia una controversia central entre la exigencia normativa y el costo computacional. Por un lado, los estándares internacionales como el PCI DSS v4.0.1 (PCI SSC, 2024) y las regulaciones locales (ASFI, 2025b) prescriben de forma taxativa el cifrado seguro de los datos en reposo y el resguardo inalterable de pistas de auditoría como condiciones no negociables de operación. Por otro lado, la investigación empírica de Madyatmadja et al. (2021) aporta evidencia experimental decisiva al medir cuantitativamente el impacto y penalización del Cifrado Transparente de Datos (TDE) sobre la eficiencia y tiempo de respuesta en motores SQL Server. Esta divergencia entre el mandato regulatorio abstracto y la realidad operativa de los servidores de bases de datos explica por qué numerosas entidades financieras intermedias han postergado la activación de esquemas criptográficos en reposo, escudándose en una presunta degradación inmanejable del rendimiento transaccional. La evidencia revisada demuestra que tal impacto es gestionable si la infraestructura se dimensiona adecuadamente."
    )
    add_formatted_paragraph(
        doc,
        "En tercer término, en el eje de la continuidad del negocio y resiliencia ante desastres, la literatura confronta el paradigma tradicional frente a los avances tecnológicos recientes. La guía clásica de NIST (2010) conceptualiza la continuidad operativa a través de umbrales cuantitativos de RTO y RPO soportados en copias de seguridad periódicas y procedimientos estructurados de restauración diferida. En contraste, la literatura reciente analizada por Unnava (2025) plantea el desplazamiento hacia arquitecturas de instantáneas en microservicios capaces de reducir el RTO a umbrales mínimos, habilitando una recuperación transaccional casi instantánea en plataformas financieras nativas de la nube. Entre ambos extremos, el antecedente nacional de Colquehuanca Javieri (2015) ofrece un anclaje pragmático intermedio para economías emergentes, lo que comprueba que la replicación asíncrona desacopla los servidores transaccionales y preserva la disponibilidad geográfica entre nodos remotos sin requerir las costosas infraestructuras propietarias de los esquemas síncronos continuos."
    )

    doc.add_paragraph("Voz y Postura Crítica del Investigador", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "Frente a las controversias detectadas en la literatura científica, la postura crítica que se asume en esta monografía es que la seguridad de bases de datos en las entidades financieras no puede gestionarse como un mero ejercicio burocrático de cumplimiento documental (*compliance*) ni como una simple acumulación de herramientas tecnológicas desarticuladas. La posición teórica fundamentada en este estudio sostiene que el marco normativo boliviano vigente, integrado por la Ley N.º 393 (2013), el Título V del RNSF (ASFI, 2018) y la Circular ASFI/885/2025 (ASFI, 2025b), establece un andamiaje regulatorio completo y técnicamente estructurado en su formulación, pero cuya efectividad real se encuentra condicionada por una marcada asimetría de capacidades técnicas de supervisión y ejecución operativa."
    )
    add_formatted_paragraph(
        doc,
        "Asimismo, el análisis realizado permite afirmar que el dilema clásico entre seguridad y rendimiento transaccional expuesto por Madyatmadja et al. (2021) carece de justificación técnica válida en el entorno contemporáneo. Con la disponibilidad de procesadores con aceleración criptográfica por hardware y motores de bases de datos con esquemas TDE optimizados, el costo marginal de cómputo resulta insignificante frente al riesgo de pérdidas económicas y reputacionales documentado por IBM Security (2024). Por consiguiente, esta investigación sostiene que las entidades financieras bolivianas deben adoptar decididamente un modelo de defensa en profundidad donde el cifrado en reposo, la segregación de privilegios administrativos mediante RBAC y la auditoría continua (DAM) se apliquen de forma simultánea, superando nociones desactualizadas sobre el impacto en el rendimiento transaccional."
    )

    doc.add_paragraph("Implicaciones Contextuales para Bolivia y Santa Cruz de la Sierra", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "Los hallazgos teóricos y normativos analizados cobran directa pertinencia al examinarse en el contexto del sistema financiero boliviano, en particular en la plaza de Santa Cruz de la Sierra. La notable expansión de los pagos electrónicos reportada por el BCB (2026), sustentada en 892 millones de transacciones por código QR en 2025 y picos de 1.697 pagos por minuto, ha transformado de manera sustantiva las condiciones de riesgo operacional del país (Zimeri David & Saucedo Cuellar, 2025). En este nuevo escenario, los motores de bases de datos relacionales operan bajo un régimen transaccional continuo durante las veinticuatro horas del día."
    )
    add_formatted_paragraph(
        doc,
        "En dicha coyuntura, Santa Cruz de la Sierra se sitúa en el centro de la exposición tecnológica nacional al concentrar el 41 % de la cartera de créditos del Sistema Financiero Nacional, superando los Bs 93.424 millones (ASFI, 2025a). La plaza cruceña concentra los principales centros de cómputo del país, el mayor flujo transaccional y los requisitos más exigentes de disponibilidad ininterrumpida. Sin embargo, en concordancia con el diagnóstico regional de Porrúa et al. (2025), el medio financiero local afronta dos restricciones estructurales: la rotación continua de profesionales especializados en administración y seguridad de bases de datos relacionales, y una marcada disparidad técnica entre la gran banca múltiple y las entidades cooperativas o de ahorro y crédito regionales. Mientras las instituciones bancarias mayores disponen de recursos para implementar infraestructuras redundantes con recuperación casi instantánea (Unnava, 2025) y auditoría automatizada, las cooperativas intermedias mantienen procesos de respaldo periódicos que conllevan ventanas de exposición frente a las exigencias de resiliencia de la ASFI (2018). Si un incidente de seguridad o una falla imprevista afectara los repositorios de una entidad relevante en Santa Cruz, las consecuencias no serían meramente patrimoniales, sino que comprometerían la cadena de pagos y la estabilidad del sistema financiero regional."
    )

    doc.add_paragraph("Limitaciones de la Literatura y Futuras Líneas de Investigación", style='Heading 2')
    add_formatted_paragraph(
        doc,
        "Finalmente, resulta indispensable precisar las limitaciones metodológicas y documentales que enmarcaron el desarrollo del presente estudio. La principal restricción detectada en el estado del arte radica en la escasez de investigaciones científicas y estudios empíricos arbitrados sobre la gestión de riesgo tecnológico y seguridad de bases de datos en instituciones financieras de Bolivia al corte de 2026. Si bien existen reportes del BCB (2026), notas estadísticas de la ASFI (2025a) y análisis sobre el desarrollo de los medios de pago (Zimeri David & Saucedo Cuellar, 2025), la literatura nacional carece de mediciones de campo que cuantifiquen el estado real de adopción del cifrado TDE, la configuración efectiva de privilegios en motores relacionales o los tiempos medios de recuperación (RTO medido) en centros de cómputo bolivianos. Gran parte de los parámetros técnicos debieron inferirse a partir de investigaciones internacionales (Madyatmadja et al., 2021; Unnava, 2025; Añasco Loor et al., 2023) y diagnósticos regionales agregados (Porrúa et al., 2025)."
    )
    add_formatted_paragraph(
        doc,
        "A partir de estas limitaciones, se perfilan con claridad las líneas de investigación prioritarias para el futuro:"
    )
    add_bullet_item(doc, "1.", "Conducción de estudios empíricos aplicados que midan cuantitativamente la degradación de rendimiento y latencia transaccional provocada por el cifrado en reposo (TDE) sobre cargas de trabajo de pagos masivos QR en entidades de intermediación financiera de Bolivia.")
    add_bullet_item(doc, "2.", "Desarrollo y evaluación de modelos de auditoría continua y detección de anomalías transaccionales basados en minería de datos y aprendizaje automático adaptados a la infraestructura de cooperativas y entidades financieras medianas de Santa Cruz.")
    add_bullet_item(doc, "3.", "Evaluación comparativa de la resiliencia operativa y tiempos reales de failover entre arquitecturas de replicación asíncrona tradicionales y esquemas modernos de microservicios distribuidos en centros de datos locales y nubes híbridas reguladas en Bolivia.")

    # -------------------------------------------------------------------------
    # 7. CONCLUSIONES (CON-1..5)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Conclusiones", style='Heading 1')

    add_formatted_paragraph(
        doc,
        "En relación con el primer objetivo específico, orientado a identificar los vectores de amenaza y vulnerabilidades en motores de bases de datos relacionales, la revisión documental demostró que los principales riesgos no provienen de técnicas imprevistas, sino de la convergencia recurrente entre inyecciones SQL, debilidades en el control de acceso y errores en la configuración de seguridad. A través del análisis de las fuentes, se constató que tales fallas comprometen directamente los repositorios transaccionales, habilitando la extracción de credenciales y la manipulación de saldos de los clientes. Asimismo, se evidenció que los altos costos asociados a la pérdida de datos y las extensas ventanas de detección convierten a la capa de datos en el blanco principal de los ciberataques contra entidades bancarias. En el contexto de Bolivia, esta exposición se incrementó notablemente con la rápida masificación de los pagos digitales. Por consiguiente, se concluyó que la protección de las bases de datos bancarias exige trascender la defensa perimetral e implementar controles de validación rigurosa de consultas junto con esquemas automatizados de detección de anomalías."
    )
    add_formatted_paragraph(
        doc,
        "Respecto al segundo objetivo específico, enfocado en examinar el marco regulatorio de la ASFI en materia de riesgo tecnológico, la sistematización normativa permitió verificar que Bolivia posee una estructura jurídica escalonada que articula mandatos a nivel legal, reglamentario y operativo especializado. Se comprobó que la normativa sectorial integra la gestión del riesgo tecnológico dentro del riesgo operativo general, haciendo obligatorios el registro de eventos de pérdida, los planes de continuidad del negocio y el control permanente por parte de la auditoría interna. De igual manera, se constató que las circulares regulatorias emitidas para servicios digitales establecen exigencias concretas de segregación de ambientes, custodia inalterable de pistas de auditoría y restricción de cuentas privilegiadas. No obstante, se identificó una brecha de capacidad técnica entre los requerimientos normativos y las prácticas observadas en entidades cooperativas y de menor escala. Se concluyó que el marco normativo nacional resulta adecuado en su diseño formal, radicando el reto principal en fortalecer los mecanismos de supervisión e inspección técnica efectiva."
    )
    add_formatted_paragraph(
        doc,
        "En cuanto al tercer objetivo específico, dirigido a comparar los modelos técnicos de seguridad lógica, cifrado y auditoría continua, los hallazgos documentales confirmaron que la salvaguarda de la integridad y confidencialidad descansa en la aplicación conjunta del Cifrado Transparente de Datos (TDE), el control de acceso por roles (RBAC) y la monitorización constante de transacciones. Mediante el contraste de estudios experimentales, se determinó que la penalización computacional atribuida al cifrado en reposo es predecible y plenamente asumible en motores modernos de bases de datos, desvirtuando su postergación por motivos de rendimiento. Asimismo, se evidenció que la aplicación estricta del menor privilegio en cuentas de administración mitiga significativamente los riesgos derivados de credenciales comprometidas y fraudes internos. En concordancia con los estándares internacionales, se demostró que el registro protegido de eventos DDL y DML representa una condición indispensable para reducir los plazos de detección de irregularidades. En consecuencia, se concluyó que la activación simultánea de esquemas de cifrado en reposo y pistas de auditoría independientes conforma la línea base mínima de seguridad para el sistema financiero boliviano."
    )
    add_formatted_paragraph(
        doc,
        "Sobre el cuarto objetivo específico, centrado en evaluar las estrategias de continuidad operativa, replicación y recuperación ante desastres (DRP), la revisión teórica evidenció un cambio sustantivo desde las restauraciones tradicionales basadas en copias de seguridad diferidas hacia esquemas de recuperación casi instantánea orientados a minimizar el RTO. Se determinó que el despliegue de arquitecturas modernas basadas en microservicios e instantáneas coordinadas permite reducir las interrupciones del servicio a niveles mínimos en procesos financieros críticos. Por su parte, se comprobó que, dadas las condiciones geográficas y de conectividad de Bolivia, los esquemas de replicación asíncrona continúan ofreciendo una solución técnica y económica viable para preservar la disponibilidad entre nodos remotos. De forma complementaria, se constató que las políticas de respaldo carecen de validez práctica si no son sometidas a pruebas periódicas de restauración bajo escenarios de contingencia simulada. Por ello, se concluyó que las entidades financieras bolivianas, en particular en la plaza de Santa Cruz, deben formalizar sus umbrales admisibles de RTO y RPO, adaptando sus mecanismos de contingencia a la exigencia de procesamiento ininterrumpido del sistema de pagos nacional."
    )
    add_formatted_paragraph(
        doc,
        "Finalmente, en torno al objetivo general integrador de la investigación, el análisis sintético de la literatura y la normativa permitió concluir que la solidez operativa del sistema financiero boliviano depende de una articulación equilibrada entre el cumplimiento de las directrices de la ASFI y la implementación efectiva de controles técnicos en la capa de datos. Se comprobó que el notable crecimiento de las transacciones electrónicas desplazó el foco de vulnerabilidad hacia las bases de datos relacionales, demandando una evolución cualitativa en las prácticas de administración y gobierno de la información. Asimismo, se determinó que la mitigación de los riesgos tecnológicos no se logra mediante herramientas desarticuladas, sino a través de una estrategia integral que combine cifrado en reposo, auditoría continua, replicación verificada y capacitación del personal técnico. En última instancia, se concluyó que reducir las asimetrías de madurez tecnológica entre grandes bancos e intermediarios cooperativos es la condición indispensable para consolidar la resiliencia operativa y preservar la confianza ciudadana en el ecosistema financiero del país."
    )

    # -------------------------------------------------------------------------
    # 8. REFERENCIAS (REF-1..8)
    # -------------------------------------------------------------------------
    doc.add_paragraph("Referencias", style='Heading 1')

    referencias = [
        "Añasco Loor, C., Morocho, K. J., & Hallo, M. T. (2023). Using data mining techniques for the detection of SQL injection attacks on database systems. *Revista Politécnica*, *51*(2), 19–28. https://doi.org/10.33333/rp.vol51n2.02",
        "Autoridad de Supervisión del Sistema Financiero [ASFI]. (2018). *Recopilación de Normas para Servicios Financieros: Libro 3°, Título V, Gestión de Riesgo Operativo* (Circular ASFI/207/2013; última actualización Circular ASFI/546/2018). ASFI. https://servdmzw.asfi.gob.bo/Textos/L03T05.pdf",
        "Autoridad de Supervisión del Sistema Financiero [ASFI]. (2025a, 8 de agosto). *ASFI destaca crecimiento continuo en depósitos y créditos del sistema financiero nacional* [Nota de prensa]. https://www.asfi.gob.bo/node/1179",
        "Autoridad de Supervisión del Sistema Financiero [ASFI]. (2025b). *Reglamento para Empresas de Tecnología Financiera* (Circular ASFI/885/2025). Gaceta Electrónica de Regulación Financiera. https://servdmzw.asfi.gob.bo/circular/Circulares/ASFI_885.pdf",
        "Banco Central de Bolivia [BCB]. (2026). *Informe de vigilancia del sistema de pagos 2025*. BCB. https://www.bcb.gob.bo/webdocs/files_noticias/IVSP%202025vf.pdf",
        "Colquehuanca Javieri, M. (2015). Replicación asíncrona de base de datos. *Fides et Ratio*, *10*(10), 61–79. https://www.scielo.org.bo/scielo.php?script=sci_arttext&pid=S2071-081X2015000200004",
        "Fondo Monetario Internacional [FMI]. (2024). *Global financial stability report, April 2024: Chapter 3. Cyber risk—A growing concern for macrofinancial stability*. International Monetary Fund. https://www.elibrary.imf.org/display/book/9798400257704/CH003.xml",
        "IBM Security. (2024). *Cost of a data breach report 2024*. IBM Corporation. https://www.ibm.com/reports/data-breach",
        "*Ley N.º 393 de Servicios Financieros*. (2013). Gaceta Oficial del Estado Plurinacional de Bolivia. https://servdmzw.asfi.gob.bo/circular/Leyes/Ley393ServiciosFinancieros.pdf",
        "Madyatmadja, E. D., Hakim, A. N., & Sembiring, D. J. M. (2021). Performance testing on Transparent Data Encryption for SQL Server's reliability and efficiency. *Journal of Big Data*, *8*(1). https://doi.org/10.1186/s40537-021-00520-z",
        "National Institute of Standards and Technology [NIST]. (2010). *Contingency planning guide for federal information systems* (NIST Special Publication 800-34, Rev. 1). U.S. Department of Commerce. https://doi.org/10.6028/NIST.SP.800-34r1",
        "Open Web Application Security Project [OWASP]. (2025). *OWASP Top 10:2025*. OWASP Foundation. https://top10.owasp.org/2025/en",
        "PCI Security Standards Council [PCI SSC]. (2024). *Payment Card Industry Data Security Standard (PCI DSS) v4.0.1*. PCI SSC. https://www.pcisecuritystandards.org/document_library/",
        "Porrúa, M., Moncayo, G., Paz, S., Nowersztern, A., Bejarano, J. F., Baudino, M. F., Bordese, M. P., Barret, K., Baena, C. E., Jaramillo, M., Garces, O., & Isidro, A. (2025). *2025 cybersecurity report: Vulnerability and maturity challenges to bridging the gaps in Latin America and the Caribbean*. Banco Interamericano de Desarrollo. https://doi.org/10.18235/0013872",
        "Unnava, N. (2025). Real-time disaster recovery for fintech: From RTO to instant recovery using microservice snapshots. *International Journal of Computational and Experimental Science and Engineering*, *11*(4). https://doi.org/10.22399/ijcesen.4537",
        "Zimeri David, G. I., & Saucedo Cuellar, D. L. (2025). Transformación estructural de los medios de pago en Bolivia entre 2025 y 2026. *Ecosistemas y Negocios*, *2*(1). https://doi.org/10.65924/enegocios.v2i1.11"
    ]

    for ref in referencias:
        add_reference_paragraph(doc, ref)

    # =========================================================================
    # 4. APÉNDICES (Sección 2 continuación, APE-1..3)
    # =========================================================================
    print("Construyendo Apéndices A y B...")
    doc.add_page_break()
    p_ap_a = doc.add_paragraph("Apéndice A", style='Heading 1')
    disable_auto_numbering(p_ap_a)

    add_table_label(doc, "Tabla A1", "Matriz de Análisis Bibliográfico (MAB): Fuentes Verificadas de la Monografía")

    add_formatted_paragraph(
        doc,
        "A continuación se presenta la Matriz de Análisis Bibliográfico (MAB) que avala metodológicamente la lectura crítica, sistemática y documental de las dieciséis fuentes académicas y regulatorias verificadas en la investigación, conforme al mandato estricto de la Guía Institucional EIP-UAGRM:"
    )

    mab_data = [
        ["ID", "Autor(es) y Año", "OE", "Hallazgo Principal Parafraseado", "Cita Textual Corta Verificada", "Relevancia para Bolivia y Santa Cruz", "Estado"],
        ["S01", "ASFI (2025b)", "OE2", "El Reglamento para ETF exige capacidades mínimas a los sistemas informáticos de las fintechs: registros completos de transacciones, cifrado en almacenamiento y tránsito, autenticación robusta con auditabilidad y trazabilidad, y registro de accesos e intentos de acceso.", "«Contar con mecanismos de identificación y autenticación robusta, permitiendo su auditabilidad y trazabilidad» (Sección 4, art. 2, inc. c, p. 1/5)", "Fija el estándar técnico obligatorio que deben cumplir las plataformas digitales en Bolivia.", "V"],
        ["S02", "Banco Central de Bolivia (2026)", "OE1, OE4", "Registra 892 millones de operaciones QR en 2025 (+131 %), con 1.697 pagos por minuto (28 por segundo), incrementando exponencialmente la carga sobre motores de BD.", "«El procesamiento es 24/7 los 365 días del año» (p. 3)", "Cuantifica la explosión transaccional y la superficie de exposición tecnológica nacional.", "V"],
        ["S03", "ASFI (2025a)", "OE2", "Santa Cruz concentra el 41 % de la cartera de créditos nacional (Bs 93.424 millones), constituyendo la mayor plaza de datos financieros del país.", "«Santa Cruz lidera con Bs93.424 millones (41%), seguido de La Paz con Bs57.048 millones (25%) y Cochabamba con Bs39.100 millones (17%)» (párr. 2)", "Demuestra la criticidad y concentración de infraestructuras bancarias en Santa Cruz.", "V"],
        ["S04", "Fondo Monetario Internacional (2024)", "OE1", "El sector financiero está desproporcionadamente expuesto al ciberriesgo, con potencial de amenazar la estabilidad macrofinanciera y las redes de pago.", "«A cyber incident at a financial institution could threaten macrofinancial stability through three key channels» (sección Transmission of Cyber Risks to Macrofinancial Stability)", "Marco de referencia global para justificar la criticidad sistémica de las bases de datos.", "V"],
        ["S05", "IBM Security (2024)", "OE1", "El costo promedio de filtración de datos en la banca alcanzó USD 6,08 millones, un 22 % por encima del promedio global intersectorial.", "«Companies now spend USD 6.08 million dealing with data breaches, which is 22% higher than the global average» (párr. 2)", "Métrica empírica del impacto financiero de incidentes internos y accesos no autorizados.", "V"],
        ["S06", "Porrúa et al. (2025)", "OE1, OE2", "Diagnostica brechas persistentes de recursos, desarrollo de talento y coordinación intersectorial en ciberseguridad en 30 países de América Latina y el Caribe (BID–OEA).", "«Persistent gaps in resources, workforce development, and cross-sector coordination continue to leave the region vulnerable to evolving digital threats» (comunicado oficial del informe)", "Explica la asimetría operativa y técnica que afecta a entidades medianas y cooperativas.", "V"],
        ["S07", "OWASP (2025)", "OE1, OE3", "En la edición 2025 del Top 10, el control de acceso roto ocupa A01, la configuración insegura A02 y la inyección —incluida la inyección SQL— A05.", "«An injection vulnerability is an application flaw that allows untrusted user input to be sent to an interpreter (e.g. a browser, database, the command line) and causes the interpreter to execute parts of that input as commands» (A05:2025)", "Taxonomía técnica internacional de los vectores de ataque más graves contra motores relacionales.", "V"],
        ["S08", "NIST (2010)", "OE4", "Define las métricas RTO (objetivo de tiempo de recuperación) y RPO (punto de recuperación) como base metodológica de la continuidad de datos.", "«RTO defines the maximum amount of time that a system resource can remain unavailable before there is an unacceptable impact on other system resources, supported mission/business processes, and the MTD» (p. 17)", "Estándar fundacional para el diseño de planes de contingencia y resiliencia ante desastres.", "V"],
        ["S09", "Zimeri David & Saucedo Cuellar (2025)", "OE1, OE2", "Caracteriza la transformación estructural del sistema de pagos boliviano por interoperabilidad QR, gratuidad regulatoria y billeteras digitales.", "«La transformación de los medios de pago en Bolivia entre 2025 y 2026 refleja un cambio estructural impulsado por la interoperabilidad del QR $imple, la gratuidad regulatoria, la crisis de divisas y la irrupción de billeteras digitales como Yape» (Resumen, p. 53)", "Evidencia científica nacional sobre la presión transaccional en infraestructuras locales.", "V"],
        ["S10", "Colquehuanca Javieri (2015)", "OE4", "Analiza las técnicas de replicación de bases de datos distribuidas y propone una estructura algorítmica evolutiva asíncrona para reducir los tiempos de transferencia de datos.", "«La replicación de bases de datos es la creación y el mantenimiento de múltiples copias de la misma base de datos» (p. 63)", "Antecedente técnico nacional en la revista arbitrada boliviana Fides et Ratio (SciELO).", "V"],
        ["S11", "PCI SSC (2024)", "OE3", "Prescribe que el PAN almacenado se torne ilegible mediante criptografía fuerte con gestión de llaves asociada, y que se proteja con criptografía fuerte en tránsito por redes abiertas.", "«PAN is rendered unreadable anywhere it is stored by using any of the following approaches: […] Strong cryptography with associated key-management processes and procedures» (Req. 3.5.1, p. 90)", "Estándar técnico internacional exigido a las redes transaccionales bancarias de Bolivia.", "V"],
        ["S12", "ASFI (2018)", "OE2", "Define el riesgo tecnológico como componente del riesgo operativo, ordenando planes de continuidad, registro CIRO y auditoría interna.", "«Riesgo tecnológico: Es la posibilidad o probabilidad de sufrir pérdidas por caídas o fallos en los sistemas informáticos o en la transmisión de datos, errores de programación u otros, siendo éste un componente del riesgo operativo» (p. 5)", "Base normativa reglamentaria vigente del sistema financiero boliviano (RNSF Libro 3°, Título V).", "V"],
        ["S13", "Ley N.º 393 (2013)", "OE2", "Marco legal rector del sistema financiero: consagra la función social, la confidencialidad, la solvencia y la continuidad de los servicios financieros.", "«Asegurar la continuidad de los servicios ofrecidos» (art. 4, num. II, inc. d)", "Ley nacional rectora de los servicios financieros en el Estado Plurinacional de Bolivia.", "V"],
        ["S14", "Añasco Loor et al. (2023)", "OE1", "Aplica técnicas de minería de datos, con adaptación de CRISP-DM, para construir una herramienta que detecte ataques de inyección SQL contra bases de datos relacionales.", "«las infraestructuras de bases de datos y de almacenamiento de la información están sujetas a diversos ataques de inyección de lenguaje de consulta estructurado (SQL)» (p. 19)", "Evidencia empírica regional arbitrada sobre detección dinámica de ataques a bases de datos.", "V"],
        ["S15", "Madyatmadja et al. (2021)", "OE3", "Mide experimentalmente el costo de rendimiento del Cifrado Transparente de Datos (TDE) en SQL Server: entre 2 % y 15 % según la operación evaluada.", "«Transparent Data Encryption uses approximately 2–15% of system databases' performance on each value focused on, namely Reliability and Efficiency» (Conclusiones)", "Estudio experimental arbitrado sobre el balance medible entre cifrado y velocidad transaccional.", "V"],
        ["S16", "Unnava (2025)", "OE4", "Modela arquitecturas de recuperación ante desastres en tiempo real para fintechs, basadas en instantáneas de microservicios, acercando el RTO a la recuperación instantánea.", "«This article presents a transformative disaster recovery paradigm leveraging microservice state snapshots, declarative infrastructure patterns, and automated orchestration to achieve near-instantaneous recovery during catastrophic regional failures» (Resumen)", "Literatura de vanguardia internacional sobre resiliencia en plataformas financieras digitales.", "V"]
    ]

    tbl_mab = doc.add_table(rows=len(mab_data), cols=7)
    tbl_mab.autofit = False
    mab_widths = [Inches(0.5), Inches(1.0), Inches(0.5), Inches(1.5), Inches(1.2), Inches(1.2), Inches(0.6)]
    for r_idx, row in enumerate(tbl_mab.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = mab_widths[c_idx]
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(mab_data[r_idx][c_idx])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9)
            if r_idx == 0:
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_table_apa_borders(tbl_mab)
    add_table_note(doc, "Todas las fuentes cuentan con estado V (Verificada). Cada cita de esta matriz fue "
                        "transcrita literalmente del documento original descargado (PDF institucional, artículo "
                        "arbitrado o página oficial) y contrastada con su localizador; las citas en inglés se "
                        "conservan en su idioma original, conforme al principio de transcripción exacta. Las fuentes "
                        "web sin paginación se localizan por sección, párrafo o requisito. Ninguna cita de esta matriz "
                        "es una reconstrucción de memoria ni una traducción retrovertida.")
    add_table_note(doc, "En **S05**, la oración citada corresponde al resumen institucional que IBM publica junto con "
                        "el informe (*Cost of a data breach 2024: Financial industry*); la cifra de USD 6,08 millones "
                        "se reproduce en el desglose de costo por industria del informe (figura 3, p. 10). En **S06**, "
                        "la oración citada corresponde al comunicado oficial de prensa del BID y la OEA que acompaña "
                        "la publicación del informe. En **S07**, la numeración A01, A02 y A05 corresponde a la edición "
                        "2025 del OWASP Top 10, en la que Inyección se ubica en A05; en la edición 2021 la misma "
                        "categoría figuraba como A03.",
                   etiqueta="Nota sobre localizadores.")

    # APÉNDICE B
    doc.add_page_break()
    p_ap_b = doc.add_paragraph("Apéndice B", style='Heading 1')
    disable_auto_numbering(p_ap_b)

    p_apb_sub = doc.add_paragraph()
    p_apb_sub.style = doc.styles['Normal']
    p_apb_sub.paragraph_format.space_before = Pt(6)
    p_apb_sub.paragraph_format.space_after = Pt(12)
    p_apb_sub.paragraph_format.line_spacing = 2.0
    r_apb_tit = p_apb_sub.add_run("Registro Metodológico de Búsqueda y Protocolo Documental")
    r_apb_tit.bold = True
    r_apb_tit.font.name = 'Times New Roman'
    r_apb_tit.font.size = Pt(12)

    add_formatted_paragraph(
        doc,
        "A continuación se detalla el protocolo documental aplicado para la identificación, selección y validación del corpus bibliográfico:"
    )

    add_bullet_item(doc, "1. Ecuaciones de Búsqueda Aplicadas:", "")
    add_sub_bullet(doc, "• Ecuación 1 (Riesgo tecnológico y regulación en Bolivia): `(\"riesgo tecnologico\" OR \"ciberseguridad\") AND (\"bases de datos\" OR \"sistema financiero\") AND (\"Bolivia\" OR \"Santa Cruz\")`")
    add_sub_bullet(doc, "• Ecuación 2 (Vectores y controles en bases de datos): `(\"database security\" OR \"SQL injection\" OR \"TDE\") AND (\"financial entities\" OR \"banking\") AND (2021..2026)`")
    add_sub_bullet(doc, "• Ecuación 3 (Continuidad y replicación): `(\"disaster recovery\" OR \"RTO\" OR \"asynchronous replication\") AND (\"relational database\" OR \"fintech\")`")

    add_bullet_item(doc, "2. Bases de Datos y Repositorios Consultados:", "")
    add_sub_bullet(doc, "• Repositorios oficiales del Estado Plurinacional de Bolivia: Autoridad de Supervisión del Sistema Financiero (Gaceta Electrónica de Regulación Financiera, ASFI) y Banco Central de Bolivia (Portal Oficial BCB).")
    add_sub_bullet(doc, "• Portales científicos indexados: SciELO Bolivia, Redalyc, Directory of Open Access Journals (DOAJ), Crossref, OpenAlex, SpringerOpen y repositorios de revistas universitarias bolivianas (*Fides et Ratio*, *Ecosistemas y Negocios* - UPSA).")
    add_sub_bullet(doc, "• Repositorios de estándares técnicos internacionales: Open Web Application Security Project (OWASP), National Institute of Standards and Technology (NIST) y PCI Security Standards Council (PCI SSC).")
    add_sub_bullet(doc, "• Informes de organismos multilaterales: Fondo Monetario Internacional (FMI) y Banco Interamericano de Desarrollo / Organización de los Estados Americanos (BID–OEA).")

    add_bullet_item(doc, "3. Criterios de Inclusión y Exclusión:", "")
    add_sub_bullet(doc, "• *Criterios de Inclusión:* Documentos normativos y leyes vigentes en Bolivia; informes oficiales con datos estadísticos del período 2021–2026; artículos de revistas científicas arbitradas con revisión por pares; estándares técnicos reconocidos internacionalmente con aplicabilidad al sector bancario; pertinencia temática directa con bases de datos relacionales y riesgo tecnológico.")
    add_sub_bullet(doc, "• *Criterios de Exclusión:* Fuentes no académicas, blogs de opinión, wikis abiertas, monografías no arbitradas de repositorios informales, literatura no verificable y estudios empíricos ajenos al ámbito financiero.")

    add_bullet_item(doc, "4. Indicador de Recencia y Actualidad a Octubre 2026:", "")
    add_sub_bullet(doc, "• Total de fuentes analizadas: 16 fuentes académicas y regulatorias oficiales.")
    add_sub_bullet(doc, "• Fuentes correspondientes al período 2021–2026: 12 fuentes (75 % de recencia, superando el mínimo institucional del 70 %).")
    add_sub_bullet(doc, "• Fuentes de vanguardia (2024–2026): 10 fuentes (S01, S02, S03, S04, S05, S06, S07, S09, S11, S16).")
    add_sub_bullet(doc, "• Fuentes fundacionales o normativa base: 4 fuentes (NIST 2010, Ley 393 de 2013, Colquehuanca 2015, ASFI RNSF Título V de 2018).")

    # =========================================================================
    # GUARDADO DEL DOCUMENTO WORD
    # =========================================================================
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        doc.save(str(OUTPUT_PATH))
        print(f"✔ Documento Word oficial generado con éxito en: {OUTPUT_PATH}")
    except PermissionError:
        doc.save(str(OUTPUT_FALLBACK_PATH))
        print(f"⚠ AVISO: '{OUTPUT_PATH.name}' está abierto en Microsoft Word.")
        print(f"✔ Documento Word actualizado generado con éxito en: {OUTPUT_FALLBACK_PATH}")
        print("  Para actualizar el archivo principal, cierre Word y vuelva a ejecutar este script.")


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "completa"
    build_monografia_docx(modo=modo)
