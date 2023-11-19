import pandas as pd
import re
import fitz
from collections import Counter, defaultdict
import json
import difflib
import json
import numpy as np

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
            fuzzy_matches = difflib.get_close_matches(section, text.split(), n=3, cutoff=0.75)
            exact_matches = re.findall(section, text)
            all_matches = list(set(fuzzy_matches+exact_matches))
            if len(all_matches)>0:
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
    
    
    def create_df(self, headers: dict):

        sekcje = pd.read_csv("sekcje_format.csv", sep=";", header=0)

        id_name = dict(zip(list(sekcje["id_sekcji"]), list(sekcje["nazwa_sekcji"])))
        name_id = dict(zip(list(sekcje["nazwa_sekcji"]), list(sekcje["id_sekcji"])))

        for i in range(len(headers["header"])):
            if len(headers["sections_present"][i])>1:
                deepest = max([len(x.split(".")) for x in headers["sections_present"][i]])
                headers["sections_present"][i] = [x for x in headers["sections_present"][i] if len(x.split("."))==deepest]
        
        config_dict = {}
        for i in range(len(headers["header"])):
            config = (headers["size"][i], headers["color"][i], headers["font"][i])
            if config not in config_dict:
                config_dict[config] = set()
            config_dict[config].update(headers["sections_present"][i])

        config_dict = {k: len(v) for k, v in config_dict.items()}

        df = pd.DataFrame(headers)
        df["sections_present"] = df["sections_present"].apply(lambda x: x[0])
        df["tuple"] = df.apply(lambda x: (x["size"], x["color"], x["font"]), axis=1)
        df["num_ocs"] = df["tuple"].map(config_dict)
        df['nazwa_sekcji'] = df['sections_present'].map(id_name).combine_first(df['header'])
        df['id_sekcji_tmp'] = df['sections_present'].map(name_id).combine_first(df['sections_present']).apply(lambda x: x.replace(" ", "").strip())
        df['sekcja_nadrzedna'] = df["id_sekcji_tmp"].apply(lambda x: ".".join(x.split(".")[:-1])).replace({"A": "A.", "B":"B.", "C": "C.", "D": "D.", "E": "E."})
        df['id_sekcji_nadrzednej2'] = df.merge(sekcje, how="left", left_on="sekcja_nadrzedna", right_on="id_sekcji")["id"]
        df['id_sekcji'] = df.merge(sekcje, how="left", left_on="id_sekcji_tmp", right_on="id_sekcji")["id"]
        df['nazwa_sekcji'] = df['id_sekcji_tmp'] + " "+df['nazwa_sekcji']


        def remove_duplicate_first_word(text):
            words = text.strip().split()
            if len(words) > 1 and words[0] == words[1]:
                return ' '.join(words[1:])
            else:
                return text

        df['nazwa_sekcji'] = df['nazwa_sekcji'].apply(remove_duplicate_first_word)
        def skip_first_n_chars(row):
            n = len(row['nazwa_sekcji'].split())
            return " ".join(row['text'].split()[max(0,n-1):])
        df['tresc']=df.apply(skip_first_n_chars, axis=1)
        df['id_sekcji'] = df['id_sekcji'].fillna(df['id_sekcji_tmp']+"_DEL")
        df = df.sort_values(by=["id_sekcji", "num_ocs"], ascending=False)
        df = df.drop_duplicates(subset=["id_sekcji"], keep="first")
        df['id_sekcji'] = df['id_sekcji'].apply(lambda x: np.nan if isinstance(x, str) and "_DEL" in x else x)
        df = df.loc[:, ['id_sekcji_nadrzednej2', 'id_sekcji', 'nazwa_sekcji', 'tresc']].reset_index(drop=True)
        df.to_csv("headers.csv")



def main():
    pdf_reader = PDFReader("2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf")
    pdf_reader2 = PDFReader("SFCR NN TUNZ 2021.pdf")
    headers = pdf_reader2.get_headers_text()
    pdf_reader2.create_df(headers)
    

if __name__ == "__main__":
    main()