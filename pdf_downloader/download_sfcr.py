import os
import re
from download_utils import (
    get_links,
    download_all_files
)

if __name__ == '__main__':
    filtered_links = get_links(os.getcwd())
    print(f"Found {len(filtered_links)} links")
    try:
        download_all_files(filtered_links, 120, 'SFCR')
    except Exception as e:
        # get stack trace
        print(e)
        print("Error while downloading files.")
