import os
import re
from download_utils import (
    get_links,
    download_all_files
)

if __name__ == '__main__':
    filtered_links = get_links(os.getcwd(), False)
    print(f"Found {len(filtered_links)} links")
    try:
        download_all_files(filtered_links, 120, 'AUDIT')
    except Exception as e:
        print(e)
        print("cos poszlo nie tak")
