import os
from PyPDF2 import PdfReader

# Function to get the path to all the PDF files in a directory
def get_pdf_files_in_directory(directory_path):
    pdf_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"An error occurred while reading the PDF: {e}"

    