import requests, os
from bs4 import BeautifulSoup

import re

def extract_subdomains(page, links):
    # Construct the regex pattern
    regex_pattern = r'^www\.[a-zA-Z0-9_-]+\.page\.com$'
    regex = re.compile(regex_pattern)

    # Extract subdomains
    subdomains = set()
    
    for link in links:
        match = regex.match(link)
        if match:
            subdomain = match.group(0)
            subdomains.add(subdomain)

    return subdomains

def get_all_sublinks(links, is_link_checked, time_limit=60, it=0):
    # get all sublinks from a given link
    for link in links:
    #     if is_link_checked[link]:
    #         print("Link already checked: " + link)
    #         return {}
        

        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        sublinks = soup.select("a[href]")
        sublinks = [link['href'] for link in sublinks]
        # if link[-1] != '/':
        #     link += '/'

        subdomains = extract_subdomains(link, sublinks)
        sublinks = set(f"{link}{sublink}" for sublink in sublinks if (len(sublink)!=0 and sublink[0] == '/'))
        # print(sublinks)

        sublinks_subdomains = sublinks | subdomains


        

        temp_dict = dict.fromkeys(sublinks, False)
        is_link_checked[link] =  True
        print(it)
        print(sum(is_link_checked.values()), len(is_link_checked))
        is_link_checked = {**is_link_checked, **temp_dict}
        print(sum(is_link_checked.values()), len(is_link_checked), "\n")
        if it == 2:
            return is_link_checked


        for sublink in sublinks_subdomains:
            # print(link, sublink)
            if is_link_checked[sublink] == False:
                is_link_checked[sublink] = True
                get_all_sublinks([sublink], is_link_checked, it=it)

        return is_link_checked
        

    
    