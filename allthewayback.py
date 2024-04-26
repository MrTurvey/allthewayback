import argparse
import datetime
import os
import sys
import time

import requests

parser = argparse.ArgumentParser(
    prog="allthewayback", description="Search the WayBackMachine for senstive data"
)

# Wayback base URL
WAYBACK_BASE_URL = "https://web.archive.org"


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
        default="2020",
    )
    parsed_args.add_argument(
        "-rl",
        dest="argRateLimit",
        metavar="seconds",
        help="Rate Limit in seconds (Default: 5)",
        default=5,
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
def get_archives(target_host, search, from_year, wait_time):
    """
    Parses the host and search query and directs requests against API

    Arguments:
    target_host: target domain to be searched
    search: value to be searched for
    from_year: year to start search from
    wait_time: rate limit in seconds
    """
    url = f"{WAYBACK_BASE_URL}/__wb/calendarcaptures/2?url={target_host}{search}&date={from_year}"
    this_year = datetime.date.today().year
    combined_items = {"items": []}
    print(f"[*] Getting list of {search} archives from {from_year} onwards...")
    print("[!] This will take about 5 seconds per year due to Wayback rate limits..")
    for year in range(int(from_year), this_year + 1):
        try:
            response = requests.get(url, timeout=30)
            time.sleep(wait_time)
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
                f"\n[+] Found {len(robot_archives['items'])} results dating back to {from_year}"
            )
            url_list = [
                f"{WAYBACK_BASE_URL}/web/{from_year}0{archive[0]}/{target_host}{search}"
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
    Initializes and validates command-line arguments, sets configurations.

    Arguments:
    initial_args: Namespace - runtime arguments

    Returns:
    str - The validated host domain to be used for archive searches.
    """
    if "http" in initial_args.argDomain:
        print(
            "Please enter a domain without a protocol: google.com and not https://google.com"
        )
        sys.exit()
    else:
        target_host = initial_args.argDomain
    return target_host


def file_write(write_data, verb, out_file):
    """
    Writes data to an output file specified by the runtime outfile variable. Data is appended if the file
    already exists, or a new file is created otherwise. Verbose output is shown if enabled.

    Arguments:
    writeData: list or str - The data to write. If a list, it will be joined by newlines.
    verb: bool - Toggle verbose output
    out_file: str - Target file to write to

    Returns:
    str - The path to the output file where the data was written.
    """
    mode = "a" if os.path.exists(out_file) else "w"
    with open(out_file, mode, encoding="utf-8") as f:
        if isinstance(write_data, list):
            f.write("\n".join(write_data) + "\n")
        else:
            f.write(write_data + "\n")
    if verb:
        print(f" {write_data} \n")
    return out_file


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
    from_year = run_args.argFromYear
    rate_limit = run_args.argRateLimit
    out_file = run_args.OUT_FILE
    verbose = run_args.verb
    write_check = False

    if run_args.robots:
        robot_urls = get_archives(target_host, "/robots.txt", from_year, rate_limit)
        if robot_urls:
            target_filename = file_write(robot_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No robots.txt data discovered")

    if run_args.git:
        git_urls = get_archives(target_host, "/.git", from_year, rate_limit)
        if git_urls:
            target_filename = file_write(git_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No .git data discovered")

    if run_args.config:
        conf_urls = get_archives(target_host, "/config", from_year, rate_limit)
        if conf_urls:
            target_filename = file_write(conf_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No /config data discovered")

    if run_args.sitemap:
        smap_urls = get_archives(target_host, "/sitemap.xml", from_year, rate_limit)
        if smap_urls:
            target_filename = file_write(smap_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No sitemap.xml data discovered")

    if run_args.htaccess:
        htaccess_urls = get_archives(target_host, "/.htaccess", from_year, rate_limit)
        if htaccess_urls:
            target_filename = file_write(htaccess_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No .htaccess data discovered")

    if run_args.wconf:
        wconf_urls = get_archives(target_host, "/web.config", from_year, rate_limit)
        if wconf_urls:
            print(f" {wconf_urls} \n")
            target_filename = file_write(wconf_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No web.config data discovered")

    if run_args.wxml:
        wxml_urls = get_archives(target_host, "/WEB-INF/web.xml", from_year, rate_limit)
        if wxml_urls:
            target_filename = file_write(wxml_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No web.xml data discovered")

    if run_args.nginx:
        nginx_urls = get_archives(target_host, "nginx.conf", from_year, rate_limit)
        if nginx_urls:
            target_filename = file_write(nginx_urls, verbose, out_file)
            write_check = True
        else:
            print("[!] No nginx.conf data discovered")

    if run_args.ownFile:
        s_term = run_args.ownFile
        own_urls = get_archives(target_host, s_term, from_year, rate_limit)
        if own_urls:
            target_filename = file_write(own_urls, verbose, out_file)
            write_check = True
        else:
            print(f"[!] No {s_term} data discovered\n")
    else:
        pass

    if not write_check:
        return None

    return target_filename


if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()

    # Check command, initalise params and return host to be checked
    host = initalise(args)

    # Run the searches based on given arguments
    filename = arg_worker(host, args)

    # Check if we've written to a file and if we have, present the filename
    if filename:
        print(f"[*] Saved results to {filename}")
    else:
        print("[!] Execution Finished: No data found :(")
