# UFC Data scraper

A set of scripts to pull data from wikipedia's ufc 
roster and ufcstats.com

There are two directories: 1) one for pulling 
`.csv` or `.json` data from wikipedia, and 2) 
another for pulling `.csv` or `.json` data from 
ufcstats.com

There is also a main script called 
`wikiToUFCToJSON.py` to fetch the active roster from 
wikipedia and then fill in stats and fight history 
from ufcstats.com. This way seems more efficient 
than saving 5000+ fighters from ufcstats directly.

***Disclaimer: This is for educational and non-commercial purposes 
and projects. I tried to space out requests to not spam their server...***

## Example json output (complete data [here](https://raw.githubusercontent.com/tmprk/ufc-data-scrape/main/data/data_2023-01-16_06-03-35.json))

<p align="center">
  <img src="../main/images/data_example.png" width="300"/>
</p>

## Installation

First get your api keys for scraperapi, zenrows, 
or scraperbox, which have 1000-5000 free requests per 
month. Insert that at the top of the script, or in 
an .env file.

```bash
mkvirtualenv webscraping
cd ufc-data-scraper
pip install -r requirements.txt
```

## Usage

```python
python [script.py]
```
* Data will be located in `./data/`
* You can import PyMongo to send data directly to 
your atlas database. It's commented right now, but 
just uncomment it and insert your MONGO_URI

## Improvements

- Pull data from UFC.com/athletes/all directly.
- Run this as a cron job using anything you want
  - Some free options: [Github Actions](https://canovasjm.netlify.app/2020/11/29/github-actions-run-a-python-script-on-schedule-and-commit-changes/), [PythonAnywhere](https://www.pythonanywhere.com/), [Fly.io](https://fly.io/)
- Instead of splitting this into many scripts, we 
could allow for CLI options to specify whether a 
user wants basic or detailed data, and `.csv` or 
`.json` output.
- A lot of the names are hard-coded since there is 
a lack of consistency between wikipedia and 
ufcstats

## Contributing

Pull requests are welcome. For major changes, 
please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
