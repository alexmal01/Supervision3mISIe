import fitz  
import re
from .key_words import count_key_phrases


def extract_file_year(pdf_path:str) -> str:
    # this is meant to be used when creating pdf name
    try:
        pdf_document = fitz.open(pdf_path)
    except:
        print("can't open document")
        return '0000'
    year_pattern = re.compile(r'\b(?:20\d{2})\b')
    
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text()

        year_found = year_pattern.search(text)

        if year_found:
            found_year = str(int(year_found.group()))
            pdf_document.close()
            return found_year

    pdf_document.close()
    return '0000'


def extract_file_date(pdf_path:str)->str:
    # this is meant to be used to generate 'DATA SFCR' column
    try:
        pdf_document = fitz.open(pdf_path)
    except:
        print("can't open document")
        return '01.01.1970'
    lookup_table = {
        ' stycznia ': '.01.',
        ' lutego ': '.02.',
        ' marca ': '.03.',
        ' kwietnia ': '.04.',
        ' maja ': '.05.',
        ' czerwca ': '.06.',
        ' lipca ': '.07.',
        ' sierpnia ': '.08.',
        ' września ': '.09.',
        ' października ': '.10.',
        ' listopada ': '.11.',
        ' grudnia ': '.12.'
    }
    polish_date_pattern = re.compile(r'\b(?:\d{1,2}\s(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s\d{4})\b', re.IGNORECASE)

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text()

        dates_found = polish_date_pattern.findall(text)

        if dates_found:
            date_str = dates_found[0].lower()
            for k, v in lookup_table.items():
                date_str = date_str.replace(k,v)
            pdf_document.close()
            return date_str

    pdf_document.close()
    return '01.01.1970'



def parse_audit_pdf(pdf_path:str, stemmer) -> int:
    # this function just looks whether the audit was g or not
    try:
        pdf_document = fitz.open(pdf_path)
    except:
        print("can't open document")
        return None
    
    key_phrases_audit = ['opinia z zastrzeżeniem', 'opinia z zastrzeżeniami', 'podstawa opinii z zastrzeżeniem','opinia negatywna', 'podstawa opinii negatywnej', 'niepewność', 'odmowa wyrażenia opinii', 'odmowa']
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text().replace('\n', ' ').lower()
        text = re.sub(r'[^a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s]', '', text)
        
        counts = count_key_phrases(text,key_phrases_audit,stemmer)
        if sum(counts.values()) > 0:
            return 1
    return 0

