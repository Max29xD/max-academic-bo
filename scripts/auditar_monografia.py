#!/usr/bin/env python3
"""Auditor estricto de monografías de compilación (EIP-FINOR-UAGRM + APA 7.ª).

Uso:
  python auditar_monografia.py archivo.(md|txt|docx) [--titulo "..."] [--year 2026] [--json]

Lee texto plano/Markdown o .docx (sin dependencias externas) y revisa reglas con ID
(ver references/reglas_institucionales.md). Es una verificación AUTOMÁTICA y heurística:
los avisos (⚠) requieren criterio humano; los errores (✖) son incumplimientos objetivos.
No sustituye la lectura del texto ni la verificación de que las fuentes existen.
"""
import argparse
import datetime
import json
import re
import sys
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

BOLIVIA_TERMINOS = [
    "bolivia", "boliviano", "boliviana", "bolivianos", "bolivianas",
    "santa cruz", "cruceño", "cruceña", "cruceños", "cruceñas",
    "la paz", "paceño", "paceña", "paceños", "paceñas",
    "cochabamba", "cochabambino", "cochabambina",
    "chuquisaca", "sucre", "chuquisaqueño", "chuquisaqueña",
    "oruro", "orureño", "orureña",
    "potosi", "potosí", "potosino", "potosina",
    "tarija", "tarijeño", "tarijeña", "chapaco", "chapaca",
    "beni", "beniano", "beniana", "trinidad",
    "pando", "pandino", "pandina", "cobija",
    "el alto", "montero", "warnes", "quillacollo", "sacaba", "yacuiba", "riberalta", "camiri"
]

# --------------------------------------------------------------------------- utilidades

def norm(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def palabras(s):
    return re.findall(r"[\wáéíóúñüÁÉÍÓÚÑÜ]+(?:[-'’][\wáéíóúñü]+)*", s)


def leer(path):
    if path.lower().endswith(".docx"):
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        lines = []
        paras = []
        for p in root.iter(W + "p"):
            buf = []
            for el in p.iter():
                if el.tag == W + "t":
                    buf.append(el.text or "")
                elif el.tag == W + "tab":
                    buf.append("\t")
            txt = "".join(buf)
            lines.append(txt)
            pPr = p.find(W + "pPr")
            pStyle = None
            if pPr is not None:
                ps = pPr.find(W + "pStyle")
                if ps is not None:
                    pStyle = ps.attrib.get(W + "val")
            paras.append({"texto": txt, "estilo": pStyle})
        return lines, paras
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
        paras = [{"texto": l, "estilo": None} for l in lines]
        return lines, paras


def limpiar(l):
    l = l.strip()
    l = re.sub(r"^#+\s*", "", l)
    l = l.replace("**", "").replace("__", "").strip("*_ ").strip()
    return re.sub(r"\s+", " ", l)


def sin_md(l):
    """Quita marcas de cursiva/negrita de Markdown para el análisis."""
    return re.sub(r"[*_]{1,3}", "", l)


class Reporte:
    def __init__(self):
        self.items = []

    def add(self, nivel, rid, msg):
        self.items.append({"nivel": nivel, "id": rid, "msg": msg})

    def err(self, rid, msg): self.add("ERR", rid, msg)
    def warn(self, rid, msg): self.add("AVISO", rid, msg)
    def ok(self, rid, msg): self.add("OK", rid, msg)
    def info(self, rid, msg): self.add("INFO", rid, msg)


# --------------------------------------------------------------------------- secciones

SEC = [
    ("resumen", r"^resumen$"),
    ("introduccion", r"^(?:\d+[\.\)]?\s*)?introduccion$"),
    ("problema", r"^(?:\d+[\.\)]?\s*)?planteamiento del problema$"),
    ("objetivos", r"^(?:\d+[\.\)]?\s*)?objetivos( de (la )?investigacion)?$"),
    ("revision", r"^(?:\d+[\.\)]?\s*)?revision (literaria|de (la )?literatura|bibliografica)$"),
    ("terminos", r"^(?:\d+[\.\)]?\s*)?definicion de terminos( y conceptos)?$"),
    ("discusion", r"^(?:\d+[\.\)]?\s*)?discusion$"),
    ("conclusiones", r"^(?:\d+[\.\)]?\s*)?conclusiones$"),
    ("referencias", r"^(?:\d+[\.\)]?\s*)?(referencias( bibliograficas)?|bibliografia)$"),
    ("apendices", r"^(?:\d+[\.\)]?\s*)?(apendices?|anexos?)( [a-z])?$"),
]
ORDEN = [k for k, _ in SEC]


def detectar_secciones(lines):
    cand = []
    for i, l in enumerate(lines):
        t = limpiar(l)
        if not t or len(t) > 80:
            continue
        n = norm(t)
        for key, rx in SEC:
            if re.match(rx, n):
                cand.append((i, key, t))
    allidx = sorted(c[0] for c in cand)
    elegido = {}
    for i, key, t in cand:
        nxt = next((j for j in allidx if j > i), len(lines))
        largo = sum(len(x) for x in lines[i + 1:nxt])
        if key == "apendices":
            if key not in elegido:
                elegido[key] = (i, t, largo)
            continue
        if key not in elegido or largo > elegido[key][2]:
            elegido[key] = (i, t, largo)
    # Varias cabeceras para Referencias (p. ej. "7. Referencias" y "8. Bibliografía"):
    # tratarlas como una sola sección continua desde la primera aparición, para no
    # confundir entradas de la lista con citas del cuerpo.
    ref_pos = [i for i, key, _ in cand if key == "referencias"]
    if "referencias" in elegido and ref_pos:
        elegido["referencias"] = (min(ref_pos), elegido["referencias"][1], elegido["referencias"][2])
    orden_idx = sorted((v[0], k) for k, v in elegido.items())
    secs = {}
    for pos, (i, k) in enumerate(orden_idx):
        fin = orden_idx[pos + 1][0] if pos + 1 < len(orden_idx) else len(lines)
        secs[k] = {"idx": i, "titulo": elegido[k][1], "lineas": lines[i + 1:fin], "inicio": i + 2}
    return secs


# --------------------------------------------------------------------------- citas

STOP_INICIO = {
    "Según", "Para", "Como", "Mientras", "Sin", "Por", "En", "De", "El", "La", "Los", "Las",
    "Además", "Asimismo", "Igualmente", "Entonces", "Aunque", "Si", "Cuando", "Donde", "Tal",
    "Esto", "Estos", "Estas", "Ese", "Esa", "También", "Pero", "Sino", "Frente", "Desde",
    "Hacia", "Tras", "Ante", "Bajo", "Contra", "Entre", "Hasta", "Lo", "Un", "Una", "Sus",
    "Su", "Dicho", "Dicha", "Así", "Finalmente", "Primero", "Segundo", "Luego", "Ahora",
    "Incluso", "Conforme", "Respecto", "Considerando", "Ver", "Véase", "Cf",
}
CONECT = {"de", "del", "la", "las", "los", "y", "e", "&", "et", "al.", "al"}
RX_NARR = re.compile(r"^\s*(\d{4}[a-z]?|s\.\s?f\.)\s*(?:,\s*pp?\.\s*[\d\-–, ]+)?\s*$")
RX_ANIO_EN_PART = re.compile(r",\s*(\d{4}[a-z]?|s\.\s?f\.)(?=\s*(?:,|$))")


def autor_narrativo(prev):
    toks = prev.rstrip().split()
    out = []
    for t in reversed(toks[-14:]):
        tl = t.strip("[]()¿?¡!«»\"“”;:").strip()
        core = tl.strip(",.")
        if not core:
            break
        es_conect = core.lower() in CONECT
        # fin de la oración anterior o definición tipo "Término: ..."
        if t.endswith(":") and not es_conect:
            break
        if t.endswith(".") and not es_conect and len(core) > 1:
            break
        if es_conect or core[0].isupper():
            out.append(tl)
        else:
            break
    out.reverse()
    while out and (out[0].strip(",").lower() in CONECT or out[0].strip(",") in STOP_INICIO):
        out.pop(0)
    # sin conector de lista (y/&/e) no hay lista de autores: cortar tras la última coma
    if not any(x.strip(",").lower() in ("&", "y", "e") for x in out):
        for i in range(len(out) - 1, -1, -1):
            if out[i].endswith(","):
                out = out[i + 1:]
                break
    return " ".join(x for x in out)


def clave_autor(a):
    a = re.sub(r"\bet al\.?", "", a)
    for tok in re.split(r"[\s,&]+", a):
        t = tok.strip("[]().")
        if t and t.lower() not in CONECT and t[0].isupper():
            return norm(t)
    return norm(a.split(",")[0].strip())


def es_sigla(a):
    """True si el autor parece una sigla institucional (p. ej. CEPAL, ASFI, INE)."""
    a = re.sub(r"\bet al\.?", "", a).strip()
    if " " in a:
        return False
    return bool(re.fullmatch(r"[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9]{1,7}", a))


def subsecuencia(a, b):
    """¿Las letras de `a` aparecen en orden dentro de `b`? (sigla ⊂ iniciales)."""
    it = iter(b)
    return bool(a) and all(ch in it for ch in a)


INSTITUCIONAL = re.compile(
    r"\b(Comisi[oó]n|Instituto|Autoridad|Banco|Ministerio|Organizaci[oó]n|Organismo|Fondo|Programa|"
    r"Agencia|Comit[eé]|Centro|Universidad|Servicio|Direcci[oó]n|Superintendencia|Asociaci[oó]n|"
    r"C[aá]mara|Confederaci[oó]n|Consejo|Secretar[ií]a|Gobierno|Estado|Empresa|Sociedad|Federaci[oó]n|"
    r"Fundaci[oó]n|Observatorio|Naciones|Departamento|Municipio|Prefectura|Viceministerio)\b", re.I)


def anio_base(y):
    m = re.match(r"(\d{4})", y)
    return m.group(1) if m else y.lower().replace(" ", "")


def n_autores(a):
    a = re.sub(r"\bet al\.?", "", a)
    partes = [p for p in re.split(r",|\s&\s|\sy\s|\se\s", a) if p.strip()]
    return len(partes)


def extraer_citas(lines, offset=0):
    citas = []
    for ln, raw in enumerate(lines, 1):
        l = sin_md(raw)
        for m in re.finditer(r"\(([^()]*)\)", l):
            cont = m.group(1)
            if RX_NARR.match(cont):
                aut = autor_narrativo(l[:m.start()])
                if aut:
                    citas.append({"aut": aut, "anio": RX_NARR.match(cont).group(1), "linea": ln + offset, "tipo": "narr"})
                continue
            for parte in cont.split(";"):
                parte = re.sub(r"^\s*(v[eé]ase|ver|cf\.|p\.\s?ej\.,?|por ejemplo,?|e\.g\.,?)\s*", "", parte, flags=re.I)
                m2 = RX_ANIO_EN_PART.search(parte)
                if not m2:
                    continue
                aut = parte[:m2.start()].strip()
                if not aut or not aut[0].isupper() or re.search(r"\d", aut) or len(aut) > 160:
                    continue
                citas.append({"aut": aut, "anio": m2.group(1), "linea": ln + offset, "tipo": "par"})
    for c in citas:
        c["clave"] = clave_autor(c["aut"])
        c["anio_b"] = anio_base(c["anio"])
    return citas


def conjunto_citas(citas):
    return {(c["clave"], c["anio_b"]) for c in citas}


# --------------------------------------------------------------------------- referencias

RX_REF_INI = re.compile(r"^[A-ZÁÉÍÓÚÑ].{0,220}?\((\d{4}[a-z]?|s\.\s?f\.)(?:,[^)]*)?\)\.?")


def acronimo(autor):
    pal = [w for w in re.split(r"\s+", re.sub(r"[.,\[\]()]", " ", autor)) if w and w.lower() not in CONECT and w[0].isupper()]
    return "".join(w[0] for w in pal).lower()


def parsear_referencias(lines):
    entradas = []
    for i, raw in enumerate(lines):
        l = raw.strip()
        l = re.sub(r"^[-•*]\s+", "", l)
        if not l:
            continue
        if RX_REF_INI.match(sin_md(l)):
            entradas.append({"raw": l, "linea": i + 1})
        elif entradas:
            entradas[-1]["raw"] += " " + l
    for e in entradas:
        plano = sin_md(e["raw"])
        m = re.search(r"\((\d{4}[a-z]?|s\.\s?f\.)", plano)
        e["anio"] = m.group(1) if m else ""
        e["anio_b"] = anio_base(e["anio"])
        e["autor"] = plano[:m.start()].strip().rstrip(".").strip() if m else plano[:40]
        e["clave"] = clave_autor(e["autor"])
        e["autor_norm"] = norm(e["autor"])
        e["acron"] = acronimo(e["autor"])
        e["plano"] = plano
    return entradas


def coincide(c, r):
    if c["anio_b"] != r["anio_b"]:
        return False
    if c["clave"] == r["clave"]:
        return True
    if c["clave"] and c["clave"] in r["autor_norm"][:120]:
        return True
    ac = norm(re.sub(r"[^A-Za-zÁÉÍÓÚÑ]", "", c["aut"].split(",")[0]))
    if len(ac) >= 2 and ac == r["acron"]:
        return True
    # Sigla institucional (p. ej. CEPAL) frente al nombre completo del organismo.
    if es_sigla(c["aut"]):
        inits = norm("".join(w[0] for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", r["autor"])))
        if len(ac) >= 2 and subsecuencia(ac, inits):
            return True
    return False


# --------------------------------------------------------------------------- chequeos

VERBOS_CAMPO = {"encuestar", "medir", "calcular"}
VERBOS_CAMPO_AFINES = {"entrevistar", "experimentar", "muestrear", "cuestionar", "sondear", "cronometrar"}
VERBOS_BAJOS_OG = {"conocer", "saber", "recordar", "listar", "enumerar", "nombrar", "revisar", "estudiar", "investigar", "ver", "tratar", "mostrar"}
PRIMERA_PERSONA = re.compile(
    r"\b(yo|nosotros|nosotras|nuestro|nuestra|nuestros|nuestras|mi|mis|considero|creo que|pienso|"
    r"analic[eé]|conclu[ií]|concluimos|analizamos|observamos|encontramos|realic[eé]|realizamos|propongo|proponemos)\b",
    re.I)
MARCADORES_CONTRASTE = re.compile(
    r"mientras que|sin embargo|en contraste|no obstante|por el contrario|a diferencia|diverg|coincid|"
    r"en cambio|contrast|por su parte|converg|pese a|aunque|difier|discrep|en consonancia|de modo similar|de manera similar",
    re.I)
FUENTES_PROHIBIDAS = ["wikipedia", "rincondelvago", "rincón del vago", "monografias.com", "buenastareas", "tareasya", "ecured"]
FUENTES_DUDOSAS = ["slideshare", "scribd", "blogspot", "wordpress", "medium.com", "youtube.com", "facebook.com"]


def parrafos(lines, min_pal=1):
    out = []
    for i, l in enumerate(lines):
        t = l.strip()
        if t and not re.match(r"^#+\s", t) and len(palabras(t)) >= min_pal:
            out.append((i + 1, t))
    return out


def quitar_enumeracion(t):
    t = re.sub(r"^\s*objetivo\s+(general|espec[ií]fico)\s*\d*\s*[:.\-–]\s*", "", t, flags=re.I)
    pat = re.compile(r"^\s*(\d+[\.\)]|[-•*]|OE\s?\d+[:.]?|[a-z]\)|\d+\.\d+\.?)\s*", flags=re.I)
    for _ in range(5):
        nuevo = pat.sub("", t)
        if nuevo == t:
            break
        t = nuevo
    return t.strip()


def primer_verbo(t):
    t = quitar_enumeracion(sin_md(t))
    m = re.match(r"([A-Za-zÁÉÍÓÚÑáéíóúñ]+)", t)
    return m.group(1) if m else ""


def chequear_titulo(titulo, r):
    pal = palabras(titulo)
    if len(pal) <= 20:
        r.ok("TIT-1", f"Título: {len(pal)} palabras (≤ 20).")
    else:
        r.err("TIT-1", f"Título con {len(pal)} palabras (máximo 20, contando subtítulo).")
    if titulo.rstrip().endswith("."):
        r.err("TIT-4", "El título termina en punto final.")
    else:
        r.ok("TIT-4", "Título sin punto final.")
    n = norm(titulo)
    if re.match(r"^(un|una)\s+(estudio|analisis|revision)\s+(sobre|de)|^analisis de", n):
        r.warn("TIT-6", "El título inicia con una frase vacía ('Un estudio sobre', 'Análisis de').")
    if not re.search(r"\b(19|20)\d{2}\b", titulo):
        r.warn("TIT-3", "El título no muestra delimitación temporal (año o período). Verificar el CUÁNDO.")
    if not any(g in n for g in BOLIVIA_TERMINOS):
        r.err("GEO-2", "El título no contiene delimitación territorial en Bolivia (debe mencionar explícitamente a Bolivia o alguno de sus departamentos, ciudades o provincias).")
    else:
        r.ok("GEO-2", "Título con anclaje territorial explícito en Bolivia (GEO-1/2).")
    if re.search(r"\b(es|son|fue|fueron|se\s+\w+[ae]n?)\b", n) and len(pal) > 3:
        r.warn("TIT-2", "Posible verbo conjugado en el título: debe ser oración nominal.")


def chequear_resumen(sec, r):
    cuerpo, kw_raw, pk_line_raw = [], None, None
    for l in sec["lineas"]:
        if not l.strip():
            continue
        plano = sin_md(l)
        m = re.search(r"palabras\s+clave\s*:", plano, re.I)
        if m:
            antes = plano[:m.start()].strip()
            if antes:
                cuerpo.append(antes)
            kw_raw = plano[m.end():]
            pk_line_raw = l
        else:
            cuerpo.append(l)
    texto = " ".join(cuerpo)
    nw = len(palabras(texto))
    if nw <= 400:
        r.ok("RES-1", f"Resumen: {nw} palabras (≤ 400).")
    else:
        r.err("RES-1", f"Resumen con {nw} palabras (máximo 400).")
    if len(cuerpo) > 1:
        r.err("RES-2", f"El resumen tiene {len(cuerpo)} párrafos/líneas; debe ser un único bloque continuo.")
    if any(re.match(r"^(\t|\s{2,})", l) for l in cuerpo):
        r.warn("RES-2", "El resumen parece tener sangría de primera línea (debe ir sin sangría).")
    cit = extraer_citas(cuerpo)
    if cit:
        r.err("RES-3", f"El resumen contiene {len(cit)} cita(s) bibliográfica(s): están prohibidas.")
    if re.search(r"\b(tabla|figura|cuadro)\s+\d", norm(texto)):
        r.err("RES-3", "El resumen menciona tablas/figuras.")
    if PRIMERA_PERSONA.search(texto):
        r.err("RES-6", "El resumen usa primera persona.")
    if kw_raw is None:
        r.err("RES-5", "No se encontró la etiqueta 'Palabras clave:'.")
        return
    kw = [k.strip() for k in re.split(r"[,;]", kw_raw) if k.strip()]
    if kw_raw.strip().endswith("."):
        r.err("RES-5", "Las palabras clave terminan con punto final.")
    if len(kw) < 3 or len(kw) > 6:
        r.err("RES-5", f"Palabras clave: {len(kw)} (deben ser 3–5; la Guía admite hasta 6).")
    elif len(kw) == 6:
        r.warn("RES-5", "6 palabras clave: válido según la Guía de Ejecución, pero el Manual indica 3–5.")
    else:
        r.ok("RES-5", f"Palabras clave: {len(kw)}.")
    mayus = [k for k in kw if k != k.lower()]
    if mayus:
        r.warn("RES-5", "Palabras clave con mayúscula: " + ", ".join(mayus) + ". Deben ir en minúsculas, salvo nombres propios (p. ej., Santa Cruz).")
    if sec.get("fmt") == "docx" or not re.search(r"[*_]\s*palabras clave", pk_line_raw.lower()):
        r.info("RES-5", "La cursiva de la etiqueta 'Palabras clave:' no se puede comprobar en texto plano/docx (verificar en Word).")


def chequear_objetivos(sec, r):
    lines = sec["lineas"]
    i_gen = next((i for i, l in enumerate(lines) if len(l.strip()) < 90 and re.search(r"objetivo\s+general", norm(l))), None)
    i_esp = next((i for i, l in enumerate(lines) if len(l.strip()) < 90 and re.search(r"objetivos?\s+especificos?", norm(l))), None)
    if i_gen is None or i_esp is None:
        r.warn("OBJ-3", "No se localizaron los subtítulos 'Objetivo General' / 'Objetivos Específicos'.")
        return None
    def cuerpo(rango):
        out = []
        for l in rango:
            t = l.strip()
            if not t:
                continue
            if len(t) < 40 and re.match(r"^(\d+\.\d+\.?\s*)?(objetivo|objetivos)\b", norm(sin_md(t))):
                continue
            out.append(t)
        return out
    gen = cuerpo(lines[i_gen + 1:i_esp] if i_gen < i_esp else lines[i_gen + 1:])
    esp = cuerpo(lines[i_esp + 1:] if i_esp > i_gen else lines[i_esp + 1:i_gen])
    if len(gen) != 1:
        r.warn("OBJ-3", f"El Objetivo General debe ser único: se detectaron {len(gen)} bloques.")
    if gen:
        og = sin_md(quitar_enumeracion(gen[0]))
        v = norm(primer_verbo(gen[0]))
        if not re.fullmatch(r"[a-zñ]+(ar|er|ir)", v):
            r.err("OBJ-1", f"El OG no inicia con verbo en infinitivo (inicia con '{primer_verbo(gen[0])}').")
        elif v in VERBOS_BAJOS_OG:
            r.warn("OBJ-1", f"El OG inicia con '{v}', verbo de bajo nivel taxonómico o de tipo medio; preferir analizar, sintetizar, evaluar…")
        n = norm(og)
        faltan = []
        if not re.search(r"mediante|a traves de|por medio de|con base en|a partir de|segun", n): faltan.append("CÓMO")
        if not re.search(r"\bpara\b|con el fin de|con el proposito", n): faltan.append("PARA QUÉ")
        if not re.search(r"\b(19|20)\d{2}\b", og) and not re.search(r"periodo|durante|entre", n): faltan.append("CUÁNDO")
        if faltan:
            r.warn("OBJ-3", "El OG podría no cubrir: " + ", ".join(faltan) + " (heurística; verificar las 5 preguntas).")
        else:
            r.ok("OBJ-3", "El OG muestra cómo/para qué/cuándo (heurística).")
        if not any(g in norm(og) for g in BOLIVIA_TERMINOS):
            r.warn("GEO-2", "El Objetivo General parece carecer de delimitación territorial explícita en Bolivia o sus entidades subnacionales.")
        else:
            r.ok("GEO-2", "Objetivo General con delimitación territorial en Bolivia.")
    n_oe = len(esp)
    if 3 <= n_oe <= 5:
        r.ok("OBJ-4", f"{n_oe} objetivos específicos (3–5).")
    else:
        r.err("OBJ-4", f"{n_oe} objetivos específicos detectados (deben ser 3–5).")
    for k, t in enumerate(esp, 1):
        v = norm(primer_verbo(t))
        if not re.fullmatch(r"[a-zñ]+(ar|er|ir)", v):
            r.err("OBJ-1", f"OE{k} no inicia con verbo en infinitivo ('{primer_verbo(t)}').")
        if v in VERBOS_CAMPO:
            r.err("OBJ-2", f"OE{k} usa verbo de trabajo de campo prohibido: '{v}'.")
        elif v in VERBOS_CAMPO_AFINES:
            r.warn("OBJ-2", f"OE{k} usa verbo asociado a trabajo de campo: '{v}'.")
    ya = any(i["id"] == "OBJ-2" for i in r.items)
    for k, t in enumerate(gen + esp):
        if ya:
            break
        if re.search(r"\b(encuest\w+|medir|calcular|entrevist\w+|aplicar (una |un )?(encuesta|cuestionario))\b", norm(t)):
            r.warn("OBJ-2", "Se detectó vocabulario de campo en un objetivo (encuesta/entrevista/medir/calcular).")
            break
    for k, t in enumerate(esp, 1):
        if len(re.findall(r"\by\b", norm(t))) >= 2 and len(palabras(t)) > 35:
            r.warn("OBJ-7", f"OE{k} podría contener más de un logro (varios 'y'); verificar.")
    return n_oe


def chequear_revision(sec, citas_rev, r):
    lines = sec["lineas"]
    texto = " ".join(l for l in lines if l.strip() and not re.match(r"^#+\s", l.strip()))
    total = max(1, len(palabras(texto)))
    q_words = 0
    sin_pag = 0
    largas = 0
    for m in re.finditer(r"[«“\"]([^»”\"]{12,}?)[»”\"]", texto):
        n = len(palabras(m.group(1)))
        if n >= 3:
            q_words += n
            if n >= 15:
                largas += 1
            if not re.search(r"\bpp?\.\s?\d", texto[m.end():m.end() + 90]):
                sin_pag += 1
    pct = 100.0 * q_words / total
    if pct < 20:
        r.ok("REV-5", f"Citas textuales ≈ {pct:.1f} % de la Revisión (< 20 %).")
    else:
        r.err("REV-5", f"Citas textuales ≈ {pct:.1f} % de la Revisión (deben ser < 20 %).")
    if largas:
        r.warn("REV-5", f"{largas} cita(s) textual(es) de 15 o más palabras: priorizar paráfrasis.")
    if sin_pag:
        r.warn("REV-5", f"{sin_pag} cita(s) textual(es) sin número de página detectable (p. xx).")
    # subsecciones (ejes)
    n_sub = sum(1 for l in lines if re.match(r"^\s*(#{2,4}\s|4\.\d)", l))
    if n_sub < 2:
        r.warn("REV-1", "No se detectaron ≥ 2 subsecciones temáticas (ejes) dentro de la Revisión.")
    else:
        r.ok("REV-1", f"{n_sub} subsecciones detectadas en la Revisión (verificar que sean ejes temáticos, no autores).")
    # encabezados que parecen autores
    for l in lines:
        t = limpiar(l)
        if re.match(r"^(#{2,4}\s|4\.\d)", l.strip()) and re.search(r"\b(seg[uú]n|propuesta de|aportes? de|teor[ií]a de [A-Z])\b", t, re.I) and re.search(r"\b[A-Z][a-záéíóú]+ (y|&) [A-Z]|\bet al\b|\(\d{4}\)", t):
            r.warn("REV-1", f"Subsección que parece organizada por autor: «{t[:70]}».")
    # Nivel 3 (proxy)
    pars = [(n, t) for n, t in parrafos(lines, 25)]
    if pars:
        n3 = 0
        for n, t in pars:
            cs = conjunto_citas(extraer_citas([t]))
            if len(cs) >= 2 and MARCADORES_CONTRASTE.search(t):
                n3 += 1
        pct3 = 100.0 * n3 / len(pars)
        if pct3 >= 60:
            r.ok("REV-4", f"Proxy Nivel 3: {n3}/{len(pars)} párrafos ({pct3:.0f} %) integran ≥ 2 fuentes y contrastan.")
        else:
            r.warn("REV-4", f"Proxy Nivel 3: solo {n3}/{len(pars)} párrafos ({pct3:.0f} %) integran ≥ 2 fuentes con marcador de contraste (meta ≥ 60 %). Heurística: revisar manualmente.")
    # fuentes citadas
    fuentes = conjunto_citas(citas_rev)
    if len(fuentes) >= 5:
        r.ok("REV-2", f"La Revisión cita {len(fuentes)} fuentes distintas (≥ 5).")
    else:
        r.err("REV-2", f"La Revisión cita {len(fuentes)} fuentes distintas (mínimo 5).")
    # paráfrasis tipo listado: párrafos que inician con autor
    ini_autor = 0
    for n, t in pars:
        if re.match(r"^(seg[uú]n\s+)?[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+(\s(y|&)\s[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+|\set al\.)?\s*\(\d{4}", t):
            ini_autor += 1
    if pars and ini_autor / len(pars) > 0.5:
        r.warn("REV-1", f"{ini_autor}/{len(pars)} párrafos inician con el nombre de un autor: posible estructura 'por autores'.")


def chequear_conclusiones(sec, n_oe, citas_concl, citas_base, r):
    pars = parrafos(sec["lineas"], 8)
    n = len(pars)
    if n_oe:
        esperado = n_oe + 1
        if n == esperado:
            r.ok("CON-1", f"{n} conclusiones = {n_oe} OE + 1 integradora.")
        else:
            r.err("CON-1", f"{n} párrafos de conclusión; se esperaban {esperado} ({n_oe} OE + 1 integradora).")
    else:
        r.info("CON-1", f"{n} párrafos de conclusión (no se pudo contrastar con los OE).")
    sin_pret = 0
    for _, t in pars:
        if not re.search(r"\bse\s+\w+(?:ó|aron|ieron|ió)\b|\b\w+(?:ó|aron|ieron)\b", t):
            sin_pret += 1
    if sin_pret:
        r.warn("CON-2", f"{sin_pret} párrafo(s) de conclusión sin verbo en pretérito detectable ('se identificó', 'se evidenció'…).")
    largos = [len(re.findall(r"[.!?](\s|$)", t)) for _, t in pars]
    fuera = sum(1 for k in largos if k < 3 or k > 7)
    if fuera:
        r.warn("CON-3", f"{fuera} párrafo(s) de conclusión fuera del rango recomendado de 4–6 oraciones.")
    nuevas = conjunto_citas(citas_concl) - citas_base
    if nuevas:
        r.err("CON-4", "Conclusiones con citas que no figuran en la Revisión: " + ", ".join(f"{a} {y}" for a, y in sorted(nuevas)))
    elif citas_concl:
        r.info("CON-4", "Las conclusiones mencionan autores ya presentes en la Revisión (permitido, pero revisar que no sea necesario).")
    for _, t in pars:
        if re.search(r"muy importante para el futuro|es de suma importancia|es muy importante", norm(t)):
            r.warn("CON-4", "Conclusión posiblemente trivial/vaga ('es muy importante…').")
            break


def chequear_referencias(sec, entradas, citas_cuerpo, year, r):
    if not entradas:
        r.err("REF-1", "No se detectaron entradas de referencia con formato 'Apellido, I. (año).'.")
        return
    # correspondencia
    sin_ref = []
    vistos = set()
    for c in citas_cuerpo:
        k = (c["clave"], c["anio_b"])
        if k in vistos:
            continue
        vistos.add(k)
        if not any(coincide(c, e) for e in entradas):
            sin_ref.append(c)
    ref_inst = any(INSTITUCIONAL.search(e["autor"]) for e in entradas)
    for c in sin_ref:
        if es_sigla(c["aut"]) and ref_inst:
            r.warn("REF-1", f"Cita con sigla sin coincidencia exacta en Referencias: «{c['aut']} ({c['anio']})» (línea ~{c['linea']}). Verificar que corresponda al organismo correcto.")
        else:
            r.err("REF-1", f"Cita sin entrada en Referencias: «{c['aut']} ({c['anio']})» (línea ~{c['linea']}).")
    sin_cita = [e for e in entradas if not any(coincide(c, e) for c in citas_cuerpo)]
    for e in sin_cita:
        if INSTITUCIONAL.search(e["autor"]):
            r.warn("REF-1", f"Referencia institucional sin cita con coincidencia exacta: «{e['autor']} ({e['anio']})». Verificar el uso de la sigla en el texto.")
        else:
            r.err("REF-1", f"Referencia sin cita en el texto: «{e['autor']} ({e['anio']})».")
    if not sin_ref and not sin_cita:
        r.ok("REF-1", f"Correspondencia 100 % entre citas y {len(entradas)} referencias (verificación automática).")
    # orden alfabético
    claves = [re.sub(r"[^a-z0-9 ]", "", e["autor_norm"]) for e in entradas]
    for a, b, ea, eb in zip(claves, claves[1:], entradas, entradas[1:]):
        if a > b:
            r.err("REF-2", f"Orden alfabético roto: «{ea['autor'][:40]}» antes de «{eb['autor'][:40]}».")
            break
    else:
        r.ok("REF-2", "Lista en orden alfabético.")
    # formato
    sin_cursiva = 0
    for k, e in enumerate(entradas, 1):
        raw, plano = e["raw"], e["plano"]
        et = f"Ref. {k} ({e['autor'][:30]} {e['anio']})"
        if re.search(r"\bdoi\s*:", plano, re.I):
            r.err("REF-5", f"{et}: usa la etiqueta 'DOI:'; debe ser https://doi.org/…")
        if re.search(r"(?<!https://)(?<!https://www\.)doi\.org/", plano) or re.search(r"dx\.doi\.org|http://doi\.org", plano):
            r.err("REF-5", f"{et}: el DOI debe tener el formato https://doi.org/…")
        if re.search(r"https?://\S+\.\s*$", plano):
            r.err("REF-5", f"{et}: punto final tras DOI/URL.")
        if re.search(r"recuperado de|retrieved from", plano, re.I):
            r.warn("REF-6", f"{et}: 'Recuperado de' solo se admite en contenido que cambia constantemente.")
        if re.search(r"\b(La Paz|Santa Cruz|Cochabamba|Madrid|Buenos Aires|Lima|Bogotá|México|New York|Nueva York|London|Londres|Barcelona)\s*[:,]\s*[A-ZÁÉÍÓÚÑ]", plano):
            r.warn("REF-6", f"{et}: parece incluir ciudad de la editorial (APA 7.ª la omite).")
        es_art = re.search(r"\b\d+\s*\(\d+[\w\-]*\)\s*,\s*[\d\-–e]+", plano) or re.search(r"\b\d+\s*\(\d+\)", plano)
        if es_art and not re.search(r"https?://", plano):
            r.warn("REF-5", f"{et}: artículo sin DOI/URL (verificar si existe).")
        if es_art and re.search(r"[*_]", raw) is None:
            sin_cursiva += 1
        if not re.match(r"^[A-ZÁÉÍÓÚÑ][\wáéíóúñ'’\-]+(?:\s[\wáéíóúñ'’\-]+)*,\s*(?:[A-ZÁÉÍÓÚÑ]\.\s?){1,3}", plano) and not re.match(r"^[A-ZÁÉÍÓÚÑ][^,]{3,}\.\s*\(", plano):
            r.warn("REF-2", f"{et}: el autor no sigue el patrón 'Apellido, I. I.' ni 'Institución.'.")
        low = raw.lower()
        for dom in FUENTES_PROHIBIDAS:
            if dom in low:
                r.err("REV-3", f"{et}: fuente no académica prohibida ({dom}).")
        for dom in FUENTES_DUDOSAS:
            if dom in low:
                r.warn("REV-3", f"{et}: fuente de respaldo institucional dudoso ({dom}).")
    if sin_cursiva:
        r.info("REF-4", f"{sin_cursiva} artículo(s): no se puede comprobar la cursiva de revista/volumen en texto plano (verificar en Word).")
    # recencia y corte temporal a octubre 2026
    anios = [int(e["anio_b"]) for e in entradas if e["anio_b"].isdigit()]
    if anios:
        lim = year - 5
        rec = sum(1 for a in anios if a >= lim)
        pct = 100.0 * rec / len(anios)
        if pct >= 70:
            r.ok("ACT-2", f"Actualidad de fuentes: {rec}/{len(anios)} ({pct:.0f} %) en los últimos 5 años ({lim}–{year}) (meta ≥ 70 %).")
        elif pct >= 60:
            r.warn("ACT-2", f"Actualidad de fuentes: {rec}/{len(anios)} ({pct:.0f} %) en {lim}–{year}. Se recomienda alcanzar ≥ 70 % para postgrado a {year}.")
        else:
            r.err("ACT-2", f"Baja actualidad de fuentes: solo {rec}/{len(anios)} ({pct:.0f} %) en {lim}–{year} (se exige ≥ 70 % según norma de actualidad a octubre {year}).")
        rec_punta = sum(1 for a in anios if a >= 2024)
        if rec_punta > 0:
            r.ok("ACT-2", f"Literatura reciente de vanguardia (2024–{year}): {rec_punta} fuente(s) detectada(s) (corte a octubre {year}).")
        else:
            r.warn("ACT-2", f"No se detectaron fuentes publicadas entre 2024 y {year}. La skill exige priorizar información nueva y actualizada a octubre {year}.")
    n = len(entradas)
    if n < 5:
        r.err("REV-2", f"Solo {n} referencias (mínimo 5 fuentes académicas).")
    elif n < 10:
        r.info("REV-2", f"{n} referencias; la Guía sugiere 10–15 para una revisión robusta.")


# --------------------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("archivo")
    ap.add_argument("--titulo", help="Título del trabajo (si no está en el archivo como 'Título:' o '# ')")
    ap.add_argument("--year", type=int, default=datetime.date.today().year)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--parcial", action="store_true",
                    help="Borrador incompleto: los acápites ausentes se informan como pendientes, no como error")
    args = ap.parse_args()

    lines, paras = leer(args.archivo)
    fmt = "docx" if args.archivo.lower().endswith(".docx") else "txt"
    r = Reporte()
    secs = detectar_secciones(lines)
    for s in secs.values():
        s["fmt"] = fmt

    # Comprobación de estilos y numeración automática (FOR-6 / plantilla apa7ma.docx)
    duplicados_num = []
    num_manual_estilos = []
    for p in paras:
        txt = p["texto"].strip()
        est = (p["estilo"] or "").lower()
        if any(h in est for h in ["ttulo", "heading", "titulo"]):
            if re.match(r"^\d+(\.\d+)*\.?\s+", txt):
                num_manual_estilos.append((p["estilo"], txt))
        if re.match(r"^\s*#+\s*\d+[\.\)]\s*\d+[\.\)]", p["texto"]) or re.match(r"^\s*\d+\.\s*\d+\.\s+[A-Za-z]", p["texto"]):
            duplicados_num.append(txt)
    if num_manual_estilos:
        for est, txt in num_manual_estilos[:3]:
            r.err("FOR-6", f"En el estilo Word '{est}', el título «{txt}» contiene numeración escrita a mano. La plantilla 'apa7ma.docx' ya tiene numeración automática vinculada a sus estilos de título; debe escribirse el texto sin números ('{re.sub(r'^\d+(\.\d+)*\.?\s*', '', txt)}') para evitar duplicados ('1. 1. ...').")
    elif any(p["estilo"] for p in paras if (p["estilo"] or "").lower().startswith("ttulo")):
        r.ok("FOR-6", "Los estilos de título Word de la plantilla 'apa7ma.docx' se usan sin numeración manual redundante (numeración automática activa).")
    if duplicados_num:
        r.err("FOR-6", f"Se detectó doble numeración en títulos: «{duplicados_num[0]}».")

    # Estructura
    requeridas = ["introduccion", "problema", "objetivos", "revision", "discusion", "conclusiones", "referencias"]
    faltan = [k for k in requeridas if k not in secs]
    if faltan and args.parcial:
        r.info("EST-1", "Acápites aún no presentes (modo parcial): " + ", ".join(faltan) + ".")
    elif faltan:
        r.err("EST-1", "Acápites no detectados: " + ", ".join(faltan) + " (revisar encabezados exactos: '1. Introducción', '2. Planteamiento del Problema', …).")
    else:
        r.ok("EST-1", "Acápites 1–4, 6–8 detectados.")
    if "resumen" not in secs and not args.parcial:
        r.warn("RES-1", "No se detectó el encabezado 'Resumen'.")
    if "terminos" not in secs:
        r.info("TER-4", "No hay acápite 5 independiente: válido solo si la Definición de términos está integrada en la Revisión.")
    pos = [ORDEN.index(k) for k, _ in sorted(((k, v["idx"]) for k, v in secs.items()), key=lambda x: x[1])]
    if pos != sorted(pos):
        r.err("EST-1", "Los acápites no siguen el orden institucional de entrega.")
    if "apendices" in secs and "anexo" in norm(secs["apendices"]["titulo"]):
        r.err("APE-1", "Se usa 'Anexo(s)': el término vigente es 'Apéndice(s)'.")
    # REF-7: acápite denominado 'Bibliografía'
    for l in lines:
        t = limpiar(l)
        if t and len(t) <= 80 and re.match(r"^(?:\d+[\.\)]?\s*)?bibliografia$", norm(t)):
            r.err("REF-7", "El acápite se titula 'Bibliografía': debe llamarse 'Referencias'.")
            break
    if "referencias" in secs and "apendices" in secs and secs["apendices"]["idx"] < secs["referencias"]["idx"]:
        r.err("APE-2", "Los Apéndices deben ir después de las Referencias.")

    # Título
    titulo = args.titulo
    if not titulo:
        for idx, l in enumerate(lines):
            m = re.match(r"^\s*(?:#\s+|t[ií]tulo\s*:\s*)(.+)$", l, re.I)
            if m:
                cand = limpiar(m.group(1))
                if norm(cand) in ("titulo", "titulo:"):
                    # El título real está en la siguiente línea no vacía
                    for next_l in lines[idx+1:idx+5]:
                        if limpiar(next_l):
                            cand = limpiar(next_l)
                            break
                if not any(re.match(rx, norm(cand)) for _, rx in SEC):
                    titulo = cand
                    break
    if titulo:
        chequear_titulo(titulo, r)
    else:
        r.info("TIT-1", "No se identificó el título (usar --titulo \"...\").")

    # Resumen
    if "resumen" in secs:
        chequear_resumen(secs["resumen"], r)

    # Introducción
    if "introduccion" in secs:
        s = secs["introduccion"]
        if fmt == "docx":
            if not re.match(r"^(1[\.\)]?\s*)?introducci", norm(s["titulo"])):
                r.warn("INT-1", "El encabezado de Introducción no corresponde a 'Introducción'.")
            elif not re.match(r"^1[\.\)]", norm(s["titulo"])):
                r.ok("INT-1", "Encabezado 'Introducción' sin número manual (correcto: la plantilla Word numera automáticamente).")
            else:
                r.ok("INT-1", "Encabezado '1. Introducción' detectado.")
        else:
            if not re.match(r"^1[\.\)]?\s*introducci", norm(s["titulo"])):
                r.warn("INT-1", "El encabezado debería ser exactamente '1. Introducción'.")
        pars = parrafos(s["lineas"], 15)
        if len(pars) < 5:
            r.warn("INT-2", f"La Introducción tiene {len(pars)} párrafos (se esperan ≥ 5 orientadores: global, local, brecha, objetivo, estructura).")
        else:
            r.ok("INT-2", f"La Introducción tiene {len(pars)} párrafos.")
        txt = norm(" ".join(l for _, l in pars))
        if not re.search(r"se organiza|se estructura|estructura del documento|acapite|apartado|capitulo", txt):
            r.warn("INT-2", "No se detectó el párrafo de estructura que anticipa los acápites.")
        if re.search(r"\b(se concluy[oó]|se concluye|las conclusiones? (de|del) (este|presente))\b", txt):
            r.warn("INT-3", "La Introducción parece anticipar conclusiones/resultados.")
        cs = conjunto_citas(extraer_citas(s["lineas"]))
        if len(cs) < 2:
            r.warn("INT-4", f"La Introducción cita {len(cs)} fuente(s); se exigen ≥ 2 (una global y una nacional).")

    # Problema
    if "problema" in secs:
        s = secs["problema"]
        txt = " ".join(s["lineas"])
        # pregunta
        preg = re.findall(r"¿[^?]+\?", txt)
        if len(preg) == 1:
            r.ok("PRO-4", "Una sola oración interrogativa de formulación.")
            p = norm(preg[0])
            if re.match(r"^¿\s*(es|son|existe|existen|puede|pueden|hay|se|ha|han|deben?|influye|tiene|tienen)\b", p):
                r.warn("PRO-4", "La pregunta parece responderse con sí/no.")
            if not re.search(r"\b(19|20)\d{2}\b|periodo|durante|ultimos", p):
                r.warn("PRO-4", "La pregunta no muestra el CUÁNDO.")
        elif len(preg) == 0:
            r.err("PRO-4", "No se detectó la pregunta de investigación (¿…?).")
        else:
            r.err("PRO-4", f"Se detectaron {len(preg)} preguntas; la formulación debe ser una sola oración interrogativa.")
        if re.search(r"\bhip[oó]tesis\b", norm(txt)):
            r.warn("PRO-5", "Se menciona 'hipótesis': la monografía de revisión no formula hipótesis.")
        cs = extraer_citas(s["lineas"])
        if len(conjunto_citas(cs)) < 2:
            r.warn("PRO-2", "El Planteamiento cita menos de 2 fuentes: la existencia del problema debe demostrarse con evidencia publicada.")
        if not re.search(r"\d", " ".join(s["lineas"])):
            r.warn("PRO-3", "No se detectan cifras: la brecha debe cuantificarse con datos citados.")
        anios_prob = [int(c["anio_b"]) for c in cs if c["anio_b"].isdigit()]
        if anios_prob and not any(a >= 2024 for a in anios_prob):
            r.warn("PRO-7", f"Las fuentes del Planteamiento no incluyen datos recientes (2024–{args.year}); verificar que las cifras del problema reflejen la situación más actualizada a octubre {args.year} (ACT-1).")
        elif anios_prob and any(a >= 2024 for a in anios_prob):
            r.ok("PRO-7", f"El Planteamiento incluye fuentes y datos recientes (2024–{args.year}), conforme a ACT-1.")
        if not any(g in norm(txt) for g in BOLIVIA_TERMINOS):
            r.err("GEO-1", "El Planteamiento del Problema no contiene referencias a Bolivia ni a sus departamentos o ciudades (la investigación debe enfocarse exclusivamente en Bolivia).")
        else:
            r.ok("GEO-1", "Planteamiento del Problema contextualizado en Bolivia.")

    # Objetivos
    n_oe = None
    if "objetivos" in secs:
        n_oe = chequear_objetivos(secs["objetivos"], r)

    # Citas por sección
    def citas_de(*keys):
        out = []
        for k in keys:
            if k in secs:
                out += extraer_citas(secs[k]["lineas"], secs[k]["inicio"])
        return out
    c_rev = citas_de("revision")
    c_ter = citas_de("terminos")
    c_dis = citas_de("discusion")
    c_con = citas_de("conclusiones")
    c_int = citas_de("introduccion")
    c_pro = citas_de("problema")
    base_rev = conjunto_citas(c_rev) | conjunto_citas(c_ter)

    # Revisión
    if "revision" in secs:
        chequear_revision(secs["revision"], c_rev, r)

    # Términos
    if "terminos" in secs:
        n_t = len([1 for l in secs["terminos"]["lineas"] if l.strip() and not re.match(r"^#+\s", l.strip())])
        if not (5 <= n_t <= 10 + 3):
            r.warn("TER-1", f"Se detectan {n_t} líneas de contenido; se esperan 5–10 términos.")
        if not extraer_citas(secs["terminos"]["lineas"]):
            r.err("TER-2", "La Definición de términos no cita fuentes académicas.")

    # Discusión
    if "discusion" in secs:
        nuevas = conjunto_citas(c_dis) - base_rev
        if nuevas:
            r.err("DIS-6", "Discusión con fuentes que no están en la Revisión: " + ", ".join(f"{a} {y}" for a, y in sorted(nuevas)))
        else:
            r.ok("DIS-6", "La Discusión no introduce autores nuevos respecto de la Revisión.")
        td = norm(" ".join(secs["discusion"]["lineas"]))
        if not re.search(r"bolivia|santa cruz|cruce", td):
            r.warn("DIS-4", "La Discusión no menciona implicaciones para Bolivia/Santa Cruz.")
        if not re.search(r"limitacion|limitaciones", td):
            r.warn("DIS-5", "No se detectan 'limitaciones' de la literatura revisada.")
        if not re.search(r"lineas? de investigacion|investigaciones futuras|estudios futuros|futura", td):
            r.warn("DIS-5", "No se detectan líneas de investigación futura.")
        if not re.search(r"esta (investigacion|monografia|revision)|el presente (trabajo|estudio)|postura", td):
            r.warn("DIS-3", "No se detecta una postura propia explícita del investigador.")

    # Conclusiones
    if "conclusiones" in secs:
        chequear_conclusiones(secs["conclusiones"], n_oe, c_con, base_rev | conjunto_citas(c_dis), r)

    # Primera persona (cuerpo)
    cuerpo_keys = ["introduccion", "problema", "objetivos", "revision", "terminos", "discusion", "conclusiones"]
    hits = []
    for k in cuerpo_keys:
        if k in secs:
            for i, l in enumerate(secs[k]["lineas"]):
                if PRIMERA_PERSONA.search(l):
                    hits.append(secs[k]["inicio"] + i)
    if hits:
        r.err("FOR-4", f"Posible primera persona en {len(hits)} línea(s) (p. ej., líneas {', '.join(map(str, hits[:6]))}). Usar tercera persona impersonal.")
    else:
        r.ok("FOR-4", "No se detectó primera persona en el cuerpo.")

    # Referencias
    if "referencias" in secs:
        entradas = parsear_referencias(secs["referencias"]["lineas"])
        # "et al." desde la primera cita
        todas = c_int + c_pro + c_rev + c_ter + c_dis + c_con
        for c in todas:
            if "et al" not in c["aut"] and n_autores(c["aut"]) >= 3:
                f = r.err if c["tipo"] == "par" else r.warn
                f("REV-6", f"Cita con 3+ autores sin 'et al.' desde la primera aparición: «{c['aut']} ({c['anio']})» (línea ~{c['linea']}).")
        # alertas de fuentes prohibidas en texto
        txt_all = " ".join(lines).lower()
        for dom in FUENTES_PROHIBIDAS:
            if dom in txt_all and not any(dom in e["raw"].lower() for e in entradas):
                r.err("REV-3", f"Se menciona una fuente no académica prohibida en el texto ({dom}).")
        chequear_referencias(secs["referencias"], entradas, todas, args.year, r)

    # Salida
    if args.json:
        print(json.dumps(r.items, ensure_ascii=False, indent=2))
        return
    sym = {"ERR": "✖", "AVISO": "⚠", "OK": "✔", "INFO": "ℹ"}
    orden = {"ERR": 0, "AVISO": 1, "INFO": 2, "OK": 3}
    print(f"AUDITORÍA — {args.archivo}")
    print("=" * 60)
    for nivel in ("ERR", "AVISO", "INFO", "OK"):
        grupo = [i for i in r.items if i["nivel"] == nivel]
        if not grupo:
            continue
        titulo = {"ERR": "ERRORES (incumplimientos objetivos)", "AVISO": "AVISOS (revisar con criterio)",
                  "INFO": "INFORMACIÓN", "OK": "CUMPLE"}[nivel]
        print(f"\n{titulo}")
        for i in grupo:
            print(f"  {sym[nivel]} [{i['id']}] {i['msg']}")
    n_err = sum(1 for i in r.items if i["nivel"] == "ERR")
    n_av = sum(1 for i in r.items if i["nivel"] == "AVISO")
    n_ok = sum(1 for i in r.items if i["nivel"] == "OK")
    print("\n" + "=" * 60)
    print(f"Resumen: {n_err} errores · {n_av} avisos · {n_ok} cumplimientos")
    print("Nota: verificación automática y heurística; no confirma que las fuentes existan ni sustituye la lectura crítica.")


if __name__ == "__main__":
    main()