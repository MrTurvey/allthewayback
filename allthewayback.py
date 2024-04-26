import requests
import re
import sys
import time
import datetime
import os
import argparse
parser = argparse.ArgumentParser(prog='allthewayback', description='Search the WayBackMachine for senstive data')

# Default search from year, change with -y flag
FROM_YEAR = "2020"
# Wayback base URL
WAYBACK_BASE_URL = "https://web.archive.org"
# Wayback Rate Limit in seconds
WAIT_TIME = 5
# Check for written data during execution
WRITE_CHECK = False

# cmd arguments
def setup_arg_parser():
    '''
    Sets up and configures the argument parser for the command-line interface.

    Returns:
    ArgumentParser: The configured argument parser.
    '''
    parser = argparse.ArgumentParser(prog='allthewayback', description='Search the WayBackMachine for sensitive data')
    parser.add_argument("-d", dest="argDomain", metavar="url", required=True, help="Domain to search for (e.g google.com)")
    parser.add_argument("-o", dest="OUT_FILE", metavar="output file", required=True, help="Output file name")
    parser.add_argument("-y", dest="argFromYear", metavar="year", help="Year to start wayback searching from (Default: 2020)")
    parser.add_argument("-rl", dest="argRateLimit", metavar="seconds", help="Rate Limit in seconds (Default: 5)")
    parser.add_argument("-v", dest="verb", help="Display URLs as they are discovered (Default: False)", action='store_true')
    parser.add_argument("-R", dest="robots", help="Search for robots.txt files", action='store_true')
    parser.add_argument("-G", dest="git", help="Search for .git files", action='store_true')
    parser.add_argument("-C", dest="config", help="Search for config files", action='store_true')
    parser.add_argument("-S", dest="sitemap", help="Search for sitemap files", action='store_true')
    parser.add_argument("-H", dest="htaccess", help="Search for htaccess files", action='store_true')
    parser.add_argument("-Wc", dest="wconf", help="Search for web.config files", action='store_true')
    parser.add_argument("-Wx", dest="wxml", help="Search for WEB-INF/web.xml files", action='store_true')
    parser.add_argument("-N", dest="nginx", help="Search for Nginx config", action='store_true')
    parser.add_argument("-OF", dest="ownFile", metavar="file name", help="Specify your own file to search for (e.g /test.php)")
    return parser

# Get list of entries from wayback machine based on search term      
def getArchives(host, search):
    '''
    Parses the host and search query and directs requests against API

    Arguments:
    host: target domain to be searched
    search: value to be searched for"  
    '''
    url = f"{WAYBACK_BASE_URL}/__wb/calendarcaptures/2?url={host}{search}&date={FROM_YEAR}"
    print(url)
    thisYear = datetime.date.today().year
    combinedItems = {'items': []}
    print(f"[*] Getting list of {search} archives from {FROM_YEAR} onwards...")
    print(f'[!] This will take about 5 seconds per year due to Wayback rate limits..')
    for year in range(int(FROM_YEAR), thisYear + 1):
        try:
            response = requests.get(url)
            time.sleep(WAIT_TIME)
            results = response.json()
            results.pop('colls', None)  # None as the default to handle cases where 'colls' doesn't exist
            if results == None or len(results['items']) == 0:  # might find nothing
                print(f"No results were found for {year}")
            else:
                combinedItems['items'].extend(results['items'])
        except Exception as e:
            pass
        if combinedItems == None or len(combinedItems['items']) == 0:  # might find nothing
            return []
        else:
            robotArchives = unpackArchives(combinedItems)
            if  len(robotArchives['items']) != 0:
                print(f"\n[+] Found {len(robotArchives['items'])} results dating back to {FROM_YEAR}")
                url_list = []
                for archive in robotArchives['items']:
                    url = f'{WAYBACK_BASE_URL}/web/{FROM_YEAR}0{archive[0]}/{host}{search}'
                    url_list.append(url)
                return url_list
            else:
                return []        

def unpackArchives(archives):
    '''
    Filters out unwanted data from waybackmachine, specifically ensuring only HTTP 200 status codes are included.
    
    Arguments:
    archives: dict - Contains archive entries potentially including statuses other than HTTP 200.
    
    Returns:
    dict - Filtered archive data with entries that only include HTTP 200 status codes.
    '''
    filtered_data = {'items': [item[:-1] for item in archives['items'] if item[1] in (200, '-')]}
    return filtered_data


def initalise():  
    '''
    Initializes and validates command-line arguments, sets global configurations.
    
    Returns:
    str - The validated host domain to be used for archive searches.
    '''
    if args.argFromYear:
        global FROM_YEAR 
        FROM_YEAR = args.argFromYear
    if args.argRateLimit:
       global WAIT_TIME
       WAIT_TIME = args.argRateLimit
    if args.OUT_FILE:
        global OUT_FILE
        OUT_FILE = args.OUT_FILE
    if "http" in args.argDomain:
        print("Please enter a domain without a protocol: google.com and not https://google.com")
        sys.exit()
    else:
        host = args.argDomain
    return host


def fileWrite(writeData):
    '''
    Writes data to an output file specified by the OUT_FILE global variable. Data is appended if the file
    already exists, or a new file is created otherwise. Verbose output is shown if enabled.

    Arguments:
    writeData: list or str - The data to write. If a list, it will be joined by newlines.

    Returns:
    str - The path to the output file where the data was written.
    '''
    mode = 'a' if os.path.exists(OUT_FILE) else 'w'
    global WRITE_CHECK
    WRITE_CHECK = True
    with open(OUT_FILE, mode) as f:
        if isinstance(writeData, list):
            f.write('\n'.join(writeData) + '\n')
        else:
            f.write(writeData + '\n')
    if args.verb == True:
        print(f" {writeData} \n")
    return OUT_FILE


def argWorker(host):
    '''
    Processes various command-line flags to perform archive searches and writes found URLs to a file.
    Logs messages when specific file types are not found in the archives.

    Arguments:
    host: str - The domain name to search archives for.

    Returns:
    str or None - The filename where URLs were written, or None if no data was written.
    '''
    if args.robots:
        robotUrls = getArchives(host, '/robots.txt')
        if robotUrls:
            filename = fileWrite(robotUrls)
        else:
            print("[!] No robots.txt data discovered")
    if args.git:
        gitUrls = getArchives(host, '/.git')
        if gitUrls:
            filename = fileWrite(gitUrls)
        else:
            print("[!] No .git data discovered")
    if args.config:
        confUrls = getArchives(host, '/config')
        if confUrls:
            filename = fileWrite(confUrls)
        else:
            print("[!] No /config data discovered")
    if args.sitemap:
        smapUrls = getArchives(host, '/sitemap.xml')
        if smapUrls:
            filename = fileWrite(smapUrls)
        else:
            print("[!] No sitemap.xml data discovered")
    if args.htaccess:
        htaccessUrls = getArchives(host, '/.htaccess')
        if htaccessUrls:
            filename = fileWrite(htaccessUrls)
        else:
            print("[!] No .htaccess data discovered")
    if args.wconf:
        wconfUrls = getArchives(host, '/web.config')
        if wconfUrls:
            print(f" {wconfUrls} \n")
            filename = fileWrite(wconfUrls)
        else:
            print("[!] No web.config data discovered")
    if args.wxml:
        wxmlUrls = getArchives(host, '/WEB-INF/web.xml')
        if wxmlUrls:
            filename = fileWrite(wxmlUrls)
        else:
            print("[!] No web.xml data discovered")
    if args.nginx:
        nginxUrls = getArchives(host, 'nginx.conf')
        if nginxUrls:
            filename = fileWrite(nginxUrls)
        else:
            print("[!] No nginx.conf data discovered")
    if args.ownFile:
        sTerm = args.ownFile
        ownUrls = getArchives(host, sTerm)
        if ownUrls:
            filename = fileWrite(ownUrls)
        else:
            print(f"[!] No {sTerm} data discovered\n")
    else:
        pass
    if WRITE_CHECK != True:
        filename = None
    return filename

if __name__ == '__main__':
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    # Check command, initalise params and return host to be checked 
    host = initalise()
    
    # Run the searches based on given arguments
    filename = argWorker(host)

    # Check if we've written to a file  and if we have, present the filename
    if WRITE_CHECK == True:
        print(f'[*] Saved results to {filename}')
    else:
        print("[!] Execution Finished: No data found :(")