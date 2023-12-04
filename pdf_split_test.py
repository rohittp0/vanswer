import PyPDF2
from pdf2image import convert_from_path
import os

def split_pdf_extract_text_and_images(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        for i in range(num_pages):
            # Extract text
            page = reader.pages[i]
            text = page.extract_text()
            text_file_path = os.path.join(output_folder, f'page_{i+1}.txt')
            with open(text_file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(text or "No text found.")

            # Extract images
            images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
            for j, image in enumerate(images):
                image_file_path = os.path.join(output_folder, f'page_{i+1}_image_{j+1}.jpg')
                image.save(image_file_path, 'JPEG')


pdf_path = 'media/05b41ab6-5307-40c1-a41f-936d68b68d5d.pdf'  # Replace with your PDF file path
output_folder = 'media'  # Replace with your desired output folder path

split_pdf_extract_text_and_images(pdf_path, output_folder)
