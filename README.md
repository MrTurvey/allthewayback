# Search the Wayback Machine for specific/sensitive files
## What is this project? 

allthewayback has been built to enable the quick discovery of specific historical files which may contain sensitive data. For example, you may search for old URL paths in archived robots.txt files or you may search for configuration data in archived .git or nginx.conf files. 

You can either use the built in flags to find common sensitive files or you can specify your own wayback search term.

Any discovered archived files will be output into a file of your choosing for self review.

This project is maintained by [TurvSec](https://twitter.com/TurvSec)

## Output Example 
Here's what you will see when running allthewayback:

![Alt text](/examples/ss1.png "allthewayback Output")

Here's what your output file will look like:

![Alt text](/examples/ss2.png "File Output")

You can then use the output URLs to search for any sensitive data.

## Installation
Simply git clone and you're away:
```
git clone https://github.com/MrTurvey/allthewayback.git
cd allthewayback
python allthewayback.py <flags>
```

## Usage
allthewayback will search a domain from the specified year to the current year.

The examples below search the Wayback Machine for bugbounty.com archived data from the years 2023 to 2024

<b>To run all built in checks (-RGCSHN -Wc -Wx) and show any URLs as they are found (-v):</b>
```
python allthewayback.py -y <year> -d <domain> -RGCSHN -Wc -Wx -o <outfile> -v

python allthewayback.py -y 2023 -d bugbounty.com -RGCSHN -Wc -Wx -o bountyoutput.txt -v
```

<b>To run a single check using your own search term (-OF) and show URLs as they are found (-v):</b>
```
python allthewayback.py -y <year> -d <domain> -OF <SearchTerm> -o <outfile> -v

python allthewayback.py -y 2023 -d bugbounty.com -OF test.php -o bountyoutput.txt -v
```

<b>From the help:</b>

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

