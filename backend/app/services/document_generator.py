import io
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from fpdf import FPDF

COMMON_SECTION_HEADERS = {
    "SUMMARY", "PROFESSIONAL SUMMARY", "CAREER SUMMARY", "EXECUTIVE SUMMARY",
    "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "AREAS OF EXPERTISE",
    "EXPERIENCE", "PROFESSIONAL EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY",
    "PROJECTS", "KEY PROJECTS", "ACADEMIC PROJECTS",
    "EDUCATION", "ACADEMIC BACKGROUND",
    "CERTIFICATIONS", "CERTIFICATIONS & LICENSES", "ACHIEVEMENTS", "HONORS & AWARDS"
}


def _is_section_header(line: str) -> bool:
    """
    Returns True only if the line is a known section header OR is a short
    all-uppercase line with at least 2 words (prevents single-word names
    like 'JOHN' from being mistaken as headers).
    """
    clean = line.strip().rstrip(":").upper()
    if clean in COMMON_SECTION_HEADERS:
        return True
    # BUG FIX #1: Require at least 2 words to avoid flagging candidate names
    # (e.g. "JOHN" or "SKILLS" by itself) as false-positive section headers.
    return (
        clean.isupper()
        and len(clean.split()) >= 2       # must be multi-word (e.g. "WORK EXPERIENCE")
        and len(clean.split()) <= 4
        and len(clean) >= 4
    )


def generate_docx(resume_text: str) -> io.BytesIO:
    """
    Generates an ATS-optimized, professionally styled DOCX document.
    Preserves exact CV structure with proper headings and bullet points.
    """
    # BUG FIX #2: Guard against None/empty input to avoid AttributeError on splitlines()
    if not resume_text:
        resume_text = ""

    doc = Document()

    # Set 0.75 inch standard margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    lines = [l.strip() for l in resume_text.splitlines()]
    first_non_empty = True

    for line in lines:
        # BUG FIX #3: Empty lines were skipped with `continue`, removing ALL spacing
        # between sections in the DOCX. Now we add a small spacer paragraph instead.
        if not line:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            continue

        # Check for first line (Candidate Name)
        if first_non_empty:
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.bold = True
            run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(15, 23, 42)
            first_non_empty = False
            continue

        # Check for Section Header
        if _is_section_header(line):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(line.rstrip(":").upper())
            run.bold = True
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(37, 99, 235)  # Professional blue accent
            continue

        # Check for Bullet Item
        if re.match(r"^[•\-*]\s+", line):
            content = re.sub(r"^[•\-*]\s+", "", line)
            # BUG FIX #4: 'List Bullet' style may not exist in all Word templates,
            # causing a KeyError crash. Use Normal style + manual indent instead.
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(f"• {content}")
            run.font.size = Pt(10)
            continue

        # Normal Paragraph (Contact info, Company details, Summary paragraph)
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream


def generate_pdf(resume_text: str) -> io.BytesIO:
    """
    Generates a clean, ATS-compliant PDF document.
    Sanitizes Unicode characters to avoid latin-1 encoding errors/question marks.
    """
    # BUG FIX #2 (PDF): Guard against None/empty input
    if not resume_text:
        resume_text = ""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Pre-clean Unicode characters to safe ASCII/Latin-1
    replacements = {
        "\u2022": "- ",   # bullet •
        "\u2013": "-",    # en dash –
        "\u2014": "-",    # em dash —
        "\u2018": "'",    # left single quote '
        "\u2019": "'",    # right single quote '
        "\u201c": '"',    # left double quote "
        "\u201d": '"',    # right double quote "
        "\u2026": "...",  # ellipsis …
        "\xa0":  " ",     # non-breaking space
        "•": "- ",
        "–": "-",
        "—": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
    }
    safe_text = resume_text
    for src, dst in replacements.items():
        safe_text = safe_text.replace(src, dst)

    safe_text = safe_text.encode("latin-1", "replace").decode("latin-1")
    lines = [l.strip() for l in safe_text.splitlines()]

    first_line = True
    for line in lines:
        if not line:
            pdf.ln(3)
            continue

        # Candidate Name at top
        if first_line:
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 8, txt=line, new_x="LMARGIN", new_y="NEXT", align="L")
            pdf.ln(2)
            first_line = False
            continue

        # Section Heading
        if _is_section_header(line):
            pdf.ln(4)
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.set_text_color(37, 99, 235)
            pdf.cell(0, 7, txt=line.rstrip(":").upper(), new_x="LMARGIN", new_y="NEXT")
            # BUG FIX #5: pdf.get_x() after new_y="NEXT" returns left margin — using
            # it as both start and computing end from it caused the underline to
            # always draw from margin+margin (double-offset). Use pdf.l_margin directly.
            pdf.set_draw_color(226, 232, 240)
            line_width = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + line_width, pdf.get_y())
            pdf.ln(2)
            continue

        # Bullet line
        if re.match(r"^[•\-*]\s+", line):
            # BUG FIX #6: `clean_bullet` was set to the raw `line` (keeping the bullet
            # marker). Now we strip the marker and use a consistent "  - " prefix.
            clean_bullet = re.sub(r"^[•\-*]\s+", "", line)
            pdf.set_font("Helvetica", size=10)
            pdf.set_text_color(51, 65, 85)
            pdf.multi_cell(0, 5.5, txt="  - " + clean_bullet, new_x="LMARGIN", new_y="NEXT")
            continue

        # Standard line (Contact info, Summary, etc.)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(0, 5.5, txt=line, new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    file_stream = io.BytesIO(pdf_bytes)
    file_stream.seek(0)
    return file_stream
