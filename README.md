# Search the Wayback Machine for Sensitive Files

## Overview

`allthewayback` is designed to facilitate the discovery of specific historical files which may contain sensitive information. With this tool, you can search for old URL paths in archived robots.txt files, configuration data in archived `.git` or `nginx.conf` files, and more.

This tool provides built-in flags for common sensitive files or allows you to specify your own search terms for the Wayback Machine. Any discovered files are output to a file of your choosing for further review.

This project is maintained by [TurvSec](https://twitter.com/TurvSec).

## Output Example

**Console Output Example:**

![allthewayback Output](/examples/ss1.png)

**Sample File Output:**

![File Output](/examples/ss2.png)

Using the output URLs, you can review and analyze any sensitive data that might be present.

## Installation

Clone the repository and set up the environment:
```
git clone https://github.com/MrTurvey/allthewayback.git
cd allthewayback
pip3 install -r requirements.txt
python allthewayback.py <flags>
```

## Usage
`allthewayback` will search a domain from the specified year(as set on [line 11](https://github.com/MrTurvey/allthewayback/blob/main/allthewayback.py#L11)) to the current year.

The examples below search the Wayback Machine for bugbounty.com archived data from the years 2023 to 2024

**To run all built in checks (-RGCSHN -Wc -Wx) and show any URLs as they are found (-v):**
```
python allthewayback.py -y <year> -d <domain> -RGCSHN -Wc -Wx -o <outfile> -v

python allthewayback.py -y 2023 -d bugbounty.com -RGCSHN -Wc -Wx -o bountyoutput.txt -v
```

**To run a single check using your own search term (-OF) and show URLs as they are found (-v):**
```
python allthewayback.py -y <year> -d <domain> -OF <SearchTerm> -o <outfile> -v

python allthewayback.py -y 2023 -d bugbounty.com -OF test.php -o bountyoutput.txt -v
```

**From the help:**

```
usage: allthewayback [-h] -d url -o output file [-y year] [-rl seconds] [-v] [-R] [-G] [-C] [-S] [-H] [-Wc] [-Wx] [-N] [-OF file name]

Search the WayBackMachine for senstive data

options:
  -h, --help      show this help message and exit
  -d url          Domain to search for (e.g google.com)
  -o output file  Output file name
  -y year         Year to start wayback searching from (Default: 2020)
  -rl seconds     Rate Limit in seconds (Default: 5)
  -v              Display URLs as they are discovered (Default: False)
  -R              Search for robots.txt files
  -G              Search for .git files
  -C              Search for config files
  -S              Search for sitemap files
  -H              Search for htaccess files
  -Wc             Search for web.config files
  -Wx             Search for WEB-INF/web.xml files
  -N              Search for Nginx config
  -OF file name   Specify your own file to search for (e.g /test.php)
```

