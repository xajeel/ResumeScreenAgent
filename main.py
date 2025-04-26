from src.dataextraction import get_pdf_files_in_directory, extract_text_from_pdf
from src.model import extract_candidate_info

# Job description txt file loading
job_description_path = "pdfs/job.txt"
with open(job_description_path, 'r') as file:
    job_description = file.read()



directory_path = "pdfs" 
pdf_files = get_pdf_files_in_directory(directory_path)

for pdf_file in pdf_files:
    text = extract_text_from_pdf(pdf_file)
    response = extract_candidate_info(job_description, text)
    print(response)