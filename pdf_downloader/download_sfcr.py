import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import time
import re
import pandas as pd


def f(links, czas):
    total = time.perf_counter()
    start = time.perf_counter()
    idx = 0
    for i in range(len(links)):
        link = links[idx]
        prevlink = ""
        if idx > 0:
            prevlink = links[idx - 1]

        if prevlink[10:15] != link[10:15]:
            start = time.perf_counter()

        if time.perf_counter() - start > czas:
            while prevlink[10:15] == link[10:15] and idx < len(links):
                idx += 1
                link = links[idx]
            start = time.perf_counter()

        print("total czas: ", round(time.perf_counter() - total, 2), "czas: ", round(time.perf_counter() - start, 2),
              " index: ", str(idx) + "/" + str(len(links)), ": ", link)
        response = requests.get(link, timeout=15)
        if response.status_code != 200:
            print("Error: ", response.status_code)
            idx += 1
            continue
        # get folder name from link - get domain name
        link_base = link.split('/')[2]
        print("Link base:",link_base)
        folder_location = r"SFCR_data/" + link_base

        os.makedirs(folder_location, exist_ok=True)
        df = pd.read_csv('../zaklady.csv')
        df.columns = ['dzial', 'kod', 'zaklad', 'lei', 'link']
        code = df[df['link'] == link_base]['lei'].values[0]
        name = df[df['link'] == link_base]['zaklad'].values[0]
        name = name.replace(' ', '_')
        name = name.replace('.', '')
        print("Kod zakladu: ", code)
        print("Nazwa zakladu: ", name)
        filename = os.path.join(folder_location, f"SFCR_{code}_{name}_{hash(link)}.pdf")
        print("Link to be used:", link)
        print("Filename:", filename)
        if not os.path.isfile(filename):
            try:
                response = requests.get(link, timeout=15)
            except Exception as e:
                print(e)
                print("Error: ", response.status_code)
                continue
            if response.status_code == 200:
                with open(filename, 'wb') as pdf:
                    print("WRITUJE")
                    pdf.write(response.content)
            else:
                print("Error: ", response.status_code)

        print("********************ESSSAAAAA***************")
        idx += 1
        if idx >= len(links):
            break

for file in os.listdir(os.getcwd()):
    if file.startswith('data'):
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

            try:
                f(merged_list, 120)
            except Exception as e:
                print(e)
                print("cos poszlo nie tak")

