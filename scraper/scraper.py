import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
import time
import re

def scrape(links, czas=60):
    total = time.perf_counter()
    start = time.perf_counter()
    idx = 0
    for i in range(len(links)):
        link = links[idx]
        if 'http' not in link:
            link = 'https://' + link
        # prevlink=""
        # if idx>0:
        #     prevlink = links[idx-1]
        #
        # if(prevlink[10:15]!=link[10:15]):
        #     start=time.perf_counter()

        # if (time.perf_counter() - start > czas):
        #     while idx < len(links):
        #         idx += 1
        #         link = links[idx]
        #     start = time.perf_counter()

        # print("total czas: ", round(time.perf_counter()-total, 2), "czas: ", round(time.perf_counter() - start, 2), " index: " ,str(idx) + "/" + str(len(links)), ": ", link)
        response = requests.get(link)
        folder_location = r"download/" + link[7:17]

        os.makedirs(folder_location, exist_ok=True)

        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = soup.select("a[href$='.pdf']")
        # filter pdf_links to only include links with 'SFCR' in their name
        pdf_links = [link for link in pdf_links if 'SFCR' in link.text.upper()]

        for sublink in pdf_links:
            # Name the pdf files using the last portion of each link which are unique in this case

            filename = os.path.join(folder_location, sublink['href'].split('/')[-1])
            if not os.path.isfile(filename):
                with open(filename, 'wb') as f:
                    f.write(requests.get(urljoin(link, sublink['href'])).content)
        # idx += 1
        # if (idx >= len(links)):
        #     break


# with open('data.json', 'r') as fcc_file:
#     links = json.load(fcc_file)
def get_links(df):
    links = df['link'].tolist()
    scrape(links)

    # patKluczowe = re.compile(r'(.*kluczowe.*)', re.IGNORECASE)
    # filteredKluczowe= [i for i in links if patKluczowe.match(i)]
    #
    # patKIID = re.compile(r'(.*kiid.*)', re.IGNORECASE)
    # filteredKIID = [i for i in links if patKIID.match(i)]
    #
    # patDokumenty = re.compile(r'(.*dokumenty.*)', re.IGNORECASE)
    # filteredDokumenty = [i for i in links if patDokumenty.match(i)]
    #
    # patTfi = re.compile(r'(.*\.pl.*tfi.*)', re.IGNORECASE)
    # filteredTfi = [i for i in links if patTfi.match(i)]
    #
    # patFundusz = re.compile(r'.*fundusz.*', re.IGNORECASE)
    # filteredFundusz = [i for i in links if patFundusz.match(i)]
    #
    # patNotAllianz = re.compile(r'^((?!allianz).)*$', re.IGNORECASE)



    # zbior = set(set(filteredKluczowe) | set(filteredKIID) | set(filteredTfi) | set(filteredDokumenty) | set(filteredFundusz))
    # lista = list(zbior)
    # lista = [i for i in lista if patNotAllianz.match(i)]






