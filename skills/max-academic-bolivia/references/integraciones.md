# Integraciones: docx · Tavily · word-bibliography

La skill es **autocontenida**: con Python y `python-docx` ya produce el documento, la
bibliografía APA 7 y `Sources.xml`. Las skills compañeras son **refuerzos opcionales**; si no
están, se aplica el plan B y se avisa al usuario. Nunca bloquees la entrega por una dependencia
opcional.

## 0. Diagnóstico

```bash
python scripts/verificar_entorno.py --json
```

Devuelve `dependencias`, `tavily` y `skills_companeras` con rutas. La skill busca compañeras en
`.agents/skills`, `.claude/skills`, `skills/`, `~/.agents/skills`, `~/.claude/skills` y
`~/.config/opencode/skills`.

## 1. Tavily — búsqueda tipo Perplexity

| Necesidad | Comando | Requiere auth |
|---|---|---|
| Búsqueda rápida con snippets | `tvly search "consulta" --json` | No (cupo keyless) |
| Búsqueda profunda | `tvly search "..." --depth advanced --max-results 10 --json` | No (cupo) |
| Noticias / rango temporal | `tvly search "..." --topic news --time-range week --json` | No (cupo) |
| Extraer una URL | `tvly extract "https://..." --json` | No (cupo) |
| Investigación multi-fuente con citas | `tvly research "tema" --model pro --citation-format apa --json` | Sí |
| Mapa de un sitio | `tvly map "https://..."` | Sí |
| Crawl de un sitio | `tvly crawl "https://..."` | Sí |

**Envoltura reproducible (recomendada):**

```bash
python scripts/buscar_fuentes.py "inclusión financiera Bolivia 2024" --tipo search --rango-tiempo year
python scripts/buscar_fuentes.py "regulación fintech Bolivia" --tipo research --modelo pro
python scripts/buscar_fuentes.py --tipo extract --url https://www.bcb.gob.bo/...
```

Guarda la evidencia en `output/fuentes/<fecha>-<tipo>-<slug>.json` con consulta, parámetros,
resultados y URLs. Esa es la materia prima de la MAB (Apéndice A) y del registro de búsqueda
(Apéndice B).

**Reglas de uso:**
- No inventes ni completes metadatos desde el snippet: abre la URL (`webfetch` o `tvly extract`).
- Cita solo fuentes que puedas enlazar; marca `[VERIFICAR]` lo que no abriste.
- En entornos no interactivos, si falta auth no lances `tvly login`; reporta la opción y usa el
  plan B.
- No envíes datos confidenciales del usuario a búsquedas externas.

**Plan B sin `tvly`:** usa la búsqueda web nativa del agente y `webfetch`. Guarda igualmente la
evidencia (consulta, fecha, URL, fragmento textual) en `output/fuentes/`. La calidad de la MAB no
depende de Tavily, sino de la verificación.

Instalación de Tavily (solo si el usuario la pide o la necesita):

```bash
curl -fsSL https://cli.tavily.com/install.sh | bash
# alternativa: uv tool install tavily-cli  |  pip install tavily-cli
tvly init --skip-auth
```

## 2. docx — Word profesional

**Cuándo usar el generador propio** (`scripts/generar_monografia_docx.py`): siempre que el
entregable sea la monografía institucional. Ya aplica carátula de 10 elementos, paginación mixta,
estilos APA 7, tablas, referencias y apéndices desde `output/monografia_completa.md`.

**Cuándo delegar a la skill `docx`** (si está instalada):
- Editar un `.docx` existente sin regenerarlo.
- Control de cambios, comentarios, aceptar/rechazar cambios.
- Convertir a PDF o renderizar para revisión visual.
- Operaciones genéricas de Word que no sean la monografía (cartas, memorandos, plantillas).

**Regla:** no mezcles ambos caminos en la misma versión. Si delegas, el `.docx` resultante debe
pasar la auditoría de contenido (`auditar_monografia.py`) y la revisión visual.

**Plan B sin la skill `docx`:** `python-docx` (ya es dependencia). Para leer un `.docx` usa
`auditar_monografia.py` (extrae texto) o `python -c "import docx; ..."`. Para PDF, pide al usuario
que exporte desde Word; no inventes una conversión que no puedas verificar.

## 3. word-bibliography — bibliografía de Word

**Camino principal:** `scripts/gestor_referencias.py` lee `output/referencias.json`, escribe
`referencias_bibliograficas.md` (APA 7) y `Sources.xml` (Office Open XML Bibliography) e
inscribe la bibliografía en el `.docx` si existe.

```bash
python scripts/gestor_referencias.py --init       # primera vez: catálogo de ejemplo
python scripts/gestor_referencias.py              # Markdown + Sources.xml
python scripts/gestor_referencias.py --incrustar  # además, dentro del .docx
```

Importar en Word: **Referencias → Administrar fuentes → Examinar…** y elegir `Sources.xml`
(EN: *References → Manage Sources → Browse…*). La lista maestra global de Word **no se toca**
salvo `--sync-word-global` explícito, para no alterar las fuentes personales del usuario.

**Cuándo usar la skill `word-bibliography`:** tipos de fuente que el generador interno no cubre
(capítulos, congresos, patentes, casos) o cuando el usuario pida su CLI. El XML siempre debe
validarse contra el esquema `shared-bibliography.xsd`.

**Plan B sin la skill:** el generador interno cubre `JournalArticle`, `Report`, `Book`,
`BookSection`, `ConferenceProceedings`, `InternetSite` y `DocumentFromInternetSite`. Si un tipo no
está cubierto, usa `Misc` y deja la referencia APA 7 correcta en el texto; anótalo como pendiente.

## 4. Matriz rápida de decisión

| Situación | Acción |
|---|---|
| "Genera la monografía en Word" | Generador propio |
| "Edita este Word y acepta los cambios" | Skill `docx`; si no está, explica la limitación |
| "Busca papers de 2024–2026 en SciELO Bolivia" | `buscar_fuentes.py` → `webfetch` para verificar |
| "Hazme un informe tipo Perplexity" | `tvly research` (o búsqueda nativa + síntesis citada) |
| "Pásame las referencias a Word" | `gestor_referencias.py` → `Sources.xml` |
| "Necesito una tesis en PDF" | Genera `.docx`; exporta a PDF desde Word |

## 5. Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `tvly: command not found` | CLI no instalado | Instalar o usar plan B |
| `tvly` pide login en research | Esa función requiere auth | `tvly login` interactivo o plan B |
| `tvly` da `oauth_refresh_failed` | Sesión OAuth caducada | `tvly login` de nuevo o `tvly logout` para volver al modo keyless |
| `ModuleNotFoundError: docx` | Falta python-docx | `pip install python-docx` |
| `PermissionError` al guardar `.docx` | Word tiene el archivo abierto | Cierra Word; el generador crea `*_actualizada.docx` |
| `Sources.xml` vacío | `referencias.json` mal formado | Valida el JSON y que sea una lista o `{"fuentes": [...]}` |
| El índice no aparece | Estilos de título no nativos | Usa la plantilla incluida y estilos Heading 1–3 |
| Logo ausente | `assets/logo.png` no existe | Coloca el logo o la carátula usará el marcador |
