<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>Deshaz la captura. Recupera la diapositiva.</b><br>
Entra una captura, sale un PowerPoint editable, píxel a píxel, en cualquier idioma.</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.fr.md" title="Français">🇫🇷</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <b title="Español">🇪🇸</b> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a> ·
  <a href="README.vi.md" title="Tiếng Việt">🇻🇳</a> ·
  <a href="README.ko.md" title="한국어">🇰🇷</a> ·
  <a href="README.fa.md" title="فارسی">🇮🇷</a> ·
  <a href="README.th.md" title="ไทย">🇹🇭</a> ·
  <a href="README.ar.md" title="العربية">🇸🇦</a>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <a href="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml"><img src="https://github.com/zaidlemouakni/unscreenshot/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
  <img src="https://img.shields.io/badge/works%20with-Claude%20%C2%B7%20ChatGPT%20%C2%B7%20Gemini%20%C2%B7%20Copilot%20%C2%B7%20Codex%20%C2%B7%20Cursor-1B2340.svg" alt="Claude · ChatGPT · Gemini · Copilot · Codex · Cursor">
</p>

![La captura de una diapositiva se convierte en un PowerPoint editable: cada texto, tarjeta y color medido y reconstruido](../../docs/demo.gif)

Tienes la imagen de una diapositiva: una captura de una reunión, una diapositiva que una IA generó como imagen, una página de un PDF, una presentación que te enviaron como imágenes. Necesitas el PowerPoint. Se perdió, o nunca existió.

`unscreenshot` es una **skill para agentes**: le das la imagen a tu asistente de IA y te devuelve un `.pptx` en el que cada cuadro de texto, viñeta, tarjeta, línea y color se mide en la imagen y se reconstruye como un objeto nativo y editable de PowerPoint.

## Instalación en 30 segundos

Pega esto en cualquier agente que pueda instalar skills (Claude Code, Codex, Gemini CLI, Cursor, Copilot…):

```text
Instala la skill unscreenshot desde https://github.com/zaidlemouakni/unscreenshot siguiendo el AGENTS.md del repositorio.
```

O elige tu plataforma:

| Dónde usas la IA | Cómo |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities: activa la ejecución de código y luego Skills > sube [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > sube el mismo zip |
| **Gemini** (app) | Skills > sube el mismo zip |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > el zip |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` y luego `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` y luego `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | copia `skills/unscreenshot` en `~/.vibe/skills/` |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

Menús, carpetas y cada plataforma paso a paso: [INSTALL](../install/INSTALL.es.md) (los menús se indican en inglés).

## Pruébalo en 60 segundos

1. Instala la skill para tu plataforma (arriba).
2. Guarda [la captura de ejemplo](../../examples/demo/source.png) o usa cualquier imagen de una diapositiva.
3. Adjúntala y pide, en tu idioma:
   > Rehaz esta diapositiva como un PowerPoint editable, idéntica.
4. Abre el `.pptx` y haz clic en el título: es un cuadro de texto real, no una imagen.

También recibes una imagen de antes/después para comparar. Varias imágenes, o un PDF de varias páginas, dan una diapositiva cada una en el mismo archivo.

## Funciona en tu idioma

![Doce escrituras en una sola diapositiva, reconstruidas](../../docs/languages-before-after.png)

Árabe, persa y hebreo (de derecha a izquierda), chino, japonés, coreano, hindi, tailandés, vietnamita, ruso, griego y todos los idiomas que usan el alfabeto latino.

- El texto se conserva palabra por palabra, en su propia escritura. No se traduce nada.
- Las diapositivas de derecha a izquierda conservan su diseño en espejo: viñetas a la derecha y hojas de ruta que apuntan a la izquierda.
- Cada escritura recibe la fuente que PowerPoint usa para ella, y su tamaño se mide según cómo se dibuja esa escritura.

Ejemplos completos: [árabe](../../examples/arabic) · [japonés](../../examples/japanese) · [doce escrituras en una diapositiva](../../examples/languages).

## Lo que obtienes

![Antes: una captura. Después: la misma diapositiva como PowerPoint editable](../../docs/demo-before-after.png)

- **Objetos nativos y editables**: cuadros de texto con el texto real, viñetas reales, rectángulos, tarjetas redondeadas, píldoras, círculos, chevrones, líneas y grupos. Cambia una palabra, el color de una tarjeta o mueve un bloque: es una diapositiva normal.
- **Medido, no adivinado**: posiciones, tamaños y colores salen de mediciones en píxeles. El tamaño de las fuentes se calcula para que cada línea tenga el mismo ancho que en la imagen.
- **Una prueba**: la imagen y la diapositiva reconstruida lado a lado, y su superposición.

## ¿Por qué no un OCR, un conversor de PDF o un generador de diapositivas con IA?

Un OCR te da el texto, no la diapositiva. Un conversor necesita el PDF original. Un generador crea una diapositiva nueva. unscreenshot te devuelve la diapositiva que tienes.

| | OCR | Conversores de PDF | Generadores de diapositivas con IA | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| Parte de una captura o una foto | ✅ | ❌ | ❌ | ✅ |
| Cada palabra se conserva, tal cual | ✅ | ✅ | ❌ | ✅ |
| Mismo diseño, posiciones y tamaños | ❌ | ⚠️ | ❌ | ✅ |
| Formas nativas, tarjetas y viñetas reales | ❌ | ⚠️ | ✅ | ✅ |
| Derecha a izquierda y escrituras no latinas | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ depende de la herramienta y del archivo.

## Cómo funciona

El asistente (cualquier modelo que vea imágenes) lee y decide. Pequeños scripts de Python, probados, miden y construyen.

1. **Análisis**: encontrar cada línea de texto, forma rellena, filete, viñeta e icono; medir líneas base, anchos de tinta y colores.
2. **Lectura**: el modelo transcribe cada línea a partir de recortes ampliados y decide qué es cada elemento.
3. **Spec**: el modelo escribe una descripción JSON de la diapositiva que se apoya en las mediciones.
4. **Ajuste**: el tamaño de las fuentes se calcula para que el ancho de tinta de cada texto coincida con la imagen, escritura por escritura.
5. **Construcción**: un generador sin dependencias produce el `.pptx` (solo Pillow y numpy).
6. **Verificación**: la diapositiva se renderiza (LibreOffice o PowerPoint), se compara con la imagen y se corrige, tres rondas como máximo.

En los cuatro ejemplos de este repositorio, cada texto queda a menos de 1 px del original tras una corrección.

## Límites

- **Fuentes**: si la imagen usa una fuente que no es de Office (Poppins, Inter, Noto…), se usa la fuente de Office más parecida. Posiciones, tamaños y anchos de línea coinciden; la forma de las letras cambia un poco.
- **Iconos, logotipos y fotos** se recortan de la imagen (con fondo transparente), no se redibujan.
- **El texto vertical en japonés o chino** se conserva como imagen.
- Tu asistente debe poder **ejecutar Python** (ejecución de código). Si no puede, hará falta el servidor MCP previsto para la v2.

## Preguntas frecuentes

**¿Es gratis?**\
Sí: licencia MIT, sin cuenta ni clave de API. Funciona dentro del asistente que ya usas.

**¿Mi diapositiva sale de mi equipo?**\
La skill no hace ninguna llamada de red: sus scripts se ejecutan en el entorno aislado de tu asistente o en tu equipo. Tu asistente ve la imagen, como cualquier archivo que compartas con él.

**¿Con qué asistentes funciona?**\
Con cualquier asistente que vea imágenes y ejecute Python: los de la tabla de instalación y otros que lean el formato `SKILL.md`. La lectura del texto pequeño depende de la visión del modelo: un modelo más potente lee mejor.

**¿Y si algún detalle no cuadra?**\
La skill renderiza su resultado, lo compara con tu imagen y lo corrige, tres rondas como máximo. Después te dice qué sigue siendo distinto. Todo es editable, así que el último retoque lleva segundos.

**¿Por qué no pegar la imagen en PowerPoint sin más?**\
Sería una imagen: no podrías cambiar una palabra, corregir una cifra ni reutilizar una tarjeta.

**¿Puede mejorar o traducir la diapositiva?**\
No por su cuenta, a propósito: reconstruye lo que muestra la imagen, palabra por palabra, erratas incluidas. Cuando tengas el PowerPoint real, pide a tu asistente los cambios que quieras.

Código, pruebas y ejemplos: consulta la [tabla del repositorio](../../README.md#repository) del README en inglés. Las correcciones de traducción son bienvenidas: [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Licencia

MIT.

*Dale una estrella si te ahorró rehacer una diapositiva a mano.*
