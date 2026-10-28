# Gestión Bibliográfica para Microsoft Word: APA 7 y `Sources.xml`

Esta guía describe el flujo de trabajo para la administración de fuentes bibliográficas, su conversión al formato oficial de Microsoft Word (`Office Open XML Bibliography`) y el formateo estricto bajo normas **APA 7.ª edición**.

---

## 1. El Catálogo Maestro (`output/referencias.json`)

El catálogo JSON del proyecto es la única fuente de verdad documental. Ninguna fuente entra a la monografía sin estar verificada y registrada aquí.

### Estructura estándar recomendada:
```json
[
  {
    "tag": "BCB2026",
    "type": "Report",
    "authors": [],
    "author_corporate": "Banco Central de Bolivia [BCB]",
    "title": "Informe de Vigilancia del Sistema de Pagos 2025",
    "year": 2026,
    "institution": "Banco Central de Bolivia",
    "url": "https://www.bcb.gob.bo/webdocs/files_noticias/IVSP%202025vf.pdf"
  },
  {
    "tag": "ZimeriSaucedo2025",
    "type": "JournalArticle",
    "authors": [
      {"first": "David", "last": "Zimeri"},
      {"first": "Daniel", "last": "Saucedo"}
    ],
    "title": "Transformación estructural de los medios de pago en Bolivia",
    "year": 2025,
    "journal_name": "Ecosistemas y Negocios",
    "volume": "2",
    "issue": "1",
    "pages": "1-15",
    "doi": "10.65924/enegocios.v2i1.11"
  }
]
```

---

## 2. Tipos de Fuente en Microsoft Word (`b:SourceType`)

Microsoft Word utiliza el namespace `http://schemas.openxmlformats.org/officeDocument/2006/bibliography`. Los tipos más comunes son:

| Tipo | Uso principal | Elementos XML clave |
|---|---|---|
| `JournalArticle` | Artículos de revistas científicas indexadas | `<b:JournalName>`, `<b:Volume>`, `<b:Issue>`, `<b:Pages>`, `<b:DOI>`, `<b:URL>` |
| `Report` | Informes de organismos (BCB, ASFI, CEPAL, BM) | `<b:Institution>`, `<b:ReportNumber>`, `<b:URL>` |
| `WebSite` / `InternetSite` | Sitios web, páginas institucionales, notas de prensa | `<b:NameofWebSite>`, `<b:Year>`, `<b:Month>`, `<b:Day>`, `<b:URL>` |
| `Book` | Libros completos | `<b:Publisher>`, `<b:City>`, `<b:Edition>` |
| `BookSection` | Capítulos de libros colectivos | `<b:BookTitle>`, `<b:Publisher>`, `<b:Pages>` |
| `ConferenceProceedings` | Ponencias en congresos académicos | `<b:ConferenceName>`, `<b:Pages>` |

---

## 3. Flujo de Ejecución con los Scripts Incorporados

### Generar o regenerar todos los entregables:
```bash
# Inicializar catálogo de ejemplo si es un proyecto nuevo
python scripts/gestor_referencias.py --init

# Generar referencias_bibliograficas.md (APA 7) y Sources.xml (Word)
python scripts/gestor_referencias.py

# Alternativa directa con el módulo de bibliografía Word
python scripts/word_bibliography.py -i output/referencias.json -o output/Sources.xml --print-apa
```

---

## 4. Importación en Microsoft Word

Para que el tribunal, el docente o el investigador tengan las fuentes activas en Word y puedan insertar citas dinámicas con un solo clic:

1. Abrir el documento `.docx` en Microsoft Word.
2. Ir a la pestaña **Referencias** (en inglés: *References*).
3. Hacer clic en **Administrar fuentes** (en inglés: *Manage Sources*).
4. Hacer clic en el botón **Examinar...** (en inglés: *Browse...*).
5. Seleccionar el archivo `output/Sources.xml` generado por la skill.
6. En la ventana izquierda (*Lista general*), seleccionar las fuentes y hacer clic en **Copiar ->** para moverlas a la *Lista actual* del documento.
7. Al hacer clic en **Bibliografía -> Insertar bibliografía**, Word creará la tabla de fuentes formateada automáticamente en APA 7.
