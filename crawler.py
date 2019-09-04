# crawler.py
# Jeremy Campbell
# A simple web crawler which will crawl pages
# with the same hostname.
import sys
import os
import time
import hashlib
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

MAXSCHEMELENGTH = 8
DEFAULTSLEEPTIME = 2
PAGELIMITFLAG = 'n'
RECURSIVEFLAG = 'r'
WAITFLAG = 'w'
HELPFLAG = 'h'
ERRORMSG = 'e'
HTMLTYPE = 'text/html'
USERAGENT = 'WebSci Crawler'

# Resources used: 
# https://stackoverflow.com/a/9626596 - urlparse
def checkForValidScheme(url):
    parsedUrl = urlparse(url)
    if parsedUrl.scheme == 'https' or parsedUrl.scheme == 'http':
        return True
    return False

def checkForTrailingNumericParameter(args, flag, index):
    result = ()

    if len(args) >= index + 1:
        num = args[index + 1]
        if num.isnumeric():
            result = (flag, int(num))
        else:
            print('Use a numeric value for the "-{}" argument.'.format(flag))
    else:
        print('Missing parameter for "-{flag}" argument. Use "-{help}" for information.'.format(flag=flag, help=HELPFLAG))

    return result


def printHelpDialog():
    spaces = 10
    print('Crawler-HU\nAuthor: Jeremy Campbell')
    print(f'Usage: python crawler.py [option] ... [url]')
    print('Options:')
    print(f'-{PAGELIMITFLAG} num'.ljust(spaces), f': Crawl "num" number of pages, then terminate. Must be used in conjuction with -{RECURSIVEFLAG}.')
    print(f'-{RECURSIVEFLAG}'.ljust(spaces), f': Turn on recursive retrieving, which follows links in discovered web pages.')
    print(f'-{WAITFLAG} seconds'.ljust(spaces), f': Wait for the given number of seconds before requesting the next URL. The default amount is {DEFAULTSLEEPTIME} seconds.')
    print(f'-{HELPFLAG}'.ljust(spaces), ': Displays this help message.')

# Tuple 'result' will contain the flag that was
# extracted and the value that goes with it
def extractFlag(args, flag, index):
    result = ()

    if flag == PAGELIMITFLAG:
        result = checkForTrailingNumericParameter(args, PAGELIMITFLAG, index)
    elif flag == RECURSIVEFLAG:
        result = (RECURSIVEFLAG, True)
    elif flag == WAITFLAG:
        result = checkForTrailingNumericParameter(args, WAITFLAG, index)
    elif flag == HELPFLAG:
        result = (HELPFLAG, True)
    else:
        print('Crawler: Unsupported flag {flag}. Use "-{help}" for more information'.format(
            flag, HELPFLAG))

    return result

# Returns a tuple of (success, flags, urls)
# success:  Bool determining whether the needed arguments 
#           were extracted correctly and program execution 
#           can continue.
# flags:    Dictionary of extracted flags and their associated
#           values
# urls:     List of urls to crawl   
def extractArgs(args):
    success = True
    urls = []
    flags = {}

    # Learned to use enumerate from here:
    # https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/
    for i, arg in enumerate(args):
        if arg[0] == '-' and len(arg) > 1:
            flag = extractFlag(args, arg[1], i)
            if len(flag) == 2:
                flags[flag[0]] = flag[1]
        elif arg.isnumeric():
            # Skip this case, as the number has already been extracted
            continue 
        else:
            urls.append(arg)
            if not checkForValidScheme(arg):
                print('Crawler: Only http or https URLs can be requested')
                success = False
                break
            

    if len(urls) == 0 and HELPFLAG not in flags:
        print('Crawler: Supply a URL to retrieve')
        success = False

    return (success, flags, urls)

# Resources used:
# https://stackoverflow.com/a/29546832
def makeRequest(url):
    try:
        print('Crawling: ' + url)
        return urlopen(Request(url, headers={'User-Agent': USERAGENT}))
    except:
        print('-- Could not access')
        return None

# Resources used: 
# https://stackabuse.com/creating-and-deleting-directories-with-python/
# https://tecadmin.net/python-check-file-directory-exists/
def makeDirectoryIfNotExists(dirname):
    if len(dirname) == 0:
         return False

    # Build new directory string. If there is not a leading
    # on 'dirname', add one. 
    newdir = os.getcwd() + ('\\' if (dirname[0] != '\\') else '') + dirname

    if not os.path.exists(newdir):
        os.mkdir(newdir)
        return True
    return False

def sleep(flags):
    if WAITFLAG in flags:
        time.sleep(flags[WAITFLAG])
    else:
        time.sleep(DEFAULTSLEEPTIME)

# Resources used: 
# https://docs.python.org/3/tutorial/inputoutput.html
# https://stackoverflow.com/a/52706404  
def savePageToFile(url, headers, body):
    filename = 'pages/' + hashlib.md5(url.encode()).hexdigest() + '.html'
    file = open(filename, 'w', encoding='utf-8')
    file.write(url + '\n')
    file.write(headers)
    file.write(body)
    file.close()
    print('-- Saved to ' + filename)
    return filename

def crawl(initialUrls, flags):
    frontier = initialUrls[:]
    visited = set()
    discovered = []        
    numPagesCrawled = 0
    recurse = RECURSIVEFLAG in flags

    # There is only a limit if the recursive and page limit flags are set
    limit = None
    if (recurse and PAGELIMITFLAG in flags):
        limit = flags[PAGELIMITFLAG]

    for url in frontier:
        # Check if the limit has been reached
        if limit != None and numPagesCrawled == flags[PAGELIMITFLAG]:
            print('Limit ' + str(limit) + ' reached')
            return

        visited.add(url)
        response = makeRequest(url)
  
        if response != None:
            headers = response.info()
            mimeType = headers.get_content_type()
            
            if mimeType != HTMLTYPE:
                print('-- Skipping ' + mimeType + 'content')
            else:
                fetchedUrl = response.geturl()
                body = str(response.read(), encoding='utf8')

                savePageToFile(fetchedUrl, str(headers), body)

                if recurse: 
                    discovered.clear()
                    soup = BeautifulSoup(body, 'html.parser')
                    links = []
                    for link in soup('a'):
                        links.append(link.get('href'))

                    for link in links:
                        if (link not in frontier) and (link not in discovered) and (link not in visited):
                            discovered.append(link)
                    
                    # Append unique links that were found in the page into the frontier
                    frontier += discovered
        
        numPagesCrawled += 1

        # Skip sleeping if this is the last page to crawl
        if numPagesCrawled != limit and numPagesCrawled != len(frontier): 
            sleep(flags)

def main():
    (success, flags, urls) = extractArgs(sys.argv[1:])

    if HELPFLAG in flags: 
        printHelpDialog()
    
    if not success:
        # Crawler should not be run
        exit(-1)

    makeDirectoryIfNotExists('pages')
    crawl(urls, flags)
    
main()