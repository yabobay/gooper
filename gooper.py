from bs4 import BeautifulSoup as bs
from re import compile as regex
import pycurl

# temp
from os import system
system('clear')

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

def punicode(string):
    return string.replace('/', '%2F')

def searchGpo(query):
    # TODO : MAKE IT SLURPY
    url = f"http://gpo.zugaina.org/Search?search={punicode(query)}"
    return parseSearchResults(curl(url))

def searchPrint(query):
    results = searchGpo(query)
    if results == {}:
        print("sorry, no results. :(")
    else:
        if args.stdout:
            for i in results.keys():
                print(i)
        else:
            for i in results.keys():
                print('\033[1m', i, '\033[0m: ', results[i], sep='')

def showGpo(query):
    url = f"http://gpo.zugaina.org/{query}"
    doc = bs(curl(url), 'html.parser')
    name = query[1+query.index('/'):]
    if doc.find(text=regex('404')):
        # TODO: try to search for a version using the packages name
        return None
    info = {
        'category': query[:query.index('/')],
        'name': name,
        'description': doc.find('h5', class_='gray').contents[0],
        'overlays': {}
    }
    ebuilds = doc.find('div', id='ebuild_list').find_all('li')
    for i in ebuilds:
        name = i.b.contents[0]
        version = name[1+name.rindex('-'):]
        overlay = i.find('a', href=regex('Overlay')).contents[0]
        if overlay not in info['overlays']:
            info['overlays'][overlay] = []
        info['overlays'][overlay].append(version)
    return info

def showPrint(query):
    package = showGpo(query)
    if package:
        import pprint
        pp = pprint.PrettyPrinter(indent=4).pprint
        pp(package)
    else:
        print("sorry, no package :(")

if __name__ == '__main__':
    from sys import argv
    import argparse
    argparser = argparse.ArgumentParser(prog = 'gooper',
                                        description = 'search gpo.zugaina.org from the terminal!')
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

    if 'query' in args: # command search
        searchPrint(args.query)
    elif 'package' in args: # command show
        showPrint(args.package)
    else:
        argparser.print_help()
