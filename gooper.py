import pycurl
from bs4 import BeautifulSoup as bs

def curl(url):
    # this whole function is just copied from the pycurl website
    # i don't care about it. TODO: why is it so slow though?
    import pycurl, certifi
    from io import BytesIO
    buffer = BytesIO(); c = pycurl.Curl(); c.setopt(c.URL, url);
    c.setopt(c.WRITEDATA, buffer);
    c.setopt(c.CAINFO, certifi.where()); c.perform(); c.close();
    body = buffer.getvalue();
    return body.decode('utf-8')

def parseSearchResults(html): # TODO rename to camelCase
    document = bs(html, 'html.parser')
    results = {}
    for div in document.find_all('div'):
        if div.get('id') == "search_results":
            for searchResult in div.find_all('a'):
                pkg = searchResult.div.contents
                results[pkg[0].strip()] = pkg[1].contents[0]
            # results.sort()
            return results

def searchGpo(query):
    # TODO : MAKE IT SLURPY
    query = query.replace('/', '%2F')
    url = f"http://gpo.zugaina.org/Search?search={query}"
    return parseSearchResults(curl(url))

if __name__ == '__main__':
    import argparse
    argparser = argparse.ArgumentParser(prog = 'gooper')
    subparsers = argparser.add_subparsers()

    searchParser = subparsers.add_parser('search',
    help='search for a package')
    searchParser.add_argument('query')
    searchParser.add_argument('--stdout', action='store_true',
    help='only output ebuild names')

    showParser = subparsers.add_parser('show',
    help='show info about a package')
    showParser.add_argument('package')

    args = argparser.parse_args()

    if 'query' in args: # if we're in search mode:
        results = searchGpo(args.query)
        if len(results) == 0:
            print("sorry, no results. :(")
        else:
            if args.stdout:
                for i in results.keys():
                    print(i)
            else:
                for i in results.keys():
                    print('\033[1m', i, '\033[0m: ', results[i], sep='')
