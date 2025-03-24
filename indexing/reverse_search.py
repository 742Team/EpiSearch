from db.firebase import getPageByContent

def reverse_search(content):
    results = getPageByContent(content)
    return results
