import os
import requests
import json
import time
import pandas as pd
import re


def filter_links(file, sfcr=True):
    if sfcr:
        print("File:", file)
        with open(file, 'r') as fcc_file:
            links = json.load(fcc_file)
            links = list(links.keys())
            print(len(links))
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
            "badani",
            "rewident",
            "biegl",
            "audytor",
        ]
        patterns = [re.compile(r'.*{}.*'.format(string), re.IGNORECASE) for string in strings]
        # print("Patterns:", patterns)
        with open(file, 'r') as fcc_file:
            links = json.load(fcc_file)
            links = list(links.keys())
            # print(len(links))
            filtered = []
            for pattern in patterns:
                filtered.append(set([i for i in links if pattern.match(i)]))
            print(len(filtered))
            merged_set = set()
            for filt in filtered:
                merged_set = merged_set | filt
            merged_list = list(merged_set)
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
    print("Splitting link:", link)
    return link.split('/')[2]


def get_folder_location(dir_local, link_base, link):
    return os.path.join(dir_local, link_base, link)


def get_code_and_name(df, link_base):
    code = df[df['link'] == link_base]['lei'].values[0]
    name = df[df['link'] == link_base]['zaklad'].values[0]
    name = name.replace(' ', '_')
    name = name.replace('.', '')
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


def get_filename(folder_location, filetype, code, name, link):
    return os.path.join(folder_location, f"{filetype}_{code}_{name}__{check_for_dot_issues(link)}")


def download_pdf(link, filename):
    try:
        response = requests.get(link, timeout=15)
        if response.status_code == 200:
            with open(filename, 'wb') as pdf:
                pdf.write(response.content)
        else:
            print("Error: ", response.status_code)
    except Exception as e:
        print(e)
        print("Error status code")


def download_all_files(links, czas, filetype):
    total = time.perf_counter()
    start = time.perf_counter()
    idx = 0
    print(os.getcwd())
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
        print("Link base:", link_base)
        # get link without the part after the last '/' sign
        link_stripped = link[:link.rfind('/')]
        print("Link stripped:", link_stripped)
        folder_location = get_folder_location(f'{os.getcwd()}/SFCR/', link_base, link_stripped)
        os.makedirs(folder_location, exist_ok=True)
        code, name = get_code_and_name(df, link_base)
        print("Kod zakladu: ", code)
        print("Nazwa zakladu: ", name)
        filename = get_filename(folder_location, filetype, code, name, link)
        print("Link to be used:", link)
        print("Filename:", filename)
        if not os.path.isfile(filename):
            download_pdf(link, filename)
        print("********************ESSSAAAAA***************")
        idx += 1
        if idx >= len(links):
            break
