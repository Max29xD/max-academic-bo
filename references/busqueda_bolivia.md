# Protocolo de búsqueda inteligente — Bolivia / Santa Cruz

Guía Institucional 2026 · Normas APA 7.ª edición · Actualidad a la fecha de corte más reciente

Objetivo: encontrar literatura **real, verificable, pertinente y rigurosamente actualizada a la fecha más reciente** (o la más nueva disponible), priorizando evidencia científica boliviana y regional sin sacrificar calidad ni rigor metodológico. Este protocolo se usa en P2 (datos duros y contextuales del problema), en P4 (revisión de literatura) y en el modo `BUSCAR`.

---

## Índice

1. [Fases B0–B8](#1-fases)
2. [Embudo geográfico](#2-embudo-geográfico)
3. [Catálogo de fuentes por nivel (T1–T5)](#3-catálogo-de-fuentes-por-nivel)
4. [Cómo consultar (buscador web / fetch) y filtros de recencia](#4-cómo-consultar)
5. [Criterios de inclusión / exclusión y filtro de recencia](#5-criterios-de-inclusión--exclusión)
6. [Verificación bibliográfica y estados V / P / N](#6-verificación-bibliográfica-y-estados)
7. [Matriz de Análisis Bibliográfico (MAB)](#7-matriz-de-análisis-bibliográfico-mab)
8. [Registro de datos duros (para P2 y P8)](#8-registro-de-datos-duros-p2-y-p8)
9. [Escasez de literatura boliviana](#9-escasez-de-literatura-boliviana)
10. [Acceso limitado (paywall, PDFs del usuario)](#10-acceso-limitado)
11. [Registro de búsqueda (Apéndice B)](#11-registro-de-búsqueda-apéndice-b-sugerido)
12. [Mandato de actualización estricta al corte más reciente](#12-mandato-de-actualización-estricta-al-corte-más-reciente)

---

## 1. Fases

**B0 · Mapa de conceptos y delimitación temporal.** A partir de la pregunta de investigación y los OE (nunca antes: buscar sin objetivos definidos dispersa la investigación), extraer 4 grupos de descriptores:
1. *Fenómeno central* (p. ej., adopción tecnológica, comercio digital, gestión logística).
2. *Población/sector* (p. ej., MyPE, microempresas, retail, sector agropecuario, banca múltiple).
3. *Contexto geográfico* (Santa Cruz de la Sierra, cruceño, oriente boliviano, Bolivia).
4. *Dimensión o relación* (factores determinantes, barreras de acceso, competitividad).
5. *Ventana temporal de actualidad:* Operadores temporales obligatorios (`2024..2026`, `2025`, `2026`, corte reciente a octubre 2026).
Ejecutar `scripts/generar_consultas.py` con los grupos definidos para obtener cadenas booleanas formales y consultas web optimizadas.

**B1 · Cadenas por base.** Cadena booleana para bases académicas (Scopus, WoS, Google Scholar, SciELO, Redalyc, Dialnet) para el Apéndice, y consultas cortas para el buscador web.

**B2 · Descubrimiento por embudo geográfico** (sección 2), de lo local a lo global, anotando cuántos resultados pertinentes rinde cada nivel.

**B3 · Triaje de relevancia y actualidad.** Aplicar criterios de la sección 5 sobre título/resumen. Descartar con motivo anotado. Si un artículo empírico aborda una realidad desactualizada habiendo estudios de 2024–2026 sobre el mismo fenómeno, priorizar el más reciente.

**B4 · Verificación de metadatos.** Abrir cada candidata (fetch) y confirmar los 8 campos de metadatos (sección 6). Asignar estado V/P/N.

**B5 · MAB.** Completar la matriz (sección 7) y asignar cada fuente a un eje temático y a un OE.

**B6 · Chequeo de suficiencia y actualidad** (ver abajo).

**B7 · Bola de nieve (backward & forward).** Desde las 2–3 mejores fuentes: revisar sus referencias (*backward*) y buscar quién las citó recientemente (*forward*, p. ej., "citado por" en Google Scholar o Scopus para identificar citas de 2024 a 2026). Repetir B4 con cada hallazgo.

**B8 · Registro.** Guardar consultas, bases, fecha exacta (octubre 2026) y resultados para el Apéndice B.

### Chequeo de suficiencia y actualidad (B6)

| Criterio | Tipo | Umbral estricto |
|---|---|---|
| Fuentes académicas V | Norma institucional | ≥ 5 (meta de la skill: 10–15 fuentes verificadas) |
| Cobertura de ejes | Calidad analítica | Cada eje temático con ≥ 2 fuentes para permitir contraste dialéctico |
| Cobertura de OE | Norma (OBJ-6) | Cada OE sustentado por ≥ 1 eje temático |
| **Actualidad (Corte 2026)** | **Norma institucional / Skill** | **≥ 70 % de fuentes del período 2021–2026, con presencia obligatoria de publicaciones 2024–2026 (hasta octubre 2026)**. Clásicos fundacionales permitidos solo si se justifican como tales. |
| **Cifras oficiales y estadísticas** | **Rigor empírico (ACT-1)** | **Último reporte oficial publicado a octubre 2026** (Censo Nacional 2024 / INE 2024–2026, BCB, ASFI, CEPAL). Prohibido usar cifras obsoletas habiendo cortes recientes. |
| Evidencia local boliviana | Meta de la skill | ≥ 3 fuentes con contexto boliviano si existen; si no, documentarlo como vacío (sección 9) |
| Variedad de procedencia | Calidad | Diversidad de autores, revistas e instituciones; no monopolio de una sola revista |

Si no se llega al mínimo de 5 fuentes V: **detenerse y avisar**; nunca completar con fuentes débiles ni inventadas.

---

## 2. Embudo geográfico (Enfoque exclusivo en Bolivia)

Toda monografía desarrollada bajo esta skill tiene como sujeto, objeto y beneficiario exclusivo al territorio boliviano. El embudo de búsqueda opera desde lo micro-local boliviano hacia lo nacional, utilizando lo externo únicamente como contraste:

| Nivel | Alcance Territorial | Uso típico y fuentes |
|---|---|---|
| **L1 Local / Subnacional** | Ciudad, municipio o provincia boliviana (p. ej., Santa Cruz de la Sierra, Montero, Warnes, El Alto, La Paz, Cochabamba, Quillacollo, Sucre, Tarija, etc.) | Evidencia empírica local, problemáticas productivas municipales, datos de cámaras empresariales regionales (CAINCO, CAO, ICAM). |
| **L2 Departamental** | Cualquiera de los 9 departamentos de Bolivia (Santa Cruz, La Paz, Cochabamba, Chuquisaca, Oruro, Potosí, Tarija, Beni, Pando) | Datos departamentales consolidados, planes departamentales de desarrollo, estadísticas territoriales del INE. |
| **L3 Nacional (Bolivia)** | Estado Plurinacional de Bolivia a nivel integral | Normativa nacional (Gaceta Oficial), estadísticas oficiales INE (Censo 2024 / series 2024–2026), Banco Central de Bolivia (BCB), ASFI, políticas públicas sectoriales. |
| **L4 Regional comparativo** | América Latina / Comunidad Andina / Cono Sur | Informes CEPAL, BID, CAF utilizados **únicamente para contrastar o medir la brecha de Bolivia respecto a la región**. |
| **L5 Global / Teórico** | Marcos conceptuales universales | Modelos teóricos y metodológicos para fundamentar conceptualmente la solución del problema boliviano. |

Reglas inviolables de territorialidad (GEO-1 / GEO-2):
- **Cero monografías de objeto extranjero:** Queda estrictamente prohibido elegir como fenómeno central problemáticas de otros países sin aplicación directa en Bolivia.
- **Rastreo deductivo:** Iniciar la búsqueda siempre en L1–L2. Si la literatura científica arbitrada local es escasa, documentar dicha escasez como evidencia directa del **vacío de investigación científica en Bolivia**.
- **Fuentes L4–L5 subordinadas:** Toda fuente regional o global que se cite debe tener una justificación de contraste o sustento conceptual para Bolivia. La Discusión y Conclusiones deben resolver exclusivamente el impacto en el territorio boliviano analizado.

---

## 3. Catálogo de fuentes por nivel

> Verificar la vigencia de cada dominio al consultarlo. Confirmar siempre la fecha de emisión del reporte o artículo.

### T1 — Revisadas por pares, locales/regionales
- **SciELO Bolivia** (`scielo.org.bo`): Revistas científicas nacionales arbitradas (foco en publicaciones 2022–2026).
- **SciELO Regional** (`scielo.org`): Filtrar por países del Cono Sur y la Comunidad Andina.
- **Redalyc** (`redalyc.org`): Sistema de información científica de acceso abierto, filtrando por artículos 2021–2026.
- **Latindex Catálogo 2.0** (`latindex.org`): Para comprobar que la revista cumple criterios estrictos de calidad editorial.
- **Dialnet** (`dialnet.unirioja.es`), **DOAJ** (`doaj.org`).
- **OJS y revistas universitarias de Bolivia:** UAGRM, UCB, UPB, UMSA, UPSA, UMSS, UAJMS, USFX, Univalle.

### T2 — Revisadas por pares, internacionales indexadas
- **Scopus / Web of Science:** Localizar mediante Google Scholar, OpenAlex, Semantic Scholar, CORE o el portal de la editorial. Verificar cuartil SJR o JCR.
- **Google Scholar** (`scholar.google.com`): Aplicar filtro de fecha *"Desde 2024"* o *"Desde 2022"*.
- **OpenAlex, CORE, BASE, Semantic Scholar:** Búsquedas por DOI y resúmenes estructurados.

### T3 — Tesis y trabajos de grado en repositorios
- Repositorios universitarios bolivianos (`uagrm.edu.bo`, `umsa.bo`, `ucb.edu.bo`, `upb.edu`, `upsa.edu.bo`, etc.).
- Agregadores: La Referencia (`lareferencia.info`), OpenAIRE. (Priorizar tesis de maestría y doctorales; pregrado solo como apoyo secundario).

### T4 — Literatura gris institucional y estadística oficial (al corte más reciente)
Esencial para P2 (Problema), P8 (Introducción) y datos de contexto. **Obligatorio emplear el último reporte publicado a la fecha:**
- **INE (Instituto Nacional de Estadística, `ine.gob.bo`):** 
  - Censo Nacional de Población y Vivienda 2024 (resultados oficiales, conteos y desgloses sociodemográficos 2024–2026).
  - Encuesta Continua de Empleo (ECE) 2025–2026 (tasas de ocupación, informalidad, desempleo).
  - Cuentas Nacionales, PIB trimestral, balanza comercial e IPC a las series más recientes de 2026.
- **Banco Central de Bolivia (`bcb.gob.bo`):** Informes de Política Monetaria (IPM 2025–2026), Informes de Estabilidad Financiera, resoluciones de pagos digitales y normativa de activos virtuales.
- **ASFI (`asfi.gob.bo`):** Boletines mensuales y anuales del sistema financiero, cartera de créditos MyPE, índices de mora e inclusión financiera a 2026.
- **ATT (`att.gob.bo`) y AGETIC (`agetic.gob.bo`):** Indicadores de penetración de internet, telecomunicaciones, comercio electrónico y trámites digitales (reportes 2024–2026).
- **SEPREC (`seprec.gob.bo`):** Estadísticas del Registro de Comercio de Bolivia (creación y cancelación de empresas a 2025–2026).
- **Organismos internacionales:** CEPAL (`cepal.org`, Balance Preliminar y Panorama Social 2024–2026), BID (`iadb.org`), Banco Mundial (`worldbank.org`), CAF (`caf.com`), UNCTAD (`unctad.org`), OIT.
- **Gremios y centros cruceños:** CAINCO (`cainco.org.bo`, reportes económicos e informes de coyuntura 2025–2026), IBCE (`ibce.org.bo`), CAO, CEDLA (`cedla.org`), INESAD (`inesad.edu.bo`), Fundación Milenio, Fundación Jubileo.

### T5 — Libros académicos
- Editoriales científicas universitarias y comerciales reconocidas (Springer, Elsevier, Routledge, Pearson, McGraw-Hill, etc.). Citar ediciones vigentes.

**Fuentes prohibidas:** Wikipedia, El Rincón del Vago, monografias.com, buenastareas, blogs no institucionales, foros de opinión, notas de prensa sin firma de analista ni rigor metodológico.

---

## 4. Cómo consultar y filtros 2026

**Herramientas operativas:** la herramienta de **búsqueda web** de tu entorno (p. ej. `web_search`, `websearch`, `WebSearch`) para descubrir fuentes, y la de **lectura/fetch** (p. ej. `web_fetch`, `webfetch`, `Fetch`) para verificar el contenido completo. La lectura solo debe abrir URLs descubiertas en resultados previos o aportadas por el usuario.

**Estrategia de búsqueda con corte a octubre 2026:**
Las consultas deben estructurarse combinando los núcleos temáticos con delimitadores temporales recientes (`2024..2026`, `2025`, `2026`, `"octubre 2026"`).

Patrones de consulta recomendados:
```text
<concepto A> <concepto B> Bolivia 2024..2026
<concepto A> <concepto B> "Santa Cruz de la Sierra" 2024 OR 2025 OR 2026
site:scielo.org.bo <concepto A> <concepto B> 2024..2026
site:redalyc.org <concepto A> Bolivia 2024..2026
site:ine.gob.bo <indicador> 2024 OR 2025 OR 2026
site:ine.gob.bo "censo 2024" resultados <sector o municipio>
site:bcb.gob.bo <indicador financiero o moneda> 2025 OR 2026
site:asfi.gob.bo <crédito o microempresa> 2025 OR 2026
site:cainco.org.bo <informe o estudio> 2024..2026
site:cepal.org Bolivia <indicador> 2024..2026
<concepto A> <concepto B> filetype:pdf Bolivia 2025 OR 2026
"<título del artículo reciente>" (para verificar DOI y páginas)
```

---

## 5. Criterios de inclusión / exclusión

**Incluir si:**
1. Responde directamente a un OE y eje temático de la monografía.
2. Es artículo revisado por pares (T1/T2), libro científico (T5), tesis de postgrado (T3) o reporte oficial institucional (T4).
3. **Pertenece a la ventana temporal de actualidad: preferentemente 2021–2026 (con prioridad en 2024–2026 al corte de octubre 2026)**.
4. Posee identificación bibliográfica completa comprobable (autores, año, título, medio, enlace DOI/URL).
5. Se pudo abrir y confirmar su contenido exacto mediante fetch o PDF subido.

**Excluir si:**
1. Cifras desactualizadas o reportes superados por publicaciones oficiales posteriores (2024–2026).
2. Artículos con autor o fecha no identificables.
3. Repeticiones de prensa sin sustento metodológico primario.
4. Artículos en listas de retractación o en revistas depredadoras.

---

## 6. Verificación bibliográfica y estados

Para cada candidata seleccionada, confirmar los 8 campos obligatorios:
1. Autores completos (apellido e iniciales, en el orden de publicación).
2. Año exacto de publicación (verificar que no sea fecha de envío preliminar).
3. Título completo y subtítulo.
4. Nombre de la revista, editorial o institución publicadora.
5. Volumen, número y rango correlativo de páginas (o artículo electrónico `eXXXX`).
6. DOI activo (`https://doi.org/...`) o URL institucional permanente.
7. Tipología documental (artículo científico, libro, reporte oficial, tesis).
8. Indexación declarada (SciELO, Scopus, Redalyc, Latindex Catálogo 2.0).

**Estados:**
- **V (Verificada):** Los 8 campos confirmados en la página oficial de la fuente. Citable con total validez.
- **P (Parcial):** Solo se visualizó el resumen o faltan páginas precisas. Solo permite afirmaciones generales contenidas en el resumen; debe completarse antes de la entrega final.
- **N (No verificada):** No existe confirmación, datos discordantes o enlace roto. **Prohibido citar en el texto.**

---

## 7. Matriz de Análisis Bibliográfico (MAB)

Se exporta como **Apéndice A**. Cada fila representa una fuente con estado V:

| ID | Estado | Autores (año) | Referencia APA completa | Nivel (T1–T5) | Indexación | País/Contexto | Objetivo | Método y muestra | Hallazgo clave | Limitación | Relevancia para Bolivia | Postura (↑/↓) | Eje | OE | Dato citable + pág. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Ninguna cita puede insertarse en el cuerpo de la monografía sin su correspondiente ID en la MAB en estado V.

---

## 8. Registro de datos duros (P2 y P8)

Para cada cifra utilizada en el planteamiento del problema o introducción:

| ID | Indicador | Valor | Unidad | Año | Fecha de publicación / Corte | Fuente oficial (APA) | Ubicación (tabla/pág.) | URL | Estado |
|---|---|---|---|---|---|---|---|---|---|

**Regla de corte:**
Antes de registrar una cifra de 2022 o anterior, se debe verificar activamente si el INE, BCB, ASFI o CEPAL emitieron una actualización en 2024, 2025 o 2026. Si existe actualización oficial, es obligatorio usar la más reciente. La fórmula de brecha debe indicar los años exactos:
`brecha = estándar (año) − observado (año)`.

---

## 9. Escasez de literatura boliviana

Si al buscar en SciELO Bolivia y repositorios nacionales se hallan pocos artículos empíricos indexados recientes:
1. Documentar exhaustivamente las búsquedas realizadas en el Apéndice B.
2. Ampliar al nivel L3 (países andinos y Latinoamérica) para contrastar el fenómeno.
3. Recurrir a T4 (informes oficiales INE, BCB, CAINCO 2024–2026) para la evidencia empírica local.
4. **Transformar la escasez en un hallazgo metodológico de valor:** señalar en la Discusión y Conclusiones que existe un **vacío de investigación científica empírica actualizada a 2026 en Bolivia**, lo que resalta la pertinencia y originalidad de la monografía.

---

## 10. Acceso limitado

Si un artículo clave de 2024–2026 se encuentra tras muro de pago (paywall):
- Asignar temporalmente estado P citando únicamente lo respaldado en su resumen público oficial.
- Solicitar al usuario que descargue y suba el archivo PDF a la sesión para su lectura integral.
- Prohibido inventar datos, tablas o conclusiones de un texto que no pudo ser leído.

---

## 11. Registro de búsqueda (Apéndice B sugerido)

| Fecha (Oct 2026) | Base / Portal | Cadena o consulta ejecutada | Filtros aplicados | Nivel geográfico | Resultados revisados | Pertinentes | Incluidas (IDs) | Criterio de exclusión |
|---|---|---|---|---|---|---|---|---|

---

## 12. Mandato de actualización estricta al corte más reciente

1. **Vigencia cronológica:** La monografía se sitúa en **Octubre de 2026**. Todo análisis coyuntural, económico, empresarial o tecnológico debe considerar la situación más reciente a esta fecha.
2. **Censo y demografía:** Considerar los datos del Censo Nacional de Población y Vivienda 2024 y los desgloses oficiales publicados por el INE hasta 2026.
3. **Cero obsolescencia injustificada:** No presentar como "situación actual" diagnósticos que tengan más de 4 años de antigüedad si el fenómeno ha evolucionado aceleradamente (especialmente en tecnología, comercio electrónico, finanzas, inteligencia artificial y comercio exterior).
