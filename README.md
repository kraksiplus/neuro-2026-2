# Neurociencias UBB 2026-2 · Certamen 1

Ocho guías temáticas y un manual integrado de Neurociencias Aplicadas a la Medicina, en HTML
autocontenido: cada página funciona sin internet, guarda el tema claro u oscuro y se imprime o
exporta a PDF desde el navegador.

Publicado en https://kraksiplus.github.io/neuro-2026-2/

## Contenido

| # | Guía |
|---|---|
| 01 | La neurona y la glía |
| 02 | Nace: neurodesarrollo temprano |
| 03 | Se construye: proliferación, migración y corteza |
| 04 | Emite señal: membrana y potencial de acción |
| 05 | Se comunica y aprende: sinapsis y neurotransmisores |
| 06 | Madura y se renueva: plasticidad y neurogénesis adulta |
| 07 | Falla: demencias, neurodegeneración y priones |
| 08 | Cajal y la doctrina neuronal |
| M | Manual del Certamen 1 |

## Registro de escritura

Cada sección desarrolla una idea en prosa continua y cada afirmación clínica lleva la fuente al
lado: `[Purves p. 78]`, `[Zeise p. 108]`, `[apuntes, bloque III]`, `[Kelly §7]`. Las tablas se
reservan para comparaciones de tres o más ítems. Las dudas del OCR se concentran en la sección
**Límites del material**, no en el cuerpo.

La hoja de estilo completa está en `_build/ESTILO.md`.

## Fuentes

- Purves, *Neurociencia*, edición en español: caps. 3, 4, 22 y 23.
- Zeise (ed.), *Neurociencia para la psicología y otras áreas*: caps. 2, 4 y 7.
- Apuntes de clase de Neurociencias Aplicadas a la Medicina (56 páginas).
- Gross, *Joseph Altman and adult neurogenesis*; Kelly et al., *Sci. Adv.* 2026.
- Viñetas clínicas de Kandel, *Principles of Neural Science*.

No se publican los PDF originales ni el OCR crudo.

## Estructura

```
index.html          Índice del certamen
01..08_*.html       Guías temáticas
manual.html         Manual integrado
creditos.html       Fuente y titularidad de cada figura
assets/fig/         Figuras
_build/             Plantilla, estilos, manifiesto, generador y QA
```

Para regenerar el HTML:

```bash
python3 _build/build.py
python3 _build/qa.py
```

El generador lee los capítulos Markdown desde `../Certamenes/C1/CAPITULOS/`, fuera de este
repositorio. El repositorio publicado contiene solo el HTML final y las figuras.
