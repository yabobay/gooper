import pycurl
from bs4 import BeautifulSoup as bs

def curl(url):
    # this whole function is just copied from the pycurl website
    # i don't care
    import pycurl
    import certifi
    from io import BytesIO
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.CAINFO, certifi.where())
    c.perform()
    c.close()
    body = buffer.getvalue()
    return body.decode('utf-8')

def parse_search_results(html):
    document = bs(curl(url), 'html.parser')
    results = []
    for div in document.find_all('div'):
        if div.get('id') == "search_results":
            for searchResult in div.find_all('a'):
                pkg = searchResult.div.contents
                results.append([pkg[0].strip(), pkg[1].contents[0]])
            results.sort()
            return results

from sys import argv, exit

if len(argv) == 1:
    print("Please provide a search query!")
else:
    query = argv[1].replace('/', '%2F')
    url = f"http://gpo.zugaina.org/Search?search={query}"

    results = parse_search_results(curl(url))
    for i in results:
        print(': '.join(i))
