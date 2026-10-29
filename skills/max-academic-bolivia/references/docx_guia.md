# Guía Técnica de DOCX: Creación, Estilos APA 7 y Validación OOXML

Esta guía documenta las capacidades y mejores prácticas para generar, editar, inspeccionar y validar documentos Word (`.docx`), integradas de forma nativa en la skill para garantizar compatibilidad total en cualquier proyecto sin requerir dependencias externas complejas.

---

## 1. Fundamentos de un archivo `.docx`

Un archivo `.docx` es un contenedor ZIP que empaqueta partes XML estructuradas bajo el estándar ECMA-376 / ISO-IEC 29500 (Open Packaging Conventions - OPC y WordprocessingML).

### Estructura interna esencial:
```text
documento.docx (ZIP)
├── [Content_Types].xml        # Mapa MIME de tipos de contenido
├── _rels/
│   └── .rels                  # Relaciones principales del paquete
└── word/
    ├── document.xml           # Cuerpo del texto, párrafos, tablas
    ├── styles.xml             # Definición de estilos tipográficos
    ├── numbering.xml          # Listas numeradas y viñetas
    ├── header1.xml / header2  # Encabezados de sección
    ├── footer1.xml / footer2  # Pies de página y numeración
    ├── settings.xml           # Configuración de compatibilidad
    └── _rels/
        └── document.xml.rels  # Hipervínculos, imágenes y estilos vinculados
```

---

## 2. Generación Institucional vs Operaciones Puntuales

| Necesidad | Herramienta | Enfoque |
|---|---|---|
| **Monografía completa institucional** | `scripts/generar_monografia_docx.py [archivo.md]` | Compilador agnóstico que lee `output/monografia_completa.md` (o cualquier `.md`), extrae metadatos y aplica la plantilla `templates/apa7ma.docx` con carátula de 10 elementos, numeración romana/arábiga y tablas APA 7. |
| **Validación de integridad XML** | `scripts/docx_utils.py validar <doc>` | Comprueba que el ZIP esté intacto y que todos los XMLs internos sintácticamente cumplan el estándar (evita el temido mensaje de Word de "contenido ilegible"). |
| **Extracción de texto / tablas** | `scripts/docx_utils.py texto <doc>` | Lee y extrae el texto a consola o markdown sin necesitar Microsoft Word ni LibreOffice. |
| **Fusión de runs fragmentados** | `scripts/docx_utils.py fusionar-runs in.docx -o out.docx` | Coalesce fragmentos contiguos de texto `<w:r>` para permitir reemplazos o búsquedas de texto exactas. |
| **Métricas e inspección de estilos** | `scripts/docx_utils.py info <doc>` | Analiza encabezados (Heading 1, Heading 2), recuento de palabras y tablas. |

---

## 3. Reglas Críticas de Formato (Normas APA 7.ª edición)

1. **Tipografía uniforme:**
   - Arial 12 pt para el cuerpo del texto, interlineado doble (2.0), sin espacio entre párrafos (`space_after = 0`).
   - Sangría de primera línea obligatoria de 1.27 cm (0.5 pulgadas) en todos los párrafos de texto regular.
2. **Encabezados numerados automáticos:**
   - La plantilla cuenta con numeración multinivel vinculada a los estilos `Heading 1` (1. Introducción) y `Heading 2` (1.1 Formulación).
   - **Regla:** Nunca agregues números manuales en el texto del encabezado al llamar al generador (`add_heading('Introducción', level=1)` en lugar de `add_heading('1. Introducción', level=1)`).
3. **Tablas APA 7:**
   - Línea superior (top), línea inferior de encabezados y línea inferior de tabla (bottom).
   - **Cero líneas verticales.**
   - Primera línea: `Tabla N` en negrita.
   - Segunda línea: Título descriptivo en cursiva a doble espacio.
   - Nota al pie: `Nota.` en cursiva seguida de la fuente y aclaraciones.
4. **Paginación mixta institucional:**
   - Sección 1 (Preliminares: Resumen, Palabras clave, Índice): Números romanos en minúscula (`ii`, `iii`, `iv`...) en el encabezado superior derecho. La primera página (carátula) tiene numeración oculta (`different_first_page_header_footer = True`).
   - Sección 2 (Cuerpo a partir de `1. Introducción`): Salto de sección de página siguiente (`WD_SECTION.NEW_PAGE`), desvinculando el encabezado de la sección anterior (`is_linked_to_previous = False`) y reiniciando la numeración en números arábigos (`start_type = 1`).

---

## 4. Edición Directa de XML en Caso de Necesidad

Si necesitas corregir o modificar un documento existente sin regenerarlo:
```bash
# 1. Descomprimir el documento
unzip -q documento.docx -d doc_temp/

# 2. Coalescer runs para facilitar búsquedas de texto
python scripts/docx_utils.py fusionar-runs documento.docx -o doc_limpio.docx

# 3. Editar doc_temp/word/document.xml preservando tags
# 4. Reempaquetar
cd doc_temp && zip -Xr ../documento_modificado.docx . && cd ..

# 5. Validar con la utilidad
python scripts/docx_utils.py validar documento_modificado.docx
```
