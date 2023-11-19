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