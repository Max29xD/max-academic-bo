# Protocolo Humanamente: Redacción Natural y Anti-Patrones de IA en Español
**Integración oficial para Monografías EIP-FINOR-UAGRM y APA 7.ª edición**  
*Basado en la metodología de 'vicentealvarezasencio/humanamente' adaptada al rigor científico de postgrado.*

---

## 1. Fundamentación y Propósito

La mayoría de los sistemas detectores y humanizadores automáticos fueron diseñados para la sintaxis del idioma inglés. Al aplicarse sobre textos académicos en castellano, introducen traducciones literales forzadas, rompen la concordancia gramatical o corrompen las citas bibliográficas APA 7ma edición.

El **Protocolo Humanamente** incorporado en **Max Academic Bolivia** opera de forma nativa sobre el español académico:
1. **Identifica y elimina los tics estructurales característicos de los Modelos de Lenguaje (LLMs)** sin empobrecer el registro científico.
2. **Protege al 100 % las citas bibliográficas:** Las citas parentéticas `(García, 2024)`, narrativas `Soto et al. (2025)` y URLs institucionales permanecen inmutables.
3. **Mantiene la tercera persona impersonal:** No incurre en la primera persona informal ni en coloquialismos inapropiados para una monografía de postgrado EIP-UAGRM.
4. **Preserva constructos técnicos y siglas bolivianas:** Términos como *«administración de bases de datos»*, *«Decreto Supremo N°...»*, *«AGETIC»*, *«ASFI»*, *«BCB»* e *«INE»* se conservan estrictamente.

---

## 2. Los 6 Tics de IA Detectados y sus Correcciones

### 2.1. Falso Paralelismo Negativo (`HUM-1`)
* **El tic de IA:** Abuso sistemático de la estructura pendular *«no solo [X], sino también [Y]»* o *«no solo... sino que además...»*.
* **Por qué es un tic:** Los LLMs lo usan compulsivamente para inflar artificialmente párrafos y fingir profundidad analítica.
* **Corrección académica:** Coordinación directa con nexos simples (*«y»*, *«además»*, *«asimismo»*) o división en oraciones correlativas independientes.
  * *IA:* «La seguridad de redes no solo protege contra intrusiones externas, sino que también salvaguarda la integridad de las transacciones internas.»
  * *Humanamente:* «La seguridad de redes previene intrusiones externas y salvaguarda la integridad de las transacciones internas.»

### 2.2. Gerundio de Consecuencia o Posterioridad (`HUM-2`)
* **El tic de IA:** Uso del gerundio para indicar consecuencia: *«, logrando así...»*, *«, permitiendo de este modo...»*, *«, garantizando con ello...»*, *«, propiciando así...»*.
* **Por qué es un tic:** En la norma gramatical de la Real Academia Española (RAE), el gerundio solo debe expresar simultaneidad o anterioridad. Usarlo como consecuencia es un calco del inglés (*", thus achieving..."*).
* **Corrección académica:** Emplear una oración coordinada con pronombre relativo o punto y seguido.
  * *IA:* «Se implementó el cifrado en reposo, garantizando así la confidencialidad de las tablas críticas.»
  * *Humanamente:* «Se implementó el cifrado en reposo, lo cual garantiza la confidencialidad de las tablas críticas.» (O: «...en reposo. Esta medida asegura la confidencialidad...»).

### 2.3. Rayas y Guiones Largos Anglosajones (`HUM-3` / `VAL-ERR`)
* **El tic de IA:** Intercalar incisos con rayas largas (`—`) o semirrayas (`–`).
* **Por qué es un tic:** Calco del *em-dash* anglosajón. En la prosa académica en español, el abuso de rayas fragmenta la lectura y denota texto sintético sin pulir.
* **Corrección académica:** Utilizar comas (`,`), paréntesis subordinados `(...)` o reformular sintácticamente.

### 2.4. Aperturas Cliché y Muletillas de Relleno (`HUM-4`)
* **El tic de IA:** Fórmulas introductorias grandilocuentes que no aportan contenido factual:
  * *«En el panorama actual de...»*
  * *«En un mundo en constante cambio / evolución...»*
  * *«En la era digital / en la sociedad del conocimiento...»*
  * *«Es crucial destacar que...»* / *«Es menester señalar que...»*
  * *«Cabe destacar que...»* / *«Cabe resaltar que...»*
  * *«Resulta imprescindible subrayar que...»*
* **Corrección académica:** Suprimir el relleno y entrar de forma directa al sujeto o al dato empírico contrastado.

### 2.5. Clichés Metafóricos y Adjetivos Inflados (`HUM-5` y `HUM-6`)
* **Metáforas trilladas de IA:** *«la piedra angular»*, *«un tapiz de»*, *«un testimonio de»*, *«el faro de»*, *«un sinfín de»*, *«desentrañar la complejidad»*, *«navegar el complejo panorama»*, *«juega un papel fundamental»*.
* **Adjetivos hiperbólicos de IA:** *revolucionario, transformador, paradigmático, holístico, fascinante, multifacético, disruptivo, vertiginoso*.
* **Corrección académica:** Usar lenguaje técnico sobrio:
  * *«juega un papel fundamental»* ➔ *«influye de manera directa»* / *«determina sustantivamente»*.
  * *«la piedra angular»* ➔ *«el fundamento metodológico principal»*.
  * *«un sinfín de»* ➔ *«múltiples»* / *«diversos»*.
  * *«enfoque holístico»* ➔ *«análisis integral»*.

### 2.6. La Regla de Tres Compulsiva
* **El tic de IA:** Agrupar ideas siempre en tríadas de adjetivos o sustantivos (*«seguro, eficiente y escalable»*, *«riguroso, exhaustivo y confiable»*).
* **Corrección académica:** Mantener únicamente el término que posea significado técnico preciso en el contexto de estudio.

---

## 3. Rúbrica de Autoevaluación en 6 Dimensiones

Al redactar o auditar cada párrafo, el modelo y el postgraduante evalúan el texto bajo esta escala:

| Dimensión | Criterio de Verificación | Pregunta de Control |
|---|---|---|
| **1. Claridad** | Prosa directa, sin rodeos ni dobles subordinadas innecesarias. | ¿Se puede decir lo mismo con menos palabras sin perder rigor? |
| **2. Ritmo (*Burstiness*)** | Alternancia orgánica entre oraciones cortas y compuestas. | ¿Suena monótono o artificial al leerlo en voz alta? |
| **3. Impersonalidad EIP** | Tercera persona académica rigurosa (*«se analizó»*). | ¿Se deslizó algún *«nosotros»*, *«nuestro estudio»* o *«vemos»*? |
| **4. Integridad de Citas** | Citas APA 7 exactas, intactas y contextualizadas. | ¿Están todos los autores y años en su formato normativo? |
| **5. Anclaje Territorial** | Datos contrastados con la realidad boliviana (2021–2026). | ¿El párrafo se refiere explícitamente a Bolivia o sus instituciones? |
| **6. Cero Fluff** | Ausencia total de metáforas de IA y muletillas de relleno. | ¿Hay algún *«en el panorama actual»* o *«juega un rol crucial»*? |

---

## 4. Comandos y Uso de las Herramientas

### Auditoría Rápida de un Borrador con Humanamente
```bash
python scripts/humanizar_texto.py output/monografia_completa.md
```
* Emite el **Puntaje de Prosa Humana (0 a 100)** y lista los números de línea exactos de cada tic detectado.

### Ver Propuesta de Sustituciones Sugeridas
```bash
python scripts/humanizar_texto.py output/monografia_completa.md --sugerir
```

### Auditoría Institucional Completa
El script maestro ejecuta los controles de Humanamente automáticamente:
```bash
python scripts/auditar_monografia.py output/monografia_completa.md
```
