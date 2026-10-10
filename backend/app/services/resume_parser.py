from io import BytesIO
import logging

from docx import Document
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_file = BytesIO(file_bytes)
        reader = PdfReader(pdf_file)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()
    except Exception as e:
        logger.warning(f"Failed to parse PDF file: {e}")
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        docx_file = BytesIO(file_bytes)
        document = Document(docx_file)

        paragraphs = []
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text)

        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.warning(f"Failed to parse DOCX file: {e}")
        return ""