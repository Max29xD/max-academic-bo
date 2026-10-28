# Evaluaciones (solo desarrollo)

Este directorio no forma parte de la skill instalable. Sirve para comparar la versión actual
contra la anterior con prompts reales.

```text
evals/
├── evals.json                 # prompts + aserciones
├── baseline/<eval>/           # copia de la skill anterior (corpus de comparación)
└── iteration-1/
    └── <eval>/
        ├── eval_metadata.json
        ├── with_skill/outputs/
        └── old_skill/outputs/
```

Para repetir una iteración:

1. Copia `iteration-1/` a `iteration-2/` sin los `outputs/`.
2. Ejecuta los prompts con un agente que lea `SKILL.md` (versión nueva y baseline).
3. Guarda los artefactos en `with_skill/outputs/` y `old_skill/outputs/`.
4. Genera `grading.json` por corrida y agrega el benchmark.
5. Abre el visor:

   ```bash
   python .agents/skills/skill-creator/eval-viewer/generate_review.py evals/iteration-2 \
     --skill-name monografia-compilacion-bolivia --static evals/iteration-2/review.html
   ```

No ejecutes `bunx skills add . --all` desde la raíz: instalaría también las skills de
`.agents/skills`.
