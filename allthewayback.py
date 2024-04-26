import argparse
import datetime
import os
import sys
import time

import requests

parser = argparse.ArgumentParser(
    prog="allthewayback", description="Search the WayBackMachine for senstive data"
)

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
    """
    Sets up and configures the argument parser for the command-line interface.

    Returns:
    ArgumentParser: The configured argument parser.
    """
    parsed_args = argparse.ArgumentParser(
        prog="allthewayback", description="Search the WayBackMachine for sensitive data"
    )
    parsed_args.add_argument(
        "-d",
        dest="argDomain",
        metavar="url",
        required=True,
        help="Domain to search for (e.g google.com)",
    )
    parsed_args.add_argument(
        "-o",
        dest="OUT_FILE",
        metavar="output file",
        required=True,
        help="Output file name",
    )
    parsed_args.add_argument(
        "-y",
        dest="argFromYear",
        metavar="year",
        help="Year to start wayback searching from (Default: 2020)",
    )
    parsed_args.add_argument(
        "-rl",
        dest="argRateLimit",
        metavar="seconds",
        help="Rate Limit in seconds (Default: 5)",
    )
    parsed_args.add_argument(
        "-v",
        dest="verb",
        help="Display URLs as they are discovered (Default: False)",
        action="store_true",
    )
    parsed_args.add_argument(
        "-R", dest="robots", help="Search for robots.txt files", action="store_true"
    )
    parsed_args.add_argument(
        "-G", dest="git", help="Search for .git files", action="store_true"
    )
    parsed_args.add_argument(
        "-C", dest="config", help="Search for config files", action="store_true"
    )
    parsed_args.add_argument(
        "-S", dest="sitemap", help="Search for sitemap files", action="store_true"
    )
    parsed_args.add_argument(
        "-H", dest="htaccess", help="Search for htaccess files", action="store_true"
    )
    parsed_args.add_argument(
        "-Wc", dest="wconf", help="Search for web.config files", action="store_true"
    )
    parsed_args.add_argument(
        "-Wx", dest="wxml", help="Search for WEB-INF/web.xml files", action="store_true"
    )
    parsed_args.add_argument(
        "-N", dest="nginx", help="Search for Nginx config", action="store_true"
    )
    parsed_args.add_argument(
        "-OF",
        dest="ownFile",
        metavar="file name",
        help="Specify your own file to search for (e.g /test.php)",
    )
    return parsed_args


# Get list of entries from wayback machine based on search term
def get_archives(target_host, search):
    """
    Parses the host and search query and directs requests against API

    Arguments:
    target_host: target domain to be searched
    search: value to be searched for
    """
    url = f"{WAYBACK_BASE_URL}/__wb/calendarcaptures/2?url={target_host}{search}&date={FROM_YEAR}"
    this_year = datetime.date.today().year
    combined_items = {"items": []}
    print(f"[*] Getting list of {search} archives from {FROM_YEAR} onwards...")
    print("[!] This will take about 5 seconds per year due to Wayback rate limits..")
    for year in range(int(FROM_YEAR), this_year + 1):
        try:
            response = requests.get(url, timeout=30)
            time.sleep(WAIT_TIME)
            results = response.json()
            results.pop(
                "colls", None
            )  # None as the default to handle cases where 'colls' doesn't exist
            if not results or not results["items"]:  # might find nothing
                print(f"No results were found for {year}")
            else:
                combined_items["items"].extend(results["items"])
        except Exception:
            pass

        if combined_items is None or not combined_items["items"]:  # might find nothing
            return []

        robot_archives = unpack_archives(combined_items)
        if robot_archives["items"]:
            print(
                f"\n[+] Found {len(robot_archives['items'])} results dating back to {FROM_YEAR}"
            )
            url_list = [
                f"{WAYBACK_BASE_URL}/web/{FROM_YEAR}0{archive[0]}/{target_host}{search}"
                for archive in robot_archives["items"]
            ]
            return url_list

        return []


def unpack_archives(archives):
    """
    Filters out unwanted data from waybackmachine, specifically ensuring only HTTP 200 status codes are included.

    Arguments:
    archives: dict - Contains archive entries potentially including statuses other than HTTP 200.

    Returns:
    dict - Filtered archive data with entries that only include HTTP 200 status codes.
    """
    filtered_data = {
        "items": [item[:-1] for item in archives["items"] if item[1] in (200, "-")]
    }
    return filtered_data


def initalise(initial_args):
    """
    Initializes and validates command-line arguments, sets global configurations.

    Arguments:
    initial_args: Namespace - runtime arguments

    Returns:
    str - The validated host domain to be used for archive searches.
    """
    if initial_args.argFromYear:
        global FROM_YEAR
        FROM_YEAR = initial_args.argFromYear
    if initial_args.argRateLimit:
        global WAIT_TIME
        WAIT_TIME = initial_args.argRateLimit
    if initial_args.OUT_FILE:
        global OUT_FILE
        OUT_FILE = initial_args.OUT_FILE
    if "http" in initial_args.argDomain:
        print(
            "Please enter a domain without a protocol: google.com and not https://google.com"
        )
        sys.exit()
    else:
        target_host = initial_args.argDomain
    return target_host


def file_write(write_data, verb):
    """
    Writes data to an output file specified by the OUT_FILE global variable. Data is appended if the file
    already exists, or a new file is created otherwise. Verbose output is shown if enabled.

    Arguments:
    writeData: list or str - The data to write. If a list, it will be joined by newlines.
    verb: bool - Toggle verbose output

    Returns:
    str - The path to the output file where the data was written.
    """
    mode = "a" if os.path.exists(OUT_FILE) else "w"
    global WRITE_CHECK
    WRITE_CHECK = True
    with open(OUT_FILE, mode, encoding="utf-8") as f:
        if isinstance(write_data, list):
            f.write("\n".join(write_data) + "\n")
        else:
            f.write(write_data + "\n")
    if verb:
        print(f" {write_data} \n")
    return OUT_FILE


def arg_worker(target_host, run_args):
    """
    Processes various command-line flags to perform archive searches and writes found URLs to a file.
    Logs messages when specific file types are not found in the archives.

    Arguments:
    target_host: str - The domain name to search archives for.
    run_args: Namespace - Arguments passed at runtime

    Returns:
    str or None - The filename where URLs were written, or None if no data was written.
    """
    if run_args.robots:
        robot_urls = get_archives(target_host, "/robots.txt")
        if robot_urls:
            target_filename = file_write(robot_urls, run_args.verb)
        else:
            print("[!] No robots.txt data discovered")
    if run_args.git:
        git_urls = get_archives(target_host, "/.git")
        if git_urls:
            target_filename = file_write(git_urls, run_args.verb)
        else:
            print("[!] No .git data discovered")
    if run_args.config:
        conf_urls = get_archives(target_host, "/config")
        if conf_urls:
            target_filename = file_write(conf_urls, run_args.verb)
        else:
            print("[!] No /config data discovered")
    if run_args.sitemap:
        smap_urls = get_archives(target_host, "/sitemap.xml")
        if smap_urls:
            target_filename = file_write(smap_urls, run_args.verb)
        else:
            print("[!] No sitemap.xml data discovered")
    if run_args.htaccess:
        htaccess_urls = get_archives(target_host, "/.htaccess")
        if htaccess_urls:
            target_filename = file_write(htaccess_urls, run_args.verb)
        else:
            print("[!] No .htaccess data discovered")
    if run_args.wconf:
        wconf_urls = get_archives(target_host, "/web.config")
        if wconf_urls:
            print(f" {wconf_urls} \n")
            target_filename = file_write(wconf_urls, run_args.verb)
        else:
            print("[!] No web.config data discovered")
    if run_args.wxml:
        wxml_urls = get_archives(target_host, "/WEB-INF/web.xml")
        if wxml_urls:
            target_filename = file_write(wxml_urls, run_args.verb)
        else:
            print("[!] No web.xml data discovered")
    if run_args.nginx:
        nginx_urls = get_archives(target_host, "nginx.conf")
        if nginx_urls:
            target_filename = file_write(nginx_urls, run_args.verb)
        else:
            print("[!] No nginx.conf data discovered")
    if run_args.ownFile:
        s_term = run_args.ownFile
        own_urls = get_archives(target_host, s_term)
        if own_urls:
            target_filename = file_write(own_urls, run_args.verb)
        else:
            print(f"[!] No {s_term} data discovered\n")
    else:
        pass
    if not WRITE_CHECK:
        target_filename = None
    return target_filename


if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Check command, initalise params and return host to be checked
    host = initalise(args)

    # Run the searches based on given arguments
    filename = arg_worker(host, args)

    # Check if we've written to a file  and if we have, present the filename
    if WRITE_CHECK:
        print(f"[*] Saved results to {filename}")
    else:
        print("[!] Execution Finished: No data found :(")
