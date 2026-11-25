# Hoja de estilo — Guías de Neurociencias, Certamen 1

Este documento manda sobre el registro de escritura. Todas las guías se escriben igual.

## Qué se busca

Que la guía se lea como un capítulo de libro, no como una lista de apuntes. Una sección
desarrolla **una idea** con prosa continua; la tabla aparece solo cuando hay cosas paralelas
que comparar; cada afirmación clínica lleva su fuente al lado.

El material de origen (las guías de `ESTUDIO/`) es el borrador: allí está todo, pero punteado,
con marcas de auditoría y repartido entre archivos. Aquí se reescribe: se elige el hilo, se
ordenan los mecanismos en cadena causal y se elimina el aparato de marcas.

## Estructura obligatoria del archivo

```markdown
# <Título exacto de la guía>

## Lo esencial en 60 segundos

- Seis a ocho viñetas, máximo 25 palabras cada una. Es el único lugar con viñetas fuera de
  "Puntos de examen" y "Límites del material".

## <Primera sección>

Prosa.

## <Segunda sección>

Prosa, tablas, subtítulos `###` si hacen falta.

## Puntos de examen

- Ocho a catorce viñetas con el dato duro: cifras, nombres, secuencias, pares.

## Límites del material

- Dos a cinco viñetas, o un párrafo corto, con lo que el OCR no permite afirmar, lo que quedó
  fuera del escaneo y lo que el material no cubre.
```

Entre seis y diez secciones de contenido. Sin numerarlas: el sitio las numera.

## Reglas de prosa

1. **Una sección, una idea.** La primera oración la enuncia; el resto la desarrolla.
2. **Cadena causal, no enumeración.** "El estímulo despolariza la membrana, lo que abre los
   canales de sodio; la entrada de sodio despolariza aún más, y así el potencial se regenera."
   No: "Etapas: 1) despolarización, 2) apertura de canales, 3) entrada de sodio".
3. **Párrafos de tres a seis oraciones.** Sin viñetas dentro de la prosa. Si algo necesita
   lista, o es una comparación (va a tabla) o es material de "Puntos de examen".
4. **Sin primera persona, sin apelaciones al lector.** No "vimos", no "fíjate que", no
   "como ya sabes". Sí se admite "conviene distinguir" y "el punto es".
5. **Presente atemporal.** "La mielina acelera la conducción", no "la mielina aceleraba".
6. **Nada de jerga de auditoría.** Prohibidos `⟦...⟧`, ⚠️, 🖼️, 🔗, "reconstrucción mía",
   "verificar", "según el OCR" dentro del cuerpo. Lo dudoso se dice en una oración normal
   ("el nombre de la vía no se lee con claridad en el original") y se concentra en
   **Límites del material**.
7. **Sin em dash (—).** Usar coma, dos puntos o paréntesis.
8. **Sin emojis ni iconos.**
9. **Números:** decimales con coma y miles con punto (1,5 % · 86.000 millones · 147 pb).
   Negrita en la cifra cuando es dato de memoria.
10. **Negrita con cuentagotas:** términos que hay que memorizar y cifras. Dos por párrafo como
    máximo. El resto del énfasis se logra con la sintaxis.

## Tablas

Solo si hay **tres o más ítems paralelos** comparables (canales, tipos de célula, demencias,
fases, secuencias de resonancia). Primera columna = la entidad. Sin celdas vacías: si no
aplica, "No aplica". Debajo de cada tabla, una línea `Fuente: [cita].` cuando el dato no esté
ya citado en el texto.

No usar tablas para contar una historia ni para dos columnas de texto corrido.

## Citas

Van al final de la oración, antes del punto, y son obligatorias en toda afirmación clínica.
Vocabulario permitido, exacto:

| Fuente | Forma | Ejemplo |
|---|---|---|
| Purves | `[Purves p. N]` o `[Purves pp. N-M]` | `[Purves p. 78]` |
| Zeise | `[Zeise p. N]` o `[Zeise §N.N]` | `[Zeise §2.5.4]` |
| Apuntes de clase | `[apuntes, bloque X]` o `[apuntes p. N]` | `[apuntes, bloque III]` |
| Kelly (Sci. Adv.) | `[Kelly §N]` | `[Kelly §7]` |
| Gross (Altman) | `[Gross §N]` | `[Gross §8]` |
| Kandel | `[Kandel cap. N]` | `[Kandel cap. 9]` |

Una cita por oración como máximo; si la oración mezcla dos fuentes, se parte en dos. **No
repetir la misma cita en oraciones seguidas del mismo párrafo**: va una sola vez, al final del
tramo que cubre. Un párrafo bien citado lleva una o dos citas, no seis. Nunca citar una página
que no aparezca en el archivo fuente: si el dato viene sin página, se cita la sección o el
bloque.

Después de escribir, si detectas más de una cita cada 35 palabras, reduce: deja la cita al
cierre de cada tramo de argumento. El script `_build/compact_cites.py` hace esa poda por
párrafo, pero es mejor escribir ya dosificado.

## Prohibiciones de contenido

- **No inventar.** Si un dato no está en las fuentes, no se escribe. No se completa con
  conocimiento general, ni con fisiología de otros textos, ni con cifras "aproximadas".
- **No prometer cobertura.** No escribir "en esta guía veremos todos los tipos de…". Se dice
  qué cubre y qué no, sin adornos.
- **No traducir nombres propios** ni cambiar siglas estándar (LTP, LTD, NMDA, AMPA, GABA,
  REM, PrP, ECJ, DTI).

## Modelo de párrafo (así se escribe)

> La mielina no genera el potencial de acción: lo hace eficiente. Los canales de sodio
> dependientes de voltaje se concentran en los nodos de Ranvier, de modo que la corriente
> fluye de forma pasiva por el segmento mielinizado y se regenera solo al llegar al nodo
> siguiente. El resultado es una propagación saltatoria, que gana velocidad y ahorra energía,
> porque la bomba de sodio y potasio trabaja menos veces para mantener el gradiente
> `[Purves p. 78]`.

## Modelo de lo que NO se escribe

> - **Mielina:** acelera.
>   - Canales de Na⁺ solo en nodos.
>   - Conducción saltatoria: salta.
> - 🖼️ Figura 3: la mielina en rojo.
> ⚠️ El OCR no dice la página exacta.

## Longitud

| Guía | Palabras objetivo |
|---|---|
| 01 Neurona y glía | 2.800 a 3.400 |
| 02 Nace | 4.600 a 5.400 |
| 03 Se construye | 4.600 a 5.400 |
| 04 Emite señal | 5.600 a 6.400 |
| 05 Se comunica | 5.600 a 6.400 |
| 06 Madura y se renueva | 5.600 a 6.400 |
| 07 Falla | 5.000 a 5.900 |
| 08 Cajal | 2.300 a 2.900 |
| Manual | 3.600 a 4.400 |

Si el material no alcanza para el rango, se escribe lo que hay y se declara en **Límites del
material**. Nunca se rellena.
