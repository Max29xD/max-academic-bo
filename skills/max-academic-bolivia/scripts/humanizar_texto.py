#!/usr/bin/env python3
"""
Módulo y CLI 'Humanamente' adaptado a Monografías de Postgrado EIP-FINOR-UAGRM.
Basado en los principios de 'vicentealvarezasencio/humanamente' y 'blader/humanizer'.

Detecta, audita y sugiere correcciones para los tics y patrones sintéticos típicos
de la redacción por Inteligencia Artificial en español, protegiendo estrictamente:
- Citas parentéticas y narrativas APA 7ma edición: (Autor, Año, p. X).
- Siglas institucionales y normativas: UAGRM, FINOR, EIP, INE, BCB, ASFI, AGETIC.
- Constructos teóricos y conceptos técnicos de la disciplina.
- Estilo en tercera persona impersonal exigido por la EIP-UAGRM.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# =========================================================================
# Diccionarios y Patrones Canónicos de IA en Español (Humanamente)
# =========================================================================

# 1. Falsos paralelismos ("no solo X, sino también Y")
PATRON_PARALELISMO = re.compile(
    r'\bno\s+solo\b[\w\s,áéíóúñü]{3,80}?\bsino\b(?:\s+(?:tambi[eé]n|que\s+tambi[eé]n|adem[aá]s))?',
    re.IGNORECASE
)

# 2. Gerundios de consecuencia o posterioridad (calco sintáctico anglosajón)
PATRON_GERUNDIO_CONSECUENCIA = re.compile(
    r',\s*(logrando|permitiendo|garantizando|propiciando|facilitando|generando|provocando|dando\s+lugar)\s+(?:as[íi]|de\s+este\s+modo|con\s+ello|asimismo)?',
    re.IGNORECASE
)

# 3. Aperturas cliché y muletillas de relleno infladas
APERTURAS_FLUFF = [
    "en el panorama actual",
    "en un mundo en constante cambio",
    "en un mundo en constante evolución",
    "en la era digital",
    "en la sociedad del conocimiento",
    "a lo largo de la historia",
    "es crucial destacar",
    "es imperativo señalar",
    "es menester destacar",
    "es menester señalar",
    "cabe destacar que",
    "cabe resaltar que",
    "cabe señalar que",
    "cabe mencionar que",
    "vale la pena destacar",
    "vale la pena mencionar",
    "resulta pertinente señalar",
    "resulta fundamental destacar",
    "no se puede subestimar",
    "en resumen, podemos decir",
    "a modo de colofón",
]

# 4. Vocabulario inflado y metáforas trilladas de IA
CLICHES_VOCABULARIO = [
    "un tapiz de",
    "un testimonio de",
    "la piedra angular",
    "una piedra angular",
    "el faro de",
    "un faro de",
    "el crisol de",
    "un crisol de",
    "un sinfín de",
    "desentrañar la complejidad",
    "navegar el complejo panorama",
    "navegar por el complejo panorama",
    "juega un papel fundamental",
    "juega un rol fundamental",
    "desempeña un rol crucial",
    "desempeña un papel crucial",
    "de vital importancia",
]

# 5. Adjetivación laudatoria / hiperbólica típica de LLMs
ADJETIVOS_IA = [
    "revolucionario", "revolucionaria", "revolucionarios", "revolucionarias",
    "transformador", "transformadora", "transformadores", "transformadoras",
    "paradigmático", "paradigmática", "paradigmáticos", "paradigmáticas",
    "holístico", "holística", "holísticos", "holísticas",
    "disruptivo", "disruptiva", "disruptivos", "disruptivas",
    "fascinante", "fascinantes",
    "multifacético", "multifacética", "multifacéticos", "multifacéticas",
    "vertiginoso", "vertiginosa", "vertiginosos", "vertiginosas",
    "intrínseco", "intrínseca", "intrínsecos", "intrínsecas",
]

# 6. Rayas anglosajonas (guion largo o semirraya)
PATRON_EMDASH = re.compile(r'[—–]')

# 7. Regla de tres compulsiva (adjetivo, adjetivo y adjetivo)
PATRON_REGLA_TRES = re.compile(
    r'\b(\w+[\wáéíóúñü]+),\s+(\w+[\wáéíóúñü]+)\s+y\s+(\w+[\wáéíóúñü]+)\b',
    re.IGNORECASE
)

# Sustituciones académicas recomendadas
SUSTITUCIONES_SUGERIDAS = {
    "juega un papel fundamental": "influye de manera directa",
    "juega un rol fundamental": "constituye un factor relevante",
    "desempeña un papel crucial": "condiciona directamente",
    "desempeña un rol crucial": "determina de forma sustantiva",
    "es de vital importancia": "resulta relevante",
    "en conclusión": "en síntesis",
    "a modo de resumen": "sintéticamente",
    "a modo de colofón": "en síntesis",
    "la piedra angular": "el fundamento principal",
    "un tapiz de": "un entramado de",
    "un sinfín de": "múltiples",
    "cabe destacar que": "se evidencia que",
    "es imperativo señalar que": "los datos indican que",
    "es crucial destacar que": "conviene precisar que",
    "en el panorama actual": "en el contexto contemporáneo",
}


# =========================================================================
# Enmascaramiento de Citas y Términos Protegidos
# =========================================================================

def enmascarar_elementos_protegidos(texto: str) -> tuple[str, dict[str, str]]:
    """Protege citas APA 7, URLs y siglas institucionales para no alterarlas al auditar o humanizar."""
    mapa = {}
    contador = 0

    def guardar(match_text: str) -> str:
        nonlocal contador
        token = f"___PROT_{contador}___"
        mapa[token] = match_text
        contador += 1
        return token

    # 1. URLs
    texto_mod = re.sub(r'https?://\S+', lambda m: guardar(m.group(0)), texto)

    # 2. Citas parentéticas APA 7: (Apellido, 2024) o (Apellido et al., 2024, p. 12)
    texto_mod = re.sub(
        r'\([A-ZÁÉÍÓÚ][^)]*?(?:19|20)\d{2}[^)]*?\)',
        lambda m: guardar(m.group(0)),
        texto_mod
    )

    # 3. Citas narrativas APA 7: Apellido (2024)
    texto_mod = re.sub(
        r'\b[A-ZÁÉÍÓÚ][a-záéíóúñü]+(?:\s+(?:y|&)\s+[A-ZÁÉÍÓÚ][a-záéíóúñü]+|\s+et\s+al\.)?\s*\((?:19|20)\d{2}\)',
        lambda m: guardar(m.group(0)),
        texto_mod
    )

    return texto_mod, mapa


def desenmascarar_elementos_protegidos(texto: str, mapa: dict[str, str]) -> str:
    """Restaura las citas y elementos protegidos en el texto final."""
    for token, original in mapa.items():
        texto = texto.replace(token, original)
    return texto


# =========================================================================
# Motor de Auditoría Humanamente
# =========================================================================

def auditar_tics_humanamente(texto: str) -> dict:
    """
    Analiza un texto contra la rúbrica Humanamente adaptada al español académico.
    Retorna un diccionario con hallazgos categorizados, puntaje y sugerencias.
    """
    texto_limpio, _ = enmascarar_elementos_protegidos(texto)
    lineas = texto_limpio.splitlines()

    hallazgos = []
    penalizacion = 0

    for idx, linea in enumerate(lineas, start=1):
        l_str = linea.strip()
        if not l_str or l_str.startswith("#") or l_str.startswith("|"):
            continue

        # 1. Falsos paralelismos
        for m in PATRON_PARALELISMO.finditer(l_str):
            hallazgos.append({
                "linea": idx,
                "categoria": "Falso Paralelismo",
                "codigo": "HUM-1",
                "texto": m.group(0),
                "mensaje": f"Fórmula artificial «{m.group(0)}». En español natural, prefiere oraciones coordinadas directas.",
                "severidad": "AVISO",
            })
            penalizacion += 5

        # 2. Gerundios de consecuencia no normativos
        for m in PATRON_GERUNDIO_CONSECUENCIA.finditer(l_str):
            hallazgos.append({
                "linea": idx,
                "categoria": "Gerundio de Consecuencia",
                "codigo": "HUM-2",
                "texto": m.group(0),
                "mensaje": f"Gerundio de consecuencia no normativo «{m.group(0)}». Usa «lo que permite...» o punto y seguido.",
                "severidad": "ERROR",
            })
            penalizacion += 7

        # 3. Rayas o guiones largos anglosajones
        for m in PATRON_EMDASH.finditer(l_str):
            hallazgos.append({
                "linea": idx,
                "categoria": "Guion Largo / Raya",
                "codigo": "HUM-3",
                "texto": m.group(0),
                "mensaje": "Guion largo («—») típico de IA anglosajona. Usa comas, paréntesis o subordinación sintáctica.",
                "severidad": "ERROR",
            })
            penalizacion += 8

        # 4. Aperturas cliché y muletillas infladas
        low = l_str.lower()
        for ap in APERTURAS_FLUFF:
            if ap in low:
                hallazgos.append({
                    "linea": idx,
                    "categoria": "Apertura Cliché / Relleno",
                    "codigo": "HUM-4",
                    "texto": ap,
                    "mensaje": f"Muletilla de relleno artificial «{ap}». Comienza directamente con los datos o el sujeto.",
                    "severidad": "AVISO",
                })
                penalizacion += 4

        # 5. Clichés metafóricos
        for cl in CLICHES_VOCABULARIO:
            if cl in low:
                sug = SUSTITUCIONES_SUGERIDAS.get(cl, "expresión académica objetiva")
                hallazgos.append({
                    "linea": idx,
                    "categoria": "Metáfora / Cliché IA",
                    "codigo": "HUM-5",
                    "texto": cl,
                    "mensaje": f"Cliché de IA «{cl}». Sugerencia de sustitución: «{sug}».",
                    "severidad": "AVISO",
                })
                penalizacion += 4

        # 6. Adjetivos hiperbólicos
        for adj in ADJETIVOS_IA:
            pattern = rf'\b{re.escape(adj)}\b'
            if re.search(pattern, low):
                hallazgos.append({
                    "linea": idx,
                    "categoria": "Adjetivo Inflado",
                    "codigo": "HUM-6",
                    "texto": adj,
                    "mensaje": f"Adjetivación grandilocuente de IA «{adj}». Prefiere terminología científica sobria.",
                    "severidad": "AVISO",
                })
                penalizacion += 3

    # Calcular Índice de Prosa Humana y Orgánica (0 a 100)
    puntaje = max(0, 100 - penalizacion)
    nivel = "Excelente (Prosa Orgánica Humana)" if puntaje >= 90 else (
        "Aceptable (Pocos Tics de IA)" if puntaje >= 75 else "Artificial (Alta Densidad de Tics de IA)"
    )

    return {
        "puntaje_humanidad": puntaje,
        "diagnostico": nivel,
        "total_hallazgos": len(hallazgos),
        "hallazgos": hallazgos,
    }


# =========================================================================
# Generador de Sugerencias de Reescritura Automática
# =========================================================================

def sugerir_humanizacion(parrafo: str) -> str:
    """
    Aplica transformaciones conservadoras del protocolo Humanamente:
    - Sustituye clichés conocidos por alternativas académicas.
    - Reemplaza guiones largos por comas o paréntesis.
    - Corrige gerundios de consecuencia comunes.
    - Preserva intactas todas las citas parentéticas.
    """
    parr_prot, mapa = enmascarar_elementos_protegidos(parrafo)
    resultado = parr_prot

    # 1. Reemplazar guiones largos por comas
    resultado = re.sub(r'\s*[—–]\s*', ', ', resultado)

    # 2. Reemplazar gerundios de consecuencia más frecuentes
    resultado = re.sub(
        r',\s*logrando\s+as[íi]\b',
        ', lo cual permite alcanzar',
        resultado,
        flags=re.IGNORECASE
    )
    resultado = re.sub(
        r',\s*permitiendo\s+de\s+este\s+modo\b',
        ', lo que hace posible',
        resultado,
        flags=re.IGNORECASE
    )
    resultado = re.sub(
        r',\s*garantizando\s+con\s+ello\b',
        ', y con ello asegura',
        resultado,
        flags=re.IGNORECASE
    )

    # 3. Sustituciones directas de clichés
    for original, reemplazo in SUSTITUCIONES_SUGERIDAS.items():
        patron = re.compile(rf'\b{re.escape(original)}\b', re.IGNORECASE)
        resultado = patron.sub(reemplazo, resultado)

    # Restaurar elementos protegidos
    return desenmascarar_elementos_protegidos(resultado, mapa)


# =========================================================================
# CLI
# =========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Auditor y Humanizador de Estilo en Español 'Humanamente' (EIP-FINOR-UAGRM / APA 7)"
    )
    parser.add_argument("archivo", type=Path, help="Ruta al archivo Markdown (.md) a auditar")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON estructurado")
    parser.add_argument("--sugerir", action="store_true", help="Muestra versión del texto con sustituciones sugeridas")
    args = parser.parse_args()

    if not args.archivo.exists():
        print(f"Error: No se encontró el archivo en {args.archivo}", file=sys.stderr)
        sys.exit(1)

    contenido = args.archivo.read_text(encoding="utf-8")
    reporte = auditar_tics_humanamente(contenido)

    if args.json:
        print(json.dumps(reporte, indent=2, ensure_ascii=False))
        return

    print("=" * 75)
    print("AUDITORÍA DE ESTILO HUMANAMENTE — ESPAÑOL ACADÉMICO (EIP-FINOR-UAGRM)")
    print("=" * 75)
    print(f"Archivo auditado: {args.archivo.name}")
    print(f"Puntaje de Humanidad: {reporte['puntaje_humanidad']} / 100")
    print(f"Diagnóstico: {reporte['diagnostico']}")
    print(f"Tics de IA detectados: {reporte['total_hallazgos']}")
    print("-" * 75)

    if not reporte["hallazgos"]:
        print("✔ No se detectaron patrones sintéticos ni clichés de IA. Prosa orgánica y natural.")
    else:
        for h in reporte["hallazgos"]:
            icono = "✖" if h["severidad"] == "ERROR" else "⚠"
            print(f"{icono} [Línea {h['linea']}] [{h['codigo']}] {h['categoria']}: {h['mensaje']}")

    if args.sugerir:
        print("\n" + "=" * 75)
        print("PROPUESTA DE TEXTO HUMANIZADO (CONSERVANDO CITAS APA Y TÉRMINOS):")
        print("=" * 75)
        print(sugerir_humanizacion(contenido))


if __name__ == "__main__":
    main()
