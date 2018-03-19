from metaphor.settings import BASE_DIR
from bs4 import BeautifulSoup
import requests

urls = ['http://www.talkenglish.com/vocabulary/top-1500-nouns.aspx',
        'http://www.talkenglish.com/vocabulary/top-500-adjectives.aspx']

for url in urls:
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        html_soup = BeautifulSoup(response.text, 'html.parser')
        table = html_soup.find("table", {"id": "GridView3"})
