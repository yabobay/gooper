from bs4 import BeautifulSoup as bs
from re import compile as regex
import pycurl

def punicode(string):
    # todo: replace with some library? that probably exists.
    return string.replace('/', '%2F')

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
    div = document.find('div', id='search_results')
    for searchResult in div.find_all('a'):
        pkg = searchResult.div.contents
        results[pkg[0].strip()] = pkg[1].contents[0]
    # results.sort()
    return results

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

def findPkgFromUnclearName(s):
    results = searchGpo(s)
    matches = []
    for result in results.keys():
        name = result[result.index('/')+1:]
        category = result[:result.index('/')]
        # don't include things from acct-user or acct-group or virtual!
        if name == s and category not in ('acct-user', 'acct-group', 'virtual'):
            matches.append(result)
    # returns a list so that a user of this function can choose what
    # to do in the case of multiple matches: display all of them,
    # error out and fail, or display the first one.
    return matches

def showGpo(string):
    matches = findPkgFromUnclearName(string)
    infos = []
    for query in matches:
        url = f"http://gpo.zugaina.org/{query}"
        doc = bs(curl(url), 'html.parser')
        name = query[1+query.index('/'):]
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
        infos.append(info)
    return infos

def showPrint(query):
    package = showGpo(query)
    if len(package) > 1:
        print("sorry, more than one packages match your query! :(",
              "did you mean:",
              *['\t' + x['category'] + '/' + x['name'] for x in package],
              sep='\n')
    elif package:
        import pprint
        pp = pprint.PrettyPrinter(indent=4).pprint
        pp(package[0])
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
