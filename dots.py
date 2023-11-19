import os

def check_for_dot_issues(link):
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


def get_all_subdirectories(directory):
    if not os.path.isdir(directory):
        return []
    subdirectories = [f.path for f in os.scandir(directory) if (f.is_dir() or f.is_file())]
    for subdir in subdirectories:
        subdirectories.extend(get_all_subdirectories(subdir))
    return subdirectories

def get_files_containing_from_dir(dir, text):
    dirs = get_all_subdirectories(dir)
    files = [f for f in dirs if text in f.lower()]
    return files
print("------------")
print(get_files_containing_from_dir("scraper", ".json"))
