from src.dataextraction import get_pdf_files_in_directory, extract_text_from_pdf

directory_path = "pdfs" 
pdf_files = get_pdf_files_in_directory(directory_path)

for pdf_file in pdf_files:
    text = extract_text_from_pdf(pdf_file)
    print(f"Text extracted from {pdf_file}:\n{text}\n")