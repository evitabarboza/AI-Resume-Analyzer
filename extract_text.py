import PyPDF2

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    extracted_text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
    return extracted_text
