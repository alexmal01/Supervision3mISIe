import pandas as pd
import re
import fitz
from collections import Counter

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(self.file_path)
        self.fonts = []
        self.sizes = []
        self.colors = []
    
    @staticmethod
    def read_sections_template():
        return pd.read_csv("sekcje_format.csv", sep=";", header=0)
    
    def extract_pdf(self):
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
        ile = Counter()
        _ = self.extract_pdf()
        sekcje = list(PDFReader.read_sections_template()["nazwa_sekcji"])

        configs = []

        # Filters to detect headlines
        size_thresh = self.get_size_filter(self.sizes)
        max_size = self.get_size_filter(self.sizes, 1)
        most_common_color = self.get_color_filter(self.colors)
        most_common_font = self.get_font_filter(self.fonts)

        if_print = False
        is_header = False
        counter=0
        for s in self.doc_iterator(self.doc):
            text = s["text"]
            if if_print:
                print(text)

            if s["size"]>size_thresh or s["size"]==max_size or s["color"] != most_common_color or s["font"]!=most_common_font:
                if is_header:
                    continue
                if_print = False
                sections_present = set(self.find_sections_by_name(sekcje, text) + self.find_sections_by_id(text))
                # sekcje = list(set(sekcje) - sections_present)
                if len(sections_present)>0:

                    # Temporary statistics
                    ile[tuple(sections_present)]+=1
                    # for sekcja in sections_present:
                    #     ile[sekcja]+=1
                    configs.append((s["size"], s["color"], s["font"]))


                    if_print = True
                    is_header = True
                    print("________")
                    print(sections_present)
                    print(text)
                    counter+=1
                    print(counter)
            else:
                is_header = False
        print(ile)
        print("_____________")
        print(Counter(configs))
        return 

    def get_size_filter(self, sizes: list, quantile: float = 0.8):
        return pd.Series(sizes).quantile(quantile)
    
    def get_color_filter(self, colors: list):
        return Counter(colors).most_common(1)[0][0]
    
    def get_font_filter(self, fonts: list):
        return Counter(fonts).most_common(1)[0][0]

    def find_sections_by_name(self, all_sections: list[str], text: str):
        sections_present = []
        for section in all_sections:
            if len(re.findall(section, text))>0:
                sections_present.append(section)
        return sections_present
    
    def find_sections_by_id(self, text: str, all_letters: list[str] = ["A", "B", "C", "D", "E"]):
        sections_present = []
        for letter in all_letters:
            for i in range(1, 6):
                for comb in ["", ".", " .", " ",". "]:
                    section = f'{letter}{comb}{i}'
                    if len(re.findall(section, text))>0:
                        sections_present.append(section)

                    section_alt = f'{letter}. {i}'
                    if len(re.findall(section_alt, text))>0:
                        sections_present.append(section_alt)
                    for j in range(1, 12):
                        section = f'{letter}.{i}.{j}'
                        if len(re.findall(section, text))>0:
                            sections_present.append(section)
        return sections_present


def main():
    pdf_reader = PDFReader("2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf")
    pdf_reader2 = PDFReader("SFCR NN TUNZ 2021.pdf")
    pdf_reader2.read_text()

    # text_content = text_content.replace(".", " ")
    text_content = re.sub(r'\s+', ' ', text_content)



if __name__ == "__main__":
    main()