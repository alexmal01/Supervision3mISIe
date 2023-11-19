import pandas as pd
import re
import fitz
from collections import Counter, defaultdict
import json
import difflib
import numpy as np
from .tools import extract_file_date
from typing import Generator

class PDFReader:
    """
    Class for reading PDF files and segmenting them into sections
    """
    def __init__(self, file_path: str) -> None:
        """
        :param file_path: path to the PDF file
        """
        self.file_path = file_path
        self.doc = fitz.open(self.file_path)
        self.fonts: list[str] = []
        self.sizes: list[float] = []
        self.colors: list[float] = []
        self.date = extract_file_date(file_path)
    
    @staticmethod
    def read_sections_template() -> pd.DataFrame:
        """
        Method for reading the sections template file - extracted from appendix 2 of the task guidelines

        :return: dataframe with sections template
        """
        df = pd.read_csv("sekcje_format.csv", sep=";", header=0)
        return df[~df["nazwa_sekcji"].isin(["Działalność i wyniki operacyjne", "System zarządzania", "Profil ryzyka", "Wycena do celów wypłacalności", "Zarządzanie kapitałem"])]

    @staticmethod
    def doc_iterator(doc) -> Generator:
        """
        Generator for iterating through the PDF document and extracting key information about the text
        Extracted information: text, font type, font color, font size

        :param doc: PDF document
        """
        for page in doc:
            blocks = page.get_text("dict", flags=11)["blocks"]
            for b in blocks:
                for l in b["lines"]:
                    for s in l["spans"]:
                        yield s
    
    def extract_pdf(self) -> str:
        """
        Method for extracting text from the PDF file

        :return: extracted text
        """
        text = ""
        for s in PDFReader.doc_iterator(self.doc):
            text += s["text"]
            self.fonts.append(s["font"])
            self.colors.append(s["color"])
            self.sizes.append(s["size"])
        return text

    def get_headers_text(self, save_headers: bool = False) -> dict:
        """
        One of the main methods, used to detect headings in the file.
        It uses a set of filters to detect headlines int the pdf text.
        Filters are based on the font size, font color, and its text content.
        Text between headlines is then extracted.

        :param save_headers: boolean flag, whether extracted headers should be saved to a json file
        :return: dictionary with extracted headers, full paragraph text, header font features: size, color, type
        """
        headers = defaultdict(list)
        _ = self.extract_pdf()
        sekcje = list(PDFReader.read_sections_template()["nazwa_sekcji"])

        # Filters to detect headlines
        size_thresh = self.get_size_filter()
        max_size = self.get_size_filter(1)
        most_common_color = self.get_color_filter()
        most_common_font = self.get_font_filter()

        is_header = False
        in_section = False

        # Iteration through the PDF document
        for s in PDFReader.doc_iterator(self.doc):
            text = s["text"]
            if in_section and len(headers["text"])>0:
                headers["text"][-1] += text
            # Filtering headline candidates
            if s["size"]>size_thresh or s["size"]==max_size or s["color"] != most_common_color or s["font"]!=most_common_font:
                if is_header:
                    headers["header"][-1]+=text
                    continue
                in_section = False
                # Checking whether headlines match section name or naming pattern (i.e. A.1.1 or B.1.2.1)
                sections_present = set(self.find_sections_by_name(sekcje, text) + self.find_sections_by_id(text))
                if len(sections_present)>0:
                    headers["sections_present"].append(tuple(sections_present))
                    headers["header"].append(text)
                    headers["size"].append(s["size"])
                    headers["color"].append(s["color"])
                    headers["font"].append(s["font"])
                    headers["text"].append(text)

                    is_header = True
                    in_section = True
            else:
                is_header = False


        # Dumping headers to json file
        if save_headers:
            with open("headers.json", "w") as f:
                json.dump(headers, f, indent=4)
        return headers

    def get_size_filter(self, quantile: float = 0.8) -> float:
        """
        Filters font sizes based on quantile

        :param quantile: quantile to filter font sizes
        :return: quantile value
        """
        return pd.Series(self.sizes).quantile(quantile)
    
    def get_color_filter(self) -> float:
        """
        Filters font colors based on the most common color

        :return: most common color
        """
        return Counter(self.colors).most_common(1)[0][0]
    
    def get_font_filter(self) -> str:
        """
        Filters out the most common font type

        :return: most common font type
        """
        return Counter(self.fonts).most_common(1)[0][0]

    def find_sections_by_name(self, all_sections: list[str], text: str) -> list[str]:
        """
        Checks which sections are present in the text.
        Method combines equal matching using RegEx and fuzzy matching using difflib

        :param all_sections: list of all available sections, in usage set to sections from the template
        :param text: text to be checked

        :return: list of sections present in the text
        """
        sections_present = []

        for section in all_sections:
            fuzzy_matches = difflib.get_close_matches(section, text.split(), n=3, cutoff=0.75)
            exact_matches = re.findall(section, text)
            all_matches = list(set(fuzzy_matches+exact_matches))
            if len(all_matches)>0:
                sections_present.append(section)
        return sections_present
    
    def find_sections_by_id(self, text: str, all_letters: list[str] = ["A", "B", "C", "D", "E"]) -> list[str]:
        """
        Method for finding sections by their id (i.e. A.1.1 or B.1.2.1)

        :param text: text to be checked
        :param all_letters: list of all available letters used in section ids
        :return: list of sections present in the text
        """
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
    

    @staticmethod
    def remove_duplicate_first_word(text: str) -> str:
        """
        Function removes duplicate first word from the text

        :param text: text to be checked
        :return: text without duplicate first word
        """
        words = text.strip().split()
        if len(words) > 1 and words[0] == words[1]:
            return ' '.join(words[1:])
        else:
            return text

    def create_df(self, headers: dict):
        """
        Function creates final dataframe with extracted headers and their content

        :param headers: dictionary with extracted headers, full paragraph text, header font features: size, color, type
        """
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
        df['NAZWA_SEKCJI'] = df['sections_present'].map(id_name).combine_first(df['header'])
        df['id_sekcji_tmp'] = df['sections_present'].map(name_id).combine_first(df['sections_present']).apply(lambda x: x.replace(" ", "").strip())
        df['sekcja_nadrzedna'] = df["id_sekcji_tmp"].apply(lambda x: ".".join(x.split(".")[:-1])).replace({"A": "A.", "B":"B.", "C": "C.", "D": "D.", "E": "E."})
        df['ID_SEKCJA NADRZĘDNA'] = df.merge(sekcje, how="left", left_on="sekcja_nadrzedna", right_on="id_sekcji")["id"]
        df['ID_SEKCJA'] = df.merge(sekcje, how="left", left_on="id_sekcji_tmp", right_on="id_sekcji")["id"]
        df['NAZWA_SEKCJI'] = df['id_sekcji_tmp'] + " "+df['NAZWA_SEKCJI']


        df['NAZWA_SEKCJI'] = df['NAZWA_SEKCJI'].apply(PDFReader.remove_duplicate_first_word)
        def skip_first_n_chars(row):
            n = len(row['NAZWA_SEKCJI'].split())
            return " ".join(row['text'].split()[max(0,n-1):])
        df['TREŚĆ']=df.apply(skip_first_n_chars, axis=1)
        df['ID_SEKCJA'] = df['ID_SEKCJA'].fillna(df['id_sekcji_tmp']+"_DEL")
        df = df.sort_values(by=["ID_SEKCJA", "num_ocs"], ascending=False)
        df = df.drop_duplicates(subset=["ID_SEKCJA"], keep="first")
        df['ID_SEKCJA'] = df['ID_SEKCJA'].apply(lambda x: np.nan if isinstance(x, str) and "_DEL" in x else x)
        df = df.loc[:, ['ID_SEKCJA NADRZĘDNA', 'ID_SEKCJA', 'NAZWA_SEKCJI', 'TREŚĆ']].reset_index(drop=True)
        df['DATA SFCR'] = self.date
        df['WERSJA SFCR'] = 1 # TODO
        df['KOD ZAKŁADU'] = 1 # TODO
        return df



def main():
    # This is example usage of the class
    sfcr_file_path = '2022-SFCR-TUIR-Sprawozdanie-o-wyplacalnosci-i-kondycji-finansowej.pdf'
    pdf_reader = PDFReader(sfcr_file_path)
    headers = pdf_reader.get_headers_text()
    pdf_reader.create_df(headers)

    

if __name__ == "__main__":
    main()