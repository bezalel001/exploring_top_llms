import io, re, requests
import pdfplumber
from pdf2image import convert_from_bytes
import pytesseract

def _load_pdf(url_or_path: str) -> bytes:
    if re.match(r"^https?://", url_or_path):
        r = requests.get(url_or_path, timeout=30)
        r.raise_for_status()
        return r.content
    with open(url_or_path, "rb") as f:
        return f.read()

def extract_pdf_text_any(url_or_path: str, use_ocr_fallback: bool = True, lang: str = "eng") -> str:
    raw = _load_pdf(url_or_path)

    # Pass 1: digital text
    text_parts = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    text = "\n".join(text_parts).strip()

    # If nothing meaningful and allowed, Pass 2: OCR
    if use_ocr_fallback and len(text) < 30:
        images = convert_from_bytes(raw, dpi=200)  # 200–300 dpi is typical
        ocr_pages = [pytesseract.image_to_string(img, lang=lang) for img in images]
        text = "\n".join(ocr_pages).strip()

    return text
