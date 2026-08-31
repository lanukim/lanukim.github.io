# CV tooling

`assets/cv/lkim-cv-source.docx` is the editable master for the CV. `assets/cv/lkim-cv.pdf`
(the file linked from the site) is generated from it — never hand-edit the PDF.

## Regenerating the PDF

```bash
pip install -r .tools/requirements.txt
python3 .tools/build_pdf.py
```

This reads `assets/cv/lkim-cv-source.docx` and writes `assets/cv/lkim-cv.pdf`.

## Editing the docx

Word splits text across many `<w:r>` runs, so a phrase you can see in the document
often isn't a contiguous string in the XML. Edit it as a zip:

```bash
mkdir /tmp/cv_unpack
unzip assets/cv/lkim-cv-source.docx -d /tmp/cv_unpack
# edit /tmp/cv_unpack/word/document.xml (see conventions below)
(cd /tmp/cv_unpack && zip -Xrq /tmp/new.docx .)
cp /tmp/new.docx assets/cv/lkim-cv-source.docx
python3 .tools/build_pdf.py
```

Find the paragraph you want to change by grepping for a short, distinctive
substring (e.g. an author's last name or a DOI) — not the full sentence, since
it may be split across runs.

### Conventions in this document

- **Section headings** (ACADEMIC POSITIONS, PUBLICATIONS, AWARDS, GRANTS,
  TEACHING, SERVICES, RESEARCH INTERESTS, EDUCATION) use a two-tier font-size
  "drop cap" style: the first letter of each word is a separate run at
  `sz=26` (13pt), the rest of the word at `sz=20` (10pt), all bold + underlined
  + centered. `build_pdf.py` reads the per-run `w:sz` directly to reproduce
  this, so any new heading must follow the same two-run-per-word pattern.
- **Bulleted lists** (Publications, Awards, Grants, Teaching, Services) use
  real Word numbering — `<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="6"/></w:numPr>...`
  — not a literal "•" character. Copy an existing bullet paragraph in the
  same section as a template when adding a new one.
- **The name/title/address/contact block** (everything above RESEARCH
  INTERESTS) uses the built-in Word "Title" paragraph style for its centering
  — there's no direct `w:jc` on those paragraphs. `build_pdf.py` detects this
  block by checking `paragraph.style.name == "Title"`, not alignment.
- Author's own name is bolded (`<w:b/>`) wherever it appears in a citation,
  including when she isn't first author. Corresponding-author underlining
  uses `<w:u w:val="single"/>` on that author's name only.
- Journal/venue names are italicized (`<w:i/>`).

## Keeping index.md and the CV in sync

When a paper moves from "under review" / "working paper" / "draft ready" to
published:

1. Get the DOI and fetch exact metadata (authors, journal, volume/issue,
   article number, and the real publication date) from Crossref:
   `curl -s https://api.crossref.org/works/<DOI>` — use `published-online` /
   `published-print` / `published` (in that preference order) for the actual
   date, not just the citation year, since two papers can share a year but
   differ by months.
2. In `index.md`, replace the `[under review]`/`[working paper]`/`[draft
   ready]` line in the "Projects and Publications/Working Papers" section
   with the full citation in the same format as neighboring entries:
   `Author list. Year. "Title." _Journal_ vol(issue). [Link](url)`
3. Recompute `## Recent Publications` — it should hold the ~5 most recent
   entries that have a link, ordered by the actual Crossref date (not just
   year), newest first.
4. Add the same publication as a new bullet in the CV's Publications section
   (see conventions above), positioned by actual date, then regenerate the
   PDF.

A Google Scholar entry that doesn't match anything already on the site
(brand new paper, not previously listed as "under review" etc.) needs a
human decision about which thematic section it belongs in — don't guess,
just flag it.
