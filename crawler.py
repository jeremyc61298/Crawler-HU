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
ERRORMSG = 'e'


def checkForValidScheme(url):
    scheme = ''
    if len(url) >= MAXSCHEMELENGTH:
        scheme = url[0:MAXSCHEMELENGTH]
    if 'https://' in scheme or 'http://' in scheme:
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
    print('Help Dialog')

# Tuple 'result' will contain the flag that was
# extracted and the value that goes with it
def extractFlag(args, flag, index):
    result = ()

    if flag == NUMPAGESFLAG:
        result = checkForTrailingNumericParameter(args, NUMPAGESFLAG, index)
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
        elif checkForValidScheme(arg):
            urls.append(arg)
        else:
            print('Crawler: Only http or https URLs can be requested')
            success = False
            break


    if len(urls) == 0 and HELPFLAG not in flags:
        print('Crawler: Supply a URL to retrieve')
        success = False

    return (success, flags, urls)


def makeRequests(urls):
    responses = []
    for url in urls:
        try:
            print('Crawling: ' + url)
            responses.append(urllib.request.urlopen(url))
        except:
            print('-- Could not access')
    return responses

def main():
    (success, flags, urls) = extractArgs(sys.argv[1:])
    if HELPFLAG in flags: 
        printHelpDialog()
    
    makeRequests(urls)


main()