# Betting odds from Tipsport.cz

Scraper and data of betting odds from betsport.com with direct update to Github.

Tested only on _politics_!

Data are structured in tabular datapackage format (http://frictionlessdata.io/guides/tabular-data-package/).

Odds for bets on **politics** are updated daily and accessible in this project.

### Example - the data of odds for Czech presidential candidates 2017
http://data.okfn.org/tools/view?url=https%3A%2F%2Fraw.githubusercontent.com%2Fmichalskop%2Fbetfair.com%2Fmaster%2Fdata%2F128255728%2Fdatapackage.json

### Custom installation
Requirements:
- Python 3
- Python packages: csv, datetime, datapackage (>=v0.8), git, lxml, re, requests, os

Copy example settings into settings and correct it for your Github account (e.g., your bot's account)

    cp settings-example.py settings.py

Note: The origin for the local git project must be 'ssh' address (not 'https' one) for bot to work.

### Automation
You can automate the data retrieval using cron. Example:

    14 3 * * * /usr/bin/python3 /home/project/tipsport.cz/scraper.py > /dev/null 2>&1
