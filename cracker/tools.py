import fitz  
import re


def extract_file_year(pdf_path:str) -> str:
    # this is meant to be used when creating pdf name
    pdf_document = fitz.open(pdf_path)

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text()

        year_pattern = re.compile(r'\b(?:20\d{2})\b')
        year_found = year_pattern.search(text)

        if year_found:
            found_year = str(int(year_found.group()))
            pdf_document.close()
            return found_year

    pdf_document.close()
    return '0000'


def extract_file_date(pdf_path:str)->str:
    # this is meant to be used to generate 'DATA SFCR' column
    pdf_document = fitz.open(pdf_path)

    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        text = page.get_text()

        polish_date_pattern = re.compile(r'\b(?:\d{1,2}\s(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s\d{4})\b', re.IGNORECASE)
        dates_found = polish_date_pattern.findall(text)

        if dates_found:
            date_str = dates_found[0]
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
            for k, v in lookup_table.items():
                date_str = date_str.replace(k,v)
            pdf_document.close()
            return date_str

    pdf_document.close()
    return '01.01.1970'