import PyPDF2
import pandas as pd
import re

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def read_sections_template():
        return pd.read_csv("sekcje_format.csv", sep=";", header=0, index_col='id')

    def read_text(self):
        with open(self.file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
        
    def find_headings(self, text: str):
        # Define a regular expression pattern for identifying headings
        heading_pattern = re.compile(r'^[A-Z].*$', re.MULTILINE)
        matches = heading_pattern.findall(text)
        return matches

def main():

    # file_path = '2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf'
    # pdf_reader = PDFReader(file_path)

    # # Read text from the PDF
    # text_content = pdf_reader.read_text()
    # print("Text content:\n", text_content)
    # print(pdf_reader.find_headings(text_content))
    df = pd.read_csv("sekcje_format.csv", sep=";", header=0, index_col='id')
    print(df)

if __name__ == "__main__":
    main()