from bs4 import BeautifulSoup

def remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")

    for data in soup(['style', 'script']):
        data.decompose()

    return ' '.join(soup.stripped_strings)