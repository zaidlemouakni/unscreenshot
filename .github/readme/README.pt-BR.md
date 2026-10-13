<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>Desfaça o print. Recupere o slide.</b><br>
Entra um print, sai um PowerPoint editável, pixel por pixel, em qualquer idioma.</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.fr.md" title="Français">🇫🇷</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
  <b title="Português (Brasil)">🇧🇷</b> ·
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

![A captura de um slide vira um PowerPoint editável: cada texto, cartão e cor medido e reconstruído](../../docs/demo.gif)

Você tem a imagem de um slide: um print de uma reunião, um slide que uma IA gerou como imagem, uma página de PDF, uma apresentação que alguém mandou em imagens. Você precisa do PowerPoint. Ele sumiu, ou nunca existiu.

`unscreenshot` é uma **skill para agentes**: você entrega a imagem ao seu assistente de IA e recebe um `.pptx` em que cada caixa de texto, marcador, cartão, linha e cor é medido na imagem e reconstruído como um objeto nativo e editável do PowerPoint.

## Instalação em 30 segundos

Cole isto em qualquer agente que instale skills (Claude Code, Codex, Gemini CLI, Cursor, Copilot…):

```text
Instale a skill unscreenshot de https://github.com/zaidlemouakni/unscreenshot seguindo o AGENTS.md do repositório.
```

Ou escolha sua plataforma:

| Onde você usa IA | Como |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities: ative a execução de código e depois Skills > envie [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > envie o mesmo zip |
| **Gemini** (app) | Skills > envie o mesmo zip |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > o zip |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` e depois `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` e depois `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | copie `skills/unscreenshot` para `~/.vibe/skills/` |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

Menus, pastas e cada plataforma passo a passo: [INSTALL](../install/INSTALL.pt-BR.md) (os menus aparecem em inglês).

## Teste em 60 segundos

1. Instale a skill na sua plataforma (acima).
2. Salve [a captura de exemplo](../../examples/demo/source.png) ou use qualquer imagem de um slide.
3. Anexe a imagem e peça, no seu idioma:
   > Refaça este slide em PowerPoint editável, idêntico.
4. Abra o `.pptx` e clique no título: é uma caixa de texto de verdade, não uma imagem.

Você também recebe uma imagem de antes/depois para comparar. Várias imagens, ou um PDF com várias páginas, viram um slide cada no mesmo arquivo.

## Funciona no seu idioma

![Doze escritas em um único slide, reconstruídas](../../docs/languages-before-after.png)

Árabe, persa e hebraico (da direita para a esquerda), chinês, japonês, coreano, hindi, tailandês, vietnamita, russo, grego e todos os idiomas escritos com letras latinas.

- O texto é mantido palavra por palavra, na sua própria escrita. Nada é traduzido.
- Slides da direita para a esquerda mantêm o layout espelhado: marcadores à direita, linhas do tempo apontando para a esquerda.
- Cada escrita recebe a fonte que o PowerPoint usa para ela, e o tamanho é medido do jeito que essa escrita é desenhada.

Exemplos completos: [árabe](../../examples/arabic) · [japonês](../../examples/japanese) · [doze escritas em um slide](../../examples/languages).

## O que você recebe

![Antes: um print. Depois: o mesmo slide como PowerPoint editável](../../docs/demo-before-after.png)

- **Objetos nativos e editáveis**: caixas de texto com o texto real, marcadores de verdade, retângulos, cartões arredondados, pílulas, círculos, chevrons, linhas e grupos. Troque uma palavra, mude a cor de um cartão, mova um bloco: é um slide normal.
- **Medido, não adivinhado**: posições, tamanhos e cores vêm de medições em pixels. O tamanho das fontes é calculado para que cada linha tenha a mesma largura da imagem.
- **Uma prova**: a imagem e o slide reconstruído lado a lado, e a sobreposição dos dois.

## Por que não um OCR, um conversor de PDF ou um gerador de slides com IA?

Um OCR entrega o texto, não o slide. Um conversor precisa do PDF original. Um gerador cria um slide novo. O unscreenshot devolve o slide que você tem.

| | OCR | Conversores de PDF | Geradores de slides com IA | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| Parte de uma captura ou de uma foto | ✅ | ❌ | ❌ | ✅ |
| Cada palavra mantida, sem mudança | ✅ | ✅ | ❌ | ✅ |
| Mesmo layout, posições e tamanhos | ❌ | ⚠️ | ❌ | ✅ |
| Formas nativas, cartões e marcadores de verdade | ❌ | ⚠️ | ✅ | ✅ |
| Direita para a esquerda e escritas não latinas | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ depende da ferramenta e do arquivo.

## Como funciona

O assistente (qualquer modelo que enxergue imagens) lê e decide. Pequenos scripts em Python, testados, medem e constroem.

1. **Análise**: encontrar cada linha de texto, forma preenchida, fio, marcador e ícone; medir linhas de base, larguras de tinta e cores.
2. **Leitura**: o modelo transcreve cada linha a partir de recortes ampliados e decide o que é cada elemento.
3. **Spec**: o modelo escreve uma descrição JSON do slide apoiada nas medições.
4. **Ajuste**: o tamanho das fontes é calculado para que a largura de tinta de cada texto bata com a imagem, escrita por escrita.
5. **Construção**: um gerador sem dependências produz o `.pptx` (só Pillow e numpy).
6. **Verificação**: o slide é renderizado (LibreOffice ou PowerPoint), comparado com a imagem e corrigido, no máximo três rodadas.

Nos quatro exemplos deste repositório, cada texto fica a menos de 1 px do original após uma correção.

## Limites

- **Fontes**: se a imagem usa uma fonte que não é do Office (Poppins, Inter, Noto…), usa-se a fonte do Office mais parecida. Posições, tamanhos e larguras continuam iguais; o desenho das letras muda um pouco.
- **Ícones, logos e fotos** são recortados da imagem (com fundo transparente), não redesenhados.
- **Texto vertical em japonês ou chinês** fica como imagem.
- Seu assistente precisa conseguir **executar Python** (execução de código). Sem isso, será preciso o servidor MCP previsto para a v2.

## Perguntas frequentes

**É grátis?**\
Sim: licença MIT, sem conta e sem chave de API. Roda dentro do assistente que você já usa.

**Meu slide sai do meu computador?**\
A skill não faz nenhuma chamada de rede: os scripts rodam no ambiente isolado do seu assistente ou na sua máquina. O assistente vê a imagem, como qualquer arquivo que você compartilha com ele.

**Com quais assistentes funciona?**\
Com qualquer assistente que veja imagens e execute Python: os da tabela de instalação e outros que leiam o formato `SKILL.md`. A leitura de textos pequenos depende da visão do modelo: um modelo mais forte lê melhor.

**E se algum detalhe ficar errado?**\
A skill renderiza o resultado, compara com a sua imagem e corrige, no máximo três rodadas. Depois diz o que ainda está diferente. Tudo é editável, então o último ajuste leva segundos.

**Por que não colar a imagem no PowerPoint e pronto?**\
Aí ela é só uma imagem: não dá para mudar uma palavra, corrigir um número nem reaproveitar um cartão.

**Ela melhora ou traduz o slide?**\
Não por conta própria, de propósito: ela reconstrói o que a imagem mostra, palavra por palavra, erros de digitação incluídos. Com o PowerPoint de verdade em mãos, peça ao seu assistente as mudanças que quiser.

Código, testes e exemplos: veja a [tabela do repositório](../../README.md#repository) no README em inglês. Correções de tradução são bem-vindas: [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Licença

MIT.

*Dê uma estrela se isso te poupou de refazer um slide na mão.*
