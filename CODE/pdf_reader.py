import pandas as pd
import re
import fitz
from collections import Counter

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = None
        self.fonts = []
        self.sizes = []
        self.colors = []
    
    @staticmethod
    def read_sections_template():
        return pd.read_csv("sekcje_format.csv", sep=";", header=0)
    
    def open_pdf(self):
        self.doc = fitz.open(self.file_path)
    
    def extract_pdf(self):
        if self.doc is None:
            self.open_pdf()
        text = ""
        for s in self.doc_iterator(self.doc):
            text += s["text"]
            self.fonts.append(s["font"])
            self.colors.append(s["color"])
            self.sizes.append(s["size"])
        return text
    
    def doc_iterator(self, doc):
        for page in doc:
            blocks = page.get_text("dict", flags=11)["blocks"]
            for b in blocks:
                for l in b["lines"]:
                    for s in l["spans"]:
                        yield s

    
    def read_text(self):
        _ = self.extract_pdf()
        sekcje = list(PDFReader.read_sections_template()["nazwa_sekcji"])
        size_thresh = self.get_size_threshold(self.sizes)
        max_size = self.get_size_threshold(self.sizes, 1)

        if_print = False
        for s in self.doc_iterator(self.doc):
            text = s["text"]
            if if_print:
                print(text)

            if s["size"]>size_thresh or s["size"]==max_size:
                if_print = False
                sections_present = self.find_sections_by_name(sekcje, text)
                if len(sections_present)>0:
                    if_print = True
                    print(sections_present)
                    print(text)
                    print("________")
        return 

    def get_size_threshold(self, sizes: list, quantile: float = 0.8):
        print(quantile)
        return pd.Series(sizes).quantile(quantile)

    def find_sections_by_name(self, all_sections: list[str], text: str):
        sections_present = []
        for section in all_sections:
            if len(re.findall(section, text))>0:
                sections_present.append(section)
        return sections_present
    
def main():
    pdf_reader = PDFReader("2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf")
    pdf_reader2 = PDFReader("SFCR NN TUNZ 2021.pdf")
    text_content, fonts, sizes, colors = pdf_reader2.read_text()

    # text_content = text_content.replace(".", " ")
    text_content = re.sub(r'\s+', ' ', text_content)



if __name__ == "__main__":
    main()