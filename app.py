import streamlit as st
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
import re
import tempfile
import os
from PIL import Image

# Title
st.title("📊 Financial PDF Analyzer with OCR Fallback")

# Upload
uploaded_file = st.file_uploader("Upload Financial Statement PDF", type="pdf")

def extract_text_text_based(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text
    return full_text

def extract_text_ocr(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    full_text = ""
    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')
        full_text += text
    return full_text

def extract_financial_metrics(text):
    # Simple pattern-based extractor for demo purposes
    patterns = {
        "Revenue": r"Revenue[:\s]*([\d,\.]+)",
        "Gross Profit": r"Gross\s+Profit[:\s]*([\d,\.]+)",
        "Net Income": r"Net\s+Income[:\s]*([\d,\.]+)",
        "EBITDA": r"EBITDA[:\s]*([\d,\.]+)"
    }

    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[key] = match.group(1)
    return extracted

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    # First try text-based extraction
    st.info("🔍 Trying to extract from text-based PDF...")
    extracted_text = extract_text_text_based(tmp_path)

    if not extracted_text.strip():
        st.warning("⚠️ No text detected. Trying OCR...")
        extracted_text = extract_text_ocr(tmp_path)

    metrics = extract_financial_metrics(extracted_text)

    if metrics:
        st.success("✅ Financial Metrics Extracted:")
        st.table(metrics)
    else:
        st.error("🚫 No financial metrics were extracted. Please upload a clearer PDF.")
    
    os.remove(tmp_path)
