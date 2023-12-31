import os
import requests
from bs4 import BeautifulSoup
import json
import time
import threading
import pandas as pd

df = pd.read_csv('scraper/zaklady.csv')
df.columns = ['dzial', 'kod', 'zaklad', 'lei', 'link']
# add https:// to links
df['link'] = 'https://' + df['link'].astype(str) + '/'
urls = df['link'].tolist()

url = ""
dict_href_links = {}


class Scraper:

    def __init__(self, urls):
        self.urls = urls
        self.long_list = dict()

    def getdata(self, url):
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print("it's not a good url")
                return f"error:{r.status_code}"
            else:
                return r.text
        except Exception as e:
            print("it's not a good url")
            return "error"

    def get_links(self, website_link, base_url):
        """
        param: website_link: single subpage link
        param: set_visited_links: global set of visited links
        return: set of unvisited links
        """
        html_data = self.getdata(website_link)
        if html_data == "errorXDXD":
            return

        try:
            soup = BeautifulSoup(html_data, "html.parser")
        except:
            return

        for link in soup.find_all("a", href=True):
            # Include all href that do not start with website link but with "/"
            adjusted_link = str(link["href"])
            if adjusted_link.startswith("/"):
                adjusted_link = base_url + link["href"][1:]

            if adjusted_link not in self.long_list.keys():
                if adjusted_link.startswith(base_url):
                    self.long_list[adjusted_link] = False
                else:
                    continue

    def thread_function(self, urls, id):

        for url in urls:
            self.long_list[url] = False
            # If there is no such folder, the script will create one automatically

            if not os.path.exists("download"):
                os.mkdir("download")

            folder_location = r"download/" + url[7:17:1]
            if not os.path.exists(folder_location): os.mkdir(folder_location)

            base_url = url[:url.find("/", 8) + 1]
            # dont check if link ends in .pdf
            if url.endswith(".pdf"):
                self.long_list[url] = True
                continue
            self.get_links(url, base_url)

            # count number of links that have not been checked yet
            not_checked_in_list = len(self.long_list) - sum(self.long_list.values())
            iterations = 0

            start = time.perf_counter()
            while not_checked_in_list != 0:
                iterations += 1

                # link to be checked starting with url

                # get list of links that start with url
                not_checked = {link: is_true for link, is_true in self.long_list.items() if link.startswith(url)}
                try:
                    current_link = list(not_checked.keys())[list(not_checked.values()).index(False)]
                except:
                    print("error")
                    break

                    # set current link as visited
                self.long_list[current_link] = True
                self.get_links(current_link, base_url)

                # Count number of non-values and set counter to 0 if there are no values within the dictionary equal to the string "Not-checked"
                not_checked_in_list = len(self.long_list) - sum(self.long_list.values())
                # Print some statements
                print("")
                print("CURRENT LINK =", current_link)
                print("THIS IS LOOP ITERATION NUMBER", iterations)
                print("LENGTH OF DICTIONARY WITH LINKS =", len(self.long_list))
                print("NUMBER OF 'Not-checked' LINKS = ", not_checked_in_list)
                print("")

                now = time.perf_counter()

                if (int(now - start) % 10 == 0):
                    print(f"saving to file {id}")
                    a_file = open(f"scraper/links_to_be_scraped/data{id}.json", "w")
                    json.dump(self.long_list, a_file)
                    a_file.close()
                if (now - start > 3600 / 2):
                    print("\n\n\n TIMEOUT \n\n\n")
                    break


def runner(urls, i):
    scraper = Scraper(urls)
    scraper.thread_function(urls, i)


urls_per_thread = 6

for i in range(0, len(urls), urls_per_thread):
    t = threading.Thread(target=runner, args=(urls[i:i + urls_per_thread], i))
    t.start()
