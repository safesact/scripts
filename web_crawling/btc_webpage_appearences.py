from urllib.request import urlopen
from bs4 import BeautifulSoup

def find_btc_webpage_appearances(btc_address):
    search_url = "https://www.bitcoinwhoswho.com/address/" + btc_address

    f = urlopen(search_url)
    raw_content = f.read()

    soup = BeautifulSoup(raw_content, 'html.parser')
    website_appearances_raw = soup.find_all('div', id="url_bitcoin_found_table")

    webpage_appearances = []

    if(len(website_appearances_raw) != 0):
        website_appearances_raw_html = website_appearances_raw[0]
        # print(website_appearances_raw_html)
        for link in website_appearances_raw_html.find_all('a', href = True):
            webpage_appearances.append(link['href'])

    return webpage_appearances