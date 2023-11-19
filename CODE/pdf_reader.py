import pandas as pd
import re
import fitz
from collections import Counter, defaultdict
import json

class PDFReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(self.file_path)
        self.fonts = []
        self.sizes = []
        self.colors = []
    
    @staticmethod
    def read_sections_template():
        df = pd.read_csv("sekcje_format.csv", sep=";", header=0)
        return df[~df["nazwa_sekcji"].isin(["Działalność i wyniki operacyjne", "System zarządzania", "Profil ryzyka", "Wycena do celów wypłacalności", "Zarządzanie kapitałem"])]

    
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

    def get_headers_text(self):
        headers = defaultdict(list)
        
        # sections_counter = Counter()
        _ = self.extract_pdf()
        sekcje = list(PDFReader.read_sections_template()["nazwa_sekcji"])

        # configs = []

        # Filters to detect headlines
        size_thresh = self.get_size_filter(self.sizes)
        max_size = self.get_size_filter(self.sizes, 1)
        most_common_color = self.get_color_filter(self.colors)
        most_common_font = self.get_font_filter(self.fonts)
        is_header = False
        in_section = False
        for s in self.doc_iterator(self.doc):
            text = s["text"]
            if in_section and len(headers["text"])>0:
                headers["text"][-1] += text
            if s["size"]>size_thresh or s["size"]==max_size or s["color"] != most_common_color or s["font"]!=most_common_font:
                if is_header:
                    headers["header"][-1]+=text
                    continue
                in_section = False
                sections_present = set(self.find_sections_by_name(sekcje, text) + self.find_sections_by_id(text))
                if len(sections_present)>0:
                    headers["sections_present"].append(tuple(sections_present))
                    headers["header"].append(text)
                    headers["size"].append(s["size"])
                    headers["color"].append(s["color"])
                    headers["font"].append(s["font"])
                    headers["text"].append(text)

                    # sections_counter[tuple(sections_present)]+=1
                    # configs.append((s["size"], s["color"], s["font"], tuple(sections_present)))
                    is_header = True
                    in_section = True
            else:
                is_header = False

        with open("headers.json", "w") as f:
            json.dump(headers, f, indent=4)
        return headers

    def keyword_duplicates(keywords: list[str], texts: list[str]):
        for text in texts:
            keyword_counter = 0
            for keyword in keywords:
                if keyword in text:
                    keyword_counter+=1
        pass

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
                    for j in range(1, 12):
                        section = f'{letter}.{i}.{j}'
                        if len(re.findall(section, text))>0:
                            sections_present.append(section)
        return sections_present


def main():
    pdf_reader = PDFReader("2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf")
    pdf_reader2 = PDFReader("SFCR NN TUNZ 2021.pdf")
    pdf_reader.get_headers_text()

if __name__ == "__main__":
    main()