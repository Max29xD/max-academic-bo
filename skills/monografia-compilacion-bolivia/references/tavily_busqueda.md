# Búsqueda Académica Avanzada con Tavily (Estilo Perplexity)

Esta guía establece el protocolo operativo para realizar búsquedas de literatura académica verificada, extracciones de contenido y síntesis multi-fuente tipo Perplexity, con respaldo reproducible en disco.

---

## 1. Modos de Ejecución Disponibles

La skill soporta tres niveles de integración automática:

1. **CLI de Tavily (`tvly`):** Si está instalado en el sistema (`which tvly`).
2. **API REST Directa (`TAVILY_API_KEY`):** Si la variable de entorno está presente, el script `buscar_fuentes.py` se conecta vía HTTPS directo con Python puro sin requerir instalación del CLI ni librerías adicionales.
3. **Registro de Agente (`--plantilla`):** Si no hay credenciales de Tavily, el agente realiza la búsqueda con sus herramientas de navegación web (`search_web`, `read_file`, etc.) y registra la evidencia en el mismo formato estándar en `output/fuentes/`.

---

## 2. Tipos de Búsqueda y Parámetros

### A. Búsqueda con Filtros y Dominios Específicos (`--tipo search`)
Utilízala para localizar artículos indexados, informes de entes reguladores y estadísticas oficiales:
```bash
# Búsqueda avanzada con límite temporal
python scripts/buscar_fuentes.py "adopción pagos QR Bolivia 2024" --tipo search --profundidad advanced --rango-tiempo year

# Búsqueda restringida a dominios oficiales de Bolivia
python scripts/buscar_fuentes.py "estabilidad financiera Bolivia" --tipo search --dominios bcb.gob.bo asfi.gob.bo ine.gob.bo scielo.org.bo
```

### B. Investigación Sintetizada Multi-Fuente (`--tipo research`)
Emula el comportamiento de Perplexity Pro: genera un informe estructurado analizando múltiples páginas web con citas explícitas:
```bash
python scripts/buscar_fuentes.py "impacto de la regulación fintech en la inclusión financiera en Bolivia" --tipo research --modelo pro
```

### C. Extracción Profunda de Contenido (`--tipo extract`)
Extrae el contenido textual limpio y estructurado en Markdown de una o varias URLs comprobadas (evita alucinaciones o citas basadas en simples snippets):
```bash
python scripts/buscar_fuentes.py --tipo extract --url "https://www.bcb.gob.bo/webdocs/files_noticias/IVSP%202025vf.pdf"
```

---

## 3. Protocolo de Evidencia Reproducible

Cada consulta ejecutada mediante `scripts/buscar_fuentes.py` almacena automáticamente un archivo JSON en:
`output/fuentes/YYYYMMDD-HHMMSS-<tipo>-<slug>.json`

### Estructura de la evidencia:
```json
{
  "generado": "2026-10-28T22:00:00Z",
  "herramienta": "tvly_cli",
  "tipo": "search",
  "consulta": "inclusión financiera Bolivia 2024",
  "urls": null,
  "parametros": {
    "profundidad": "advanced",
    "maximo": 10,
    "rango_tiempo": "year",
    "tema": null,
    "modelo": null
  },
  "resultado": {
    "results": [
      {
        "title": "Informe del Sistema de Pagos",
        "url": "https://www.bcb.gob.bo/...",
        "content": "Texto verificado...",
        "score": 0.92
      }
    ]
  }
}
```

Esta evidencia es la base inalterable para:
1. La **Matriz de Análisis Bibliográfico (MAB)** incluida en el Apéndice A.
2. El **Protocolo de Búsqueda** del Apéndice B.
3. El catálogo de fuentes `output/referencias.json`.

---

## 4. Embudo de Búsqueda para Bolivia (Corte 2021–2026)

| Nivel | Enfoque | Dominios prioritarios |
|---|---|---|
| **Nivel 1: Oficial Regulatorio** | Datos macroeconómicos, normativas y censos | `bcb.gob.bo`, `asfi.gob.bo`, `ine.gob.bo`, `gacetaoficialdebolivia.gob.bo` |
| **Nivel 2: Académico Boliviano** | Tesis y revistas indexadas nacionales | `scielo.org.bo`, `revistasbolivianas.org.bo`, repositorios UAGRM, UMSA, UCB |
| **Nivel 3: Organismos Regionales** | Contexto comparado y macrofinanciero | `cepal.org`, `iadb.org` (BID), `bancomundial.org`, `imf.org` |
