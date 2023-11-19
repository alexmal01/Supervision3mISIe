import os
import requests
import json
import time
import pandas as pd
import re
import fitz


def filter_links(file, sfcr=True):
    if sfcr:
        print("File:", file)
        with open(file, 'r') as fcc_file:
            links = json.load(fcc_file)
            links = list(links.keys())
            patSFCR = re.compile(r'(.*sfcr.*)', re.IGNORECASE)
            filteredSFCR = [i for i in links if patSFCR.match(i)]

            patSolvency = re.compile(r'(.*solvency.*)', re.IGNORECASE)
            pattern_false = re.compile(r'.*insolvency.*', re.IGNORECASE)
            filteredSolvency = [i for i in links if patSolvency.match(i)]
            filteredSolvency = [i for i in filteredSolvency if not pattern_false.match(i)]

            patKondycja = re.compile(r'(.*kondycj.*)', re.IGNORECASE)
            patFinansowa = re.compile(r'(.*finans.*)', re.IGNORECASE)
            filteredKondycja = [i for i in links if patKondycja.match(i) and patFinansowa.match(i)]

            merged_set = set(set(filteredSFCR) | set(filteredSolvency) | set(filteredKondycja))
            merged_list = list(merged_set)
        return merged_list
    else:
        strings = [
            "rewident",
            "biegl",
            "audyt",
        ]
        patterns = [re.compile(r'.*{}.*'.format(string), re.IGNORECASE) for string in strings]
        pattern_pdf = re.compile(r'\.pdf$', re.IGNORECASE)
        with open(file, 'r') as fcc_file:
            links = json.load(fcc_file)
            links = list(links.keys())
            pattern_opinia = re.compile(r'.*opini.*', re.IGNORECASE)
            pattern_badanie = re.compile(r'.*badan.*', re.IGNORECASE)
            pattern_sprawozdanie = re.compile(r'.*sprawozdan.*', re.IGNORECASE)
            opinia_badanie = set([i for i in links if pattern_opinia.match(i) and pattern_badanie.match(i)])
            opinia_sprawozdanie = set([i for i in links if pattern_opinia.match(i) and pattern_sprawozdanie.match(i)])
            badanie_sprawozdanie = set([i for i in links if pattern_badanie.match(i) and pattern_sprawozdanie.match(i)])
            filtered = [opinia_sprawozdanie, opinia_badanie, badanie_sprawozdanie]
            for pattern in patterns:
                filtered.append(set([i for i in links if pattern.match(i)]))
            merged_set = set()
            for filt in filtered:
                merged_set = merged_set | filt
            merged_list = list(merged_set)
            merged_list = [i for i in merged_list if pattern_pdf.search(i)]
        return merged_list


def find_data_files(directory):
    for file in os.listdir(directory):
        if file.startswith('data'):
            yield file


# function using find_data_files and filter_links to get all links from all files in directory
def get_links(directory, sfcr=True) -> list:
    links = []
    for file in find_data_files(directory):
        links += filter_links(os.path.join(directory, file), sfcr)
    return links


def get_link_base(link):
    return link.split('/')[2]


def get_name(link_base):
    name = link_base.split('.')[1]
    return name


def get_folder_location(dir_local, link_base):
    return os.path.join(dir_local, get_name(link_base))


def get_code_and_name(df, link_base):
    code = df[df['link'] == link_base]['kod'].values[0]
    name = get_name(link_base)
    return code, name


def check_for_dot_issues(link):
    link = link.split('/')[-1]
    if link.endswith(".pdf"):
        return link
    if link.endswith(".PDF"):
        return link
    if link.endswith("."):
        return f"{link}.pdf"
    # if link has no extension in the last 5 characters
    if "." not in link[-5:]:
        return f"{link}.pdf"
    return link


def get_filename(folder_location, filetype, code, name):
    return os.path.join(folder_location, f"{filetype}_{code}_{name}.pdf")


def download_pdf(link, filename):
    try:
        response = requests.get(link, timeout=15)
        if response.status_code == 200:
            with open(filename, 'wb') as pdf:
                pdf.write(response.content)
            return response.status_code
        else:
            print("Error: ", response.status_code)
            return response.status_code
    except Exception as e:
        print(e)
        print("Error")
        return response.status_code


def download_all_files(links, czas, filetype):
    total = time.perf_counter()
    start = time.perf_counter()
    idx = 0
    df = pd.read_csv('../scraper/zaklady.csv')
    df.columns = ['dzial', 'kod', 'zaklad', 'lei', 'link']
    for i in range(len(links)):
        link = links[idx]
        prevlink = ""
        if idx > 0:
            prevlink = links[idx - 1]

        if idx == 0 or (get_link_base(prevlink) != get_link_base(link)):
            start = time.perf_counter()

        if time.perf_counter() - start > czas:
            while get_link_base(prevlink) == get_link_base(link) and idx < len(links):
                idx += 1
                link = links[idx]
            start = time.perf_counter()

        print("total czas: ", round(time.perf_counter() - total, 2), "czas: ", round(time.perf_counter() - start, 2),
              " index: ", str(idx) + "/" + str(len(links)), ": ", link)
        try:
            response = requests.get(link, timeout=15)
            if response.status_code != 200:
                print("Error: ", response.status_code)
                idx += 1
                continue
        except Exception as ex:
            print(ex)
            idx += 1
            continue
        link_base = get_link_base(link)
        folder_location = get_folder_location(f'{os.getcwd()}/SFCR/', link_base)
        os.makedirs(folder_location, exist_ok=True)
        code, name = get_code_and_name(df, link_base)
        print("Kod zakladu: ", code)
        print("Nazwa zakladu: ", name)
        filename = get_filename(folder_location, filetype, code, name)
        print("Filename:", filename)
        status_code = 404
        if not os.path.isfile(filename):
            status_code = download_pdf(link, filename)
        if status_code != 200:
            print("Error: ", status_code)
            idx += 1
            continue
        print("Downloaded file")
        year = extract_file_year(filename)
        new_filename_base = f"{year}_{os.path.basename(filename)}"
        print("New filename base:", new_filename_base)
        new_folder = os.path.join(folder_location, year)
        os.makedirs(new_folder, exist_ok=True)
        new_filename = os.path.join(new_folder, new_filename_base)
        print("New filename:", new_filename)
        os.rename(filename, new_filename)
        print(f"Moved file from {filename} to {new_filename}")
        print("********************DOWNLOAD SUCCESSFUL***************")
        idx += 1
        if idx >= len(links):
            break


def extract_file_year(pdf_path: str) -> str:
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
