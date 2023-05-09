from bs4 import BeautifulSoup
from datetime import datetime


def parse_page(r):
    soup = BeautifulSoup(r.text, 'html.parser')
    h1, title, description = '', '', ''
    h1_tag = soup.find('h1')
    if h1_tag:
        h1 = h1_tag.text
    title_tag = soup.title
    if title_tag:
        title = title_tag.string
    description_tag = soup.find('meta', attrs={'name': 'description'})
    if description_tag:
        description = description_tag['content']
    created_at = datetime.now()
    return h1, title, description, created_at
