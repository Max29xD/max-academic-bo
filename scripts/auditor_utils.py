"""Utilidades puras del auditor de monografías.

Contiene funciones sin efectos secundarios (salvo `leer`, que solo lee archivos)
y constantes de configuración. `auditar_monografia.py` las importa y las
orquesta; aquí no hay lógica específica de cada sección.
"""
import re
import unicodedata
import zipfile
from pathlib import Path
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
    if Path(path).suffix.lower() == ".docx":
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
    r"Fundaci[oó]n|Observatorio|Naciones|Departamento|Municipio|Prefectura|Viceministerio)\b", re.IGNORECASE)


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
            m_narr = RX_NARR.match(cont)
            if m_narr:
                aut = autor_narrativo(l[:m.start()])
                if aut:
                    citas.append({"aut": aut, "anio": m_narr.group(1), "linea": ln + offset, "tipo": "narr"})
                continue
            for parte in cont.split(";"):
                parte = re.sub(r"^\s*(v[eé]ase|ver|cf\.|p\.\s?ej\.,?|por ejemplo,?|e\.g\.,?)\s*", "", parte, flags=re.IGNORECASE)
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


# --------------------------------------------------------------------------- texto

def parrafos(lines, min_pal=1):
    out = []
    for i, l in enumerate(lines):
        t = l.strip()
        if t and not re.match(r"^#+\s", t) and len(palabras(t)) >= min_pal:
            out.append((i + 1, t))
    return out


def quitar_enumeracion(t):
    t = re.sub(r"^\s*objetivo\s+(general|espec[ií]fico)\s*\d*\s*[:.\-–]\s*", "", t, flags=re.IGNORECASE)
    pat = re.compile(r"^\s*(\d+[\.\)]|[-•*]|OE\s?\d+[:.]?|[a-z]\)|\d+\.\d+\.?)\s*", flags=re.IGNORECASE)
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


# --------------------------------------------------------------------------- constantes de chequeo (usadas por las reglas de sección)

VERBOS_CAMPO = {"encuestar", "medir", "calcular"}
VERBOS_CAMPO_AFINES = {"entrevistar", "experimentar", "muestrear", "cuestionar", "sondear", "cronometrar"}
VERBOS_BAJOS_OG = {"conocer", "saber", "recordar", "listar", "enumerar", "nombrar", "revisar", "estudiar", "investigar", "ver", "tratar", "mostrar"}
PRIMERA_PERSONA = re.compile(
    r"\b(yo|nosotros|nosotras|nuestro|nuestra|nuestros|nuestras|mi|mis|considero|creo que|pienso|"
    r"analic[eé]|conclu[ií]|concluimos|analizamos|observamos|encontramos|realic[eé]|realizamos|propongo|proponemos)\b",
    re.IGNORECASE)
MARCADORES_CONTRASTE = re.compile(
    r"mientras que|sin embargo|en contraste|no obstante|por el contrario|a diferencia|diverg|coincid|"
    r"en cambio|contrast|por su parte|converg|pese a|aunque|difier|discrep|en consonancia|de modo similar|de manera similar",
    re.IGNORECASE)
FUENTES_PROHIBIDAS = ["wikipedia", "rincondelvago", "rincón del vago", "monografias.com", "buenastareas", "tareasya", "ecured"]
FUENTES_DUDOSAS = ["slideshare", "scribd", "blogspot", "wordpress", "medium.com", "youtube.com", "facebook.com"]
