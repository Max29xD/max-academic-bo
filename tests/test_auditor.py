"""Tests para las funciones puras y de mayor riesgo de auditor_utils.py.

Ejecutar:  python tests/test_auditor.py
Estas son pruebas de regresión: documentan el comportamiento actual de cada
función para que un cambio futuro que lo altere falle ruidosamente.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from auditor_utils import (
    anio_base,
    clave_autor,
    coincide,
    es_sigla,
    extraer_citas,
    n_autores,
    norm,
    palabras,
    parsear_referencias,
    primer_verbo,
    quitar_enumeracion,
    subsecuencia,
)

FAILURES = []


def check(name, cond, extra=""):
    if cond:
        print(f"  ok   {name}")
    else:
        FAILURES.append(name)
        print(f"  FAIL {name} {extra}")


# ---------- norm / palabras ----------
check("norm tildes", norm("Cochabamba") == "cochabamba")
check("norm mayus", norm("SANTA CRUZ") == "santa cruz")
check("palabras cuenta", len(palabras("Hola, mundo!")) == 2)
check("palabras guion", len(palabras("e-learning")) == 1)

# ---------- anio_base (requiere dígitos al inicio; "(2024)" no califica) ----------
check("anio_base año", anio_base("2024") == "2024")
check("anio_base s.f.", anio_base("s. f.") == "s.f.")
check("anio_base año letra", anio_base("2024a") == "2024")

# ---------- n_autores (divide en comas, por eso "Apellido, I." cuenta 2) ----------
check("n_autores uno", n_autores("Quispe, A.") == 2)
check("n_autores dos", n_autores("Quispe, A. & Ramos, B.") == 4)
check("n_autores et al", n_autores("Quispe, A. et al.") == 2)

# ---------- clave_autor ----------
check("clave_autor simple", clave_autor("Quispe, A.") == "quispe")
check("clave_autor et al", clave_autor("Quispe, A. et al.") == "quispe")
check("clave_autor sigla", clave_autor("CEPAL (2024)") == "cepal")

# ---------- es_sigla ----------
check("es_sigla si", es_sigla("CEPAL") is True)
check("es_sigla no esp", es_sigla("Banco Central") is False)
check("es_sigla con guion", es_sigla("ONG-B") is False)

# ---------- subsecuencia (sensible a mayúsculas) ----------
check("subsecuencia true", subsecuencia("ABC", "A x B y C") is True)
check("subsecuencia false", subsecuencia("XYZ", "A B C") is False)

# ---------- extraer_citas ----------
citas = extraer_citas(["Según Quispe (2024), el problema es grave."])
check("extraer_citas narrativo", len(citas) == 1 and citas[0]["aut"] == "Quispe" and citas[0]["anio"] == "2024")

citas = extraer_citas(["(Quispe, 2024) y (Ramos, 2025) coinciden."])
check("extraer_citas parentetico", len(citas) == 2)
check("extraer_citas claves", {c["clave"] for c in citas} == {"quispe", "ramos"})

# ---------- parsear_referencias ----------
refs = parsear_referencias([
    "Quispe, A. (2024). Título del artículo. Revista Boliviana, 10(2), 45-60.",
    "  segunda línea de la misma referencia que continúa aquí.",
    "Ramos, B. (2025). Otro libro. Editorial X.",
])
check("parsear_referencias cuenta", len(refs) == 2)
check("parsear_referencias une continua", "segunda línea" in refs[0]["raw"])
check("parsear_referencias clave", refs[0]["clave"] == "quispe")
check("parsear_referencias anio", refs[0]["anio_b"] == "2024")

# ---------- coincide (ambos lados llevan 'clave') ----------
c = {"clave": "quispe", "anio_b": "2024", "aut": "Quispe, A."}
r = {"clave": "quispe", "autor": "Quispe, A.", "autor_norm": "quispe, a.", "anio_b": "2024", "acron": "q"}
check("coincide mismo", coincide(c, r) is True)

c2 = {"clave": "ramos", "anio_b": "2025", "aut": "Ramos, B."}
check("coincide distinto año", coincide(c2, r) is False)

# ---------- quitar_enumeracion ----------
check("quitar OE", quitar_enumeracion("OE1. Analizar el problema.") == "Analizar el problema.")
check("quitar numero", quitar_enumeracion("1. Introducción") == "Introducción")

# ---------- primer_verbo ----------
check("primer_verbo infinitivo", primer_verbo("Analizar la situación.") == "Analizar")
check("primer_verbo conjugado", primer_verbo("El problema afecta a todos.") == "El")

print()
if FAILURES:
    print(f"FALLOS: {len(FAILURES)} -> {', '.join(FAILURES)}")
    sys.exit(1)
print("TODOS LOS TESTS PASARON")
