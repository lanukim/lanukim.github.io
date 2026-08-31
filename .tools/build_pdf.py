import docx
from docx.oxml.ns import qn
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = str(REPO_ROOT / "assets" / "cv" / "lkim-cv-source.docx")
OUT = str(REPO_ROOT / "assets" / "cv" / "lkim-cv.pdf")

d = docx.Document(SRC)

def run_props(r):
    rpr = r.find(qn('w:rPr'))
    bold = italic = underline = False
    size = None
    if rpr is not None:
        bold = rpr.find(qn('w:b')) is not None
        italic = rpr.find(qn('w:i')) is not None
        underline = rpr.find(qn('w:u')) is not None
        sz = rpr.find(qn('w:sz'))
        if sz is not None:
            size = int(sz.get(qn('w:val'))) / 2.0
    return bold, italic, underline, size

def para_markup_and_plain(p):
    markup_parts = []
    plain_parts = []
    for r in p._p.iter(qn('w:r')):
        bold, italic, underline, size = run_props(r)
        seg = ""
        for child in r:
            tag = child.tag
            if tag == qn('w:t'):
                seg += (child.text or "")
            elif tag == qn('w:br') or tag == qn('w:cr'):
                seg += "\n"
            elif tag == qn('w:tab'):
                seg += "    "
        if not seg:
            continue
        plain_parts.append(seg.replace("\n", " "))
        pieces = seg.split("\n")
        wrapped = []
        for piece in pieces:
            t = escape(piece)
            if bold:
                t = f"<b>{t}</b>"
            if italic:
                t = f"<i>{t}</i>"
            if underline:
                t = f"<u>{t}</u>"
            if size:
                t = f'<font size="{size:g}">{t}</font>'
            wrapped.append(t)
        markup_parts.append("<br/>".join(wrapped))
    return "".join(markup_parts), "".join(plain_parts)

heading_style = ParagraphStyle("heading", fontName="Times-Bold", fontSize=13, leading=15,
                                alignment=TA_CENTER, spaceBefore=2, spaceAfter=2)
name_style = ParagraphStyle("name", fontName="Times-Bold", fontSize=20, leading=20, alignment=TA_CENTER)
header_style = ParagraphStyle("header", fontName="Times-Bold", fontSize=11, leading=11, alignment=TA_CENTER)
contact_style = ParagraphStyle("contact", fontName="Times-Bold", fontSize=10.5, leading=10.5, alignment=TA_CENTER)
body_style = ParagraphStyle("body", fontName="Times-Roman", fontSize=11, leading=13.5, alignment=TA_LEFT, spaceAfter=0)
bullet_style = ParagraphStyle("bullet", fontName="Times-Roman", fontSize=11, leading=13.5, alignment=TA_LEFT,
                               leftIndent=18, firstLineIndent=-14, spaceAfter=0)
sub_style = ParagraphStyle("sub", fontName="Times-Bold", fontSize=11, leading=13.5, alignment=TA_LEFT, spaceBefore=4, spaceAfter=0)

SECTION_HEADS = {"RESEARCH INTERESTS","ACADEMIC POSITIONS","EDUCATION","PUBLICATIONS","AWARDS",
                  "GRANTS","TEACHING","SERVICES"}

story = []
paras = d.paragraphs
n = len(paras)
seen_name = False

for i, p in enumerate(paras):
    markup, plain = para_markup_and_plain(p)
    text = plain.strip()
    is_title_style = (p.style is not None and p.style.name == "Title")

    if not text:
        story.append(Spacer(1, 6))
        continue

    if not seen_name and text == "LANU KIM":
        story.append(Paragraph("LANU KIM", name_style))
        seen_name = True
        continue

    if text.upper() in SECTION_HEADS and text.upper() == text:
        story.append(Paragraph(markup, heading_style))
        continue

    if not markup:
        markup = escape(text)

    has_numpr = p._p.find(qn('w:pPr') + '/' + qn('w:numPr')) is not None

    if text.lstrip().startswith("•"):
        content = markup.split("•", 1)[-1].strip()
        story.append(Paragraph(f"•&nbsp;&nbsp;{content}", bullet_style))
    elif has_numpr:
        story.append(Paragraph(f"•&nbsp;&nbsp;{markup}", bullet_style))
    elif is_title_style:
        if any(k in text for k in ["Daehak", "Daejeon", "Phone", "Website", "Lab website", "Email"]):
            story.append(Paragraph(markup, contact_style))
        else:
            story.append(Paragraph(markup, header_style))
    else:
        style = sub_style if (text.endswith("courses")) else body_style
        story.append(Paragraph(markup, style))

while story and isinstance(story[-1], Spacer):
    story.pop()

doc = SimpleDocTemplate(OUT, pagesize=LETTER,
                         topMargin=0.85*inch, bottomMargin=0.85*inch,
                         leftMargin=1.0*inch, rightMargin=1.0*inch)
doc.build(story)
print("PDF written:", OUT)
