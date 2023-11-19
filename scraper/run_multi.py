
import requests
from bs4 import BeautifulSoup
import time
import os
import threading

from scraper import scrape

def get_links(df):
    links = df['link'].tolist()
    scrape(links)

# run scrape function using threading library - provide different links to each thread
def run_multi(df, skipped_links = []):
    links = df['link'].tolist()
    threads = []
    for i in range(0, len(links), 20):
        t = threading.Thread(target=scrape, args=(links[i:i+10],))
        threads.append(t)
        t.start()

# run scrape function using multiprocessing library - provide different links to each process
# def run_multi(df):
#     links = df['link'].tolist()
#     processes = []
#     for i in range(0, len(links), 10):
#         p = multiprocessing.Process(target=scrape, args=(links[i:i+10],))
#         processes.append(p)
#         p.start()


