# crawler.py
# Jeremy Campbell
# A simple web crawler which will crawl pages
# with the same hostname.
import sys
import urllib.request

MAXSCHEMELENGTH = 8
NUMPAGESFLAG = 'n'
RECURSIVEFLAG = 'r'
WAITFLAG = 'w'
HELPFLAG = 'h'


def checkForValidScheme(url):
    scheme = ''
    if len(url) >= MAXSCHEMELENGTH:
        scheme = url[0:MAXSCHEMELENGTH]
    if 'https://' in scheme or 'http://' in scheme:
        return True
    return False


def consumeFlag(flag, index=None):
    if flag == NUMPAGESFLAG:
        # TODO: Num pages workflow
        print('num pages workflow')
    elif flag == RECURSIVEFLAG:
        # TODO: Recursive workflow
        print('recursive workflow')
    elif flag == WAITFLAG:
        # TODO: Wait workflow
        print('wait workflow')
    elif flag == HELPFLAG:
        # TODO: Display help dialog
        print('help workflow')
    else:
        return 'Crawler: Unsupported flag {flag}. Use "-{help}" for more information'.format(
            flag, HELPFLAG)


def extractArgs(argv):
    errMsg = ''
    option = None
    urls = []

    # Learned to use enumerate from here:
    # https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/
    for i, arg in enumerate(argv):
        if arg[0] == '-' and len(arg) > 1:
            errMsg = consumeFlag(arg[1], i)
        elif checkForValidScheme(arg):
            urls.append(arg)
        else:
            errMsg = 'Crawler: Only http or https URLs can be requested'

    if len(urls) == 0:
        errMsg = 'Crawler: Supply a URL to retrieve'

    return (errMsg, option, urls)


def makeRequests(urls):
    responses = []
    for url in urls:
        try:
            print('Crawling: ' + url)
            responses.append(urllib.request.urlopen(url))
        except:
            print('-- Could not access')
    return responses
