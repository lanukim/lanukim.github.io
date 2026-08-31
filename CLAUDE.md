# lanukim.github.io

Lanu Kim's personal academic website (Jekyll, `jekyll-theme-minimal`, GitHub Pages) and CV.
Content lives in `index.md`. The CV is generated from `assets/cv/lkim-cv-source.docx` via
`.tools/build_pdf.py` — see `.tools/README.md` for the editing conventions before touching
either.

## Checking for new publications

When the user asks to check for new papers — any short phrasing works ("확인해줘", "새 논문
있는지 봐줘", "check my papers", etc.) — run this whole pipeline without asking her to spell
out the steps:

1. Fetch her Google Scholar profile:
   `https://scholar.google.com/citations?user=77i0fdMAAAAJ&hl=en&oi=ao`
2. Read the "## Projects and Publications/Working Papers" section of `index.md` and find every
   entry tagged `[under review]`, `[working paper]`, or `[draft ready]`.
3. Match each such entry against the Scholar list by author overlap + topic — titles often
   change between the draft stage and final publication, so don't rely on an exact title match.
4. For each match, fetch exact citation metadata from Crossref
   (`curl -s https://api.crossref.org/works/<DOI>`): authors, journal, volume/issue, article
   number, and the real publication date (prefer `published-online` > `published-print` >
   `published` — not just the citation year, since two papers can share a year but differ by
   months).
5. Update `index.md`: replace the matched entry with the full published citation + `[Link]` in
   the same format as neighboring entries, and recompute `## Recent Publications` (the ~5 most
   recent entries with a link, ordered by actual Crossref date, newest first).
6. Update the CV: add/update the matching bullet in `assets/cv/lkim-cv-source.docx`'s
   Publications section (follow `.tools/README.md` exactly — drop-cap heading style, `numId=6`
   bullet paragraphs, "Title"-style header block), then run `python3 .tools/build_pdf.py` to
   regenerate `assets/cv/lkim-cv.pdf`.
7. Show her the diff and the new CV, and wait for her go-ahead before committing or pushing —
   never push without explicit confirmation.
8. If a Scholar entry doesn't match anything already on the site (a genuinely new paper never
   mentioned before), don't guess which section it belongs in — just flag it to her.
