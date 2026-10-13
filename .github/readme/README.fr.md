<p align="center"><img src="../../docs/logo.png" width="120" alt=""></p>

<h1 align="center">unscreenshot</h1>

<p align="center"><b>Annule la capture d'écran. Récupère ta slide.</b><br>
Une capture en entrée, un PowerPoint modifiable en sortie. Au pixel près, dans toutes les langues.</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <b title="Français">🇫🇷</b> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href="README.es.md" title="Español">🇪🇸</a> ·
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

![Une capture de slide devient un PowerPoint modifiable : chaque texte, carte et couleur mesuré puis reconstruit](../../docs/demo.gif)

Tu as l'image d'une slide : une capture prise en réunion, une slide qu'une IA a générée sous forme d'image, une page de PDF, un deck reçu en images. Il te faut le PowerPoint. Il a disparu, ou il n'a jamais existé.

`unscreenshot` est une **skill d'agent** : tu donnes l'image à ton assistant IA, il te rend un `.pptx` où chaque zone de texte, puce, carte, ligne et couleur est mesurée sur l'image puis reconstruite en objet PowerPoint natif et modifiable.

## Installation en 30 secondes

Colle ceci dans n'importe quel agent capable d'installer des skills (Claude Code, Codex, Gemini CLI, Cursor, Copilot…) :

```text
Installe la skill unscreenshot depuis https://github.com/zaidlemouakni/unscreenshot en suivant le fichier AGENTS.md du dépôt.
```

Ou choisis ta plateforme :

| Où tu utilises l'IA | Comment |
|---|---|
| **Claude** (claude.ai) | Settings > Capabilities : active l'exécution de code, puis Skills > importe [`unscreenshot.zip`](https://github.com/zaidlemouakni/unscreenshot/releases/latest) |
| **ChatGPT** (Business, Enterprise, Edu) | Skills > importe le même zip |
| **Gemini** (app) | Skills > importe le même zip |
| **Microsoft Copilot Studio** | Agent > Build > Skills > Upload a skill > le zip |
| **Claude Code** | `claude plugin marketplace add zaidlemouakni/unscreenshot` puis `claude plugin install unscreenshot@unscreenshot` |
| **Codex** | `codex plugin marketplace add zaidlemouakni/unscreenshot --ref main` puis `codex plugin add unscreenshot@unscreenshot` |
| **Gemini CLI** | `gemini extensions install https://github.com/zaidlemouakni/unscreenshot` |
| **Mistral Vibe** | copie `skills/unscreenshot` dans `~/.vibe/skills/` |
| **GitHub Copilot, Cursor, OpenCode…** | `npx skills add zaidlemouakni/unscreenshot` |

Menus, dossiers et chaque plateforme pas à pas : [INSTALL](../install/INSTALL.fr.md) (les menus sont indiqués en anglais).

## Essaie en 60 secondes

1. Installe la skill pour ta plateforme (ci-dessus).
2. Enregistre [la capture d'exemple](../../examples/demo/source.png), ou prends n'importe quelle image de slide.
3. Joins-la et demande, dans ta langue :
   > Refais cette slide à l'identique en PowerPoint modifiable.
4. Ouvre le `.pptx` et clique sur le titre : c'est une vraie zone de texte, pas une image.

Tu reçois aussi une image avant/après pour comparer. Plusieurs images, ou un PDF de plusieurs pages, donnent une slide chacune dans le même fichier.

## Fonctionne dans ta langue

![Douze écritures sur une seule slide, reconstruites](../../docs/languages-before-after.png)

Arabe, persan et hébreu (de droite à gauche), chinois, japonais, coréen, hindi, thaï, vietnamien, russe, grec et toutes les langues en alphabet latin.

- Le texte est repris mot pour mot, dans son écriture. Rien n'est traduit.
- Les slides de droite à gauche gardent leur mise en page en miroir : puces à droite, feuilles de route orientées vers la gauche.
- Chaque écriture reçoit la police que PowerPoint utilise pour elle, et sa taille est mesurée selon la façon dont elle est dessinée.

Exemples complets : [arabe](../../examples/arabic) · [japonais](../../examples/japanese) · [douze écritures sur une slide](../../examples/languages).

## Ce que tu obtiens

![Avant : une capture. Après : la même slide en PowerPoint modifiable](../../docs/demo-before-after.png)

- **Des objets natifs et modifiables** : zones de texte avec le vrai texte, vraies puces, rectangles, cartes arrondies, pastilles, cercles, chevrons, lignes, groupes. Change un mot, recolore une carte, déplace un bloc : c'est une slide normale.
- **Mesuré, pas deviné** : positions, tailles et couleurs viennent de mesures au pixel. La taille des polices est calculée pour que chaque ligne ait la même largeur que sur l'image.
- **Une preuve** : l'image et la slide reconstruite côte à côte, et leur superposition.

## Pourquoi pas un OCR, un convertisseur PDF ou un générateur de slides IA ?

Un OCR te donne le texte, pas la slide. Un convertisseur a besoin du PDF d'origine. Un générateur fait une nouvelle slide. unscreenshot te rend la slide que tu as.

| | OCR | Convertisseurs PDF | Générateurs de slides IA | **unscreenshot** |
|---|:-:|:-:|:-:|:-:|
| Part d'une capture ou d'une photo | ✅ | ❌ | ❌ | ✅ |
| Chaque mot conservé, à l'identique | ✅ | ✅ | ❌ | ✅ |
| Même mise en page, positions et tailles | ❌ | ⚠️ | ❌ | ✅ |
| Formes natives, cartes et vraies puces | ❌ | ⚠️ | ✅ | ✅ |
| Droite à gauche et écritures non latines | ⚠️ | ⚠️ | ⚠️ | ✅ |

⚠️ dépend de l'outil et du fichier.

## Comment ça marche

L'assistant (n'importe quel modèle qui voit les images) ne fait que lire le texte. De petits scripts Python testés font tout le reste : le résultat est le même avec un petit modèle ou un grand.

1. **Analyse** : repérer chaque ligne de texte, forme pleine, filet, puce et icône ; mesurer lignes de base, largeurs d'encre et couleurs.
2. **Lecture** : le modèle tape chaque ligne de texte à partir d'agrandissements ; les scripts signalent toute ligne dont la lecture ne correspond pas à l'image.
3. **Spec** : les scripts écrivent la description de la slide à partir des mesures : formes, chevrons, puces, polices, tailles, alignement.
4. **Ajustement** : la taille des polices est calculée pour que la largeur d'encre de chaque texte corresponde à l'image, écriture par écriture.
5. **Construction** : un générateur sans dépendance produit le `.pptx` (uniquement Pillow et numpy).
6. **Vérification** : la slide est rendue (LibreOffice ou PowerPoint), comparée à l'image et corrigée, trois passes au maximum.

Sur les quatre exemples du dépôt, chaque texte tombe à 1 px près de l'original après une correction.

## Limites

- **Polices** : si l'image utilise une police absente d'Office (Poppins, Inter, Noto…), la plus proche est utilisée. Positions, tailles et largeurs restent justes ; le dessin des lettres diffère légèrement.
- **Icônes, logos, photos** : recadrés depuis l'image (fond rendu transparent), pas redessinés.
- **Le texte vertical japonais ou chinois** est conservé en image.
- L'assistant doit pouvoir **exécuter du Python** (exécution de code). Sinon, il faudra le serveur MCP prévu en v2.

## Questions fréquentes

**C'est gratuit ?**\
Oui : sous licence MIT, sans compte ni clé d'API. Ça tourne dans l'assistant que tu utilises déjà.

**Ma slide quitte-t-elle mon ordinateur ?**\
La skill ne fait aucun appel réseau : ses scripts tournent dans le bac à sable de ton assistant ou sur ta machine. Ton assistant voit l'image, comme tout fichier que tu lui confies.

**Avec quels assistants ça marche ?**\
Tout assistant qui voit les images et exécute du Python : ceux du tableau d'installation, et les autres qui lisent le format `SKILL.md`. La lecture des petits textes dépend de la vision du modèle : un modèle plus puissant lit mieux.

**Et si un détail cloche ?**\
La skill fait le rendu de son résultat, le compare à ton image et le corrige, trois passes au maximum. Puis elle te dit ce qui diffère encore. Tout est modifiable : la dernière retouche prend quelques secondes.

**Pourquoi ne pas simplement coller l'image dans PowerPoint ?**\
Ce serait une image : impossible de changer un mot, de corriger un chiffre ou de réutiliser une carte.

**Peut-elle améliorer ou traduire la slide ?**\
Pas d'elle-même, et c'est voulu : elle reconstruit ce que montre l'image, mot pour mot, coquilles comprises. Une fois le vrai PowerPoint en main, demande à ton assistant les changements que tu veux.

Code, tests et exemples : voir le [tableau du dépôt](../../README.md#repository) du README en anglais. Les corrections de traduction sont bienvenues : [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Licence

MIT.

*Mets une étoile si ça t'a évité de refaire une slide à la main.*
