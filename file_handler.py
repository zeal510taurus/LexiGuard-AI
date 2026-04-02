from PyPDF2 import PdfReader

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_txt(file):
    return file.read().decode("utf-8")