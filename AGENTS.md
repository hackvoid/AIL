# AGENTS.md

## Project overview

This is **not a traditional software project** — it is a content repository for the
**Kineton Academy** bootcamp (automotive E/E engineering training), plus a small set of
utility scripts that process and publish that content.

The core deliverable is a static documentation site called the **Kineton Academy Wiki**,
built with [MkDocs](https://www.mkdocs.org/) + the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, and generated
by a Python script from the source content trees.

There is no git repository, no test suite, and no CI.

### Content

The training material is organized into four modules, one directory each:

| Directory | Theme | Topic subdirectories |
|---|---|---|
| `MIL1/` | Vehicle Fundamentals | `CAN_LIN`, `EE_Architecture`, `Electric_Motors`, `HEV_Architecture_BEV`, `HEV_Architecture_Hybrid`, `ICE`, `Sensors`, `V_Cycle`, `Vehicle_Subsystems` |
| `MIL2/` | Tools & Testing Basics | `12_CANalyzer`, `14_CAPL`, `16_CANoe`, `17_Diagnosis`, `18_RDI_Testing`, `19_Diagnostic_Tools`, `40_TestAutomation` |
| `MIL3/` | Requirements, HIL & Calibration | `21_Requirements`, `23_VF`, `24_TestCases`, `25_HIL_Users`, `26_INCA`, `27_INCA_2` |
| `MIL4/` | Verification & Validation | `28_Verification`, `31_Validation`, `32_Diagnosis_Process`, `34_Troubleshooting`, `35_First_Level_Analysis` |

Content files are mostly PDF slide decks (~87), MP3 lecture recordings (~26), Whisper
transcripts of those recordings (`.txt`/`.srt`/`.vtt`/`.tsv`/`.json`), and automotive
engineering attachments (`.dbc` CAN databases, `.cdd` diagnostic descriptions, `.zip`,
`.png`, `.html`). Numbers in directory names (e.g. `12_CANalyzer`) are the course
lesson numbering; the wiki generator strips them from displayed titles.

Notable special files:

- `MIL1/cards_export.json` — glossary term cards (name, acronym, description, bullets)
  grouped by `tab` topic; consumed by the wiki generator to build the Glossary section.
- `MIL1/VideoLinks.txt`, `MIL2/MIL2_Links.txt` — curated YouTube links, format
  `Name - URL` per line; used to build the wiki Resources page.
- `MIL1/vv_cheat_sheet.html` — V&V cheat sheet, linked from the Resources page.
- `Files/` — a **flat derived copy** of everything under `MIL1`–`MIL4`, produced by
  `consolidate.py` (name collisions get `_1`, `_2`, … suffixes). Do not edit files here;
  edit the originals in `MIL*`. Note the wiki's glossary/resources builders read from
  `Files/`, so `consolidate.py` must be re-run after those specific source files change.
- `heirarchy.txt` *(sic, filename has a typo)* — mapping log written by `consolidate.py`:
  `Original Path -> Copied Filename`.
- `server_agent_prompt.txt` — the prompt that was used to have an agent set up GPU
  transcription on a server (historical context for `transcribe_audio.sh`).

## Code and tooling

All code lives at the project root and in `wiki/`:

- `wiki/extract_decks.py` — deck extraction pipeline. Reads every PDF under
  `MIL1`–`MIL4`, pulls per-slide text (title via largest-font heuristic, body text
  with boilerplate stripped) with pypdf, renders each page to a WebP image with
  pypdfium2 (poppler `pdftoppm` fallback), and caches results under
  `wiki/.cache/decks/`. Cache key is the file's sha1, so identical PDF copies are
  extracted once. Rendered slide images go to `wiki/.cache/img/<mod>/<slug>-<hash>/`
  and serve as **authoring material** (text source for articles, crop source for
  figures) — they are not copied into the site.
- `wiki/articles/` — **the real wiki content, hand/agent-authored Markdown**, one
  `index.md` per MIL directory, mirroring the source tree with slugified names
  (e.g. `wiki/articles/mil1/can-lin/index.md` ↔ `MIL1/CAN_LIN/`). Articles rewrite
  the slide decks as prose with Mermaid diagrams and cropped figures in local
  `img/` dirs; they never paste slide text verbatim. `wiki/articles/mil1/can-lin/`
  is the style exemplar.
- `wiki/build_wiki.py` — the assembler. Copies `wiki/articles/` into `wiki/docs/`
  (plus each article's `img/` assets), appends auto-generated **Source material**
  (PDF links) and **Downloads** (dbc/cdd/transcripts/etc.) sections to every page,
  generates module curriculum pages, the home page (`build_home()`, the "Your orbit
  starts here" hero + module cards), glossary and resources pages, asset symlinks
  `wiki/docs/assets/mil<N> -> ../../MIL<N>`, copies the theme assets
  (`copy_theme_assets()`), and writes `wiki/mkdocs.yml` (including the full nav
  tree, the Mermaid superfences config, `custom_dir`, `extra_css` and
  `extra_javascript`). Directories without an article get a fallback
  references-only page. **Run from the project root.** `--manifest` writes
  `wiki/.cache/source_manifest.json`, the per-directory authoring aid (article
  path, deck cache JSONs, transcripts, image dirs).
- `wiki/theme/` — the **custom theme** (clean dark/light UI, single violet
  accent, flat surfaces, thin borders). All theme work happens here, never in
  `wiki/docs/` or `wiki/mkdocs.yml`:
  - `theme/overrides/main.html` — MkDocs Material template override (`custom_dir`).
    The `footer` block injects the assistant panel markup (single edge-handle
    toggle, message thread, composer); the `scripts` block defines the backend
    hook `window.KX_CHAT_CONFIG = { endpoint: null, model: null }`.
  - `theme/assets/kineton.css` — the whole visual layer. All `--kx-*` tokens are
    defined **per palette scheme** (`[data-md-color-scheme="default"]` for light,
    `"slate"` for dark); component rules reference only tokens, so both modes
    stay in sync. The light/dark toggle itself is MkDocs Material's built-in
    palette switcher (media-query default + header toggle), configured in
    `build_wiki.py`'s `MKDOCS_HEADER`.
  - `theme/assets/kineton-chat.js` — assistant panel behavior: the same handle
    button opens and closes the panel (state persisted in localStorage,
    `#assistant` URL hash opens it). Until `KX_CHAT_CONFIG.endpoint` is set,
    every message gets the static placeholder reply; once set, `askBackend()`
    POSTs `{message}` there and renders `{reply}`. **No backend is wired yet —
    frontend shell only.**
  - `theme/assets/mermaid.min.js` — vendored Mermaid v11 (offline-friendly, no
    CDN dependency).
  - `theme/assets/kineton-mermaid.js` — renders `pre.kx-mermaid` blocks with
    palette-matched colors (separate light/dark `themeVariables`, re-renders
    when the palette toggle flips). The superfences custom fence deliberately
    uses the class `kx-mermaid` (not `mermaid`) because Material's own bundle
    hijacks `.mermaid` elements and races any other renderer; the `kx-` prefix
    makes this script the only renderer. It captures diagram source
    synchronously (script loads at end of `<body>`, before Mermaid's auto-run)
    and re-renders with `themeVariables`.
- `consolidate.py` — copies all files from `MIL1`–`MIL4` into flat `Files/` and logs the
  mapping to `heirarchy.txt`. Overwrites both on each run.
- `AIL.ps1` (PowerShell, Windows-oriented) — converts all `.mp4`/`.mkv` under the tree
  to mono 64 kbps MP3 with ffmpeg, then **deletes the original videos**.
- `transcribe_audio.sh` (bash) — transcribes all `.mp3` files with OpenAI Whisper
  (`whisper --model base`, expects whisper at `~/.local/bin/whisper`), writes `.txt`,
  `.srt`, `.vtt`, `.tsv`, `.json` next to the audio, then **deletes the original MP3s**.
- `convert_to_pdf.sh` (bash) — converts all `.docx`/`.pptx`/`.xlsx` to PDF via
  LibreOffice headless, then **deletes the originals**.
- `wiki/mkdocs.yml` — **generated file**, do not hand-edit; `build_wiki.py` rewrites it.
- `wiki/site/` — **generated** static build output of `mkdocs build`.
- `wiki/.cache/decks/` — **generated** deck-extraction cache (JSON per unique PDF).
- `wiki/.cache/img/` — **generated** rendered slide images (WebP), authoring material
  for article figures.
- `wiki/.cache/source_manifest.json` — **generated** authoring manifest
  (`build_wiki.py --manifest`).
- `wiki-venv/` — local Python 3.13 virtualenv with mkdocs 1.6.1, mkdocs-material,
  pypdf, pypdfium2 and Pillow installed (plus `ghp-import`).

## Build and run commands

```bash
# Assemble wiki/docs from wiki/articles + MIL* trees and regenerate mkdocs.yml
# (stdlib + PyYAML; PyYAML comes from the venv)
wiki-venv/bin/python wiki/build_wiki.py

# Refresh the deck-extraction cache (only needed when source PDFs change)
wiki-venv/bin/python wiki/extract_decks.py

# Build the static site into wiki/site/
cd wiki && ../wiki-venv/bin/mkdocs build

# Serve locally for preview
cd wiki && ../wiki-venv/bin/mkdocs serve

# Rebuild the flat Files/ copy (after editing source content)
python3 consolidate.py
```

System dependencies for the media scripts (not needed for the wiki): `ffmpeg`,
`libreoffice`, `openai-whisper` (with CUDA-enabled PyTorch if GPU transcription is
wanted — see `server_agent_prompt.txt`). PDF extraction/rendering for the wiki needs
`pypdf`, `pypdfium2`, `Pillow` (venv) and poppler (`pdftoppm`, system).

## Conventions

- All documentation, comments, and content are in **English** (some source exercise
  filenames are in Italian, e.g. `Esercizio_diagnosi_1.pdf`; leave those as-is).
- Filenames use `snake_case` / course numbering prefixes (`26_INCA_MDA.pdf`). The wiki
  generator derives page titles and URL slugs from names: leading digits are stripped,
  `___` becomes " - ", `_` becomes a space. Keep new filenames consistent with this.
- Python scripts: stdlib-first, simple `main()` + `if __name__ == '__main__'` layout,
  `pathlib` for paths, no type annotations in `consolidate.py` but typed where useful
  in `build_wiki.py`. Match the style of the file you are editing.
- To edit wiki content, edit the articles in `wiki/articles/` — never `wiki/docs/`
  (regenerated). Article style: single `#` title, `##` sections, rewritten prose (no
  verbatim slide text), Mermaid diagrams via ```` ```mermaid ```` blocks, cropped
  figures in a local `img/` dir, a `!!! success "Key takeaways"` admonition at the
  end. Do NOT write "Source material"/"Downloads" sections — `build_wiki.py` appends
  them from the MIL* tree. The style exemplar is `wiki/articles/mil1/can-lin/index.md`.
- To add or reorganize source content: place files under the appropriate
  `MIL<N>/<Topic>/` directory, run `extract_decks.py` if PDFs changed, write/refresh
  the matching article under `wiki/articles/`, then re-run `build_wiki.py` (and
  `consolidate.py` if you touched `cards_export.json`, `VideoLinks.txt`, or
  `MIL2_Links.txt`). New file extensions may need to be registered in
  `build_wiki.py`'s `TRANSCRIPT_EXTS` / `ATTACH_EXTS` / `SKIP_EXTS` sets. If a whole
  module changes theme, update `MODULE_TITLES` / `MODULE_BLURBS` in `build_wiki.py`.
- Never commit or copy generated artifacts (`wiki/docs/`, `wiki/site/`,
  `wiki/.cache/`, `mkdocs.yml`, `Files/`, `heirarchy.txt`) by hand — regenerate them.
- Theme changes go only in `wiki/theme/` (template override in `overrides/`,
  CSS/JS in `assets/`). New asset files must be registered in `build_wiki.py`
  (`MKDOCS_HEADER`'s `extra_css`/`extra_javascript` lists — `copy_theme_assets()`
  copies the whole `assets/` dir, but only listed files are referenced by the
  generated `mkdocs.yml`). Never paste custom CSS/JS into generated files.
- `mkdocs serve` does **not** watch `wiki/articles/` or `wiki/theme/` — after
  editing either, re-run `build_wiki.py` and restart serve (or run
  `mkdocs build`) to see changes.

## Testing

There are no automated tests. Verification is manual:

1. `wiki-venv/bin/python wiki/build_wiki.py` runs without errors.
2. `cd wiki && ../wiki-venv/bin/mkdocs build` completes without warnings about missing
   pages or broken nav entries.
3. Spot-check the built site (`mkdocs serve`) for the changed pages.

## Safety considerations

Several scripts are **destructive by design** — they delete source files after a
successful conversion (`AIL.ps1`, `transcribe_audio.sh`, `convert_to_pdf.sh`). Do not
run them speculatively; warn before executing, and never "fix" them by removing the
safety checks (exit-code verification before deletion).

Also note:

- `wiki/docs/assets/` contains **symlinks into the real `MIL*` content trees** — be
  careful with recursive delete/copy operations under `wiki/docs/`.
- The repo contains proprietary automotive data (Stellantis/FCA DBC/CDD files for the
  P332 BEV platform, internal specs such as VF179). Treat it as confidential; do not
  publish or upload it externally.
- `consolidate.py` overwrites `Files/` and `heirarchy.txt` on every run.
