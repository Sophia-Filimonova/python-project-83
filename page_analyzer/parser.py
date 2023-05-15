from bs4 import BeautifulSoup


def get_seo_data(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
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
    return h1, title, description
