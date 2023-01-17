from bs4 import BeautifulSoup
import requests
import csv
from pathlib import Path
import json
import string
import time
import os
import datetime
from pathlib import Path
import re
import unicodedata as ud
from unidecode import unidecode
# from pymongo import MongoClient


# this file scrapes ufc wiki roster, then adds additional data (entire fight history, stats) for each entry using ufc stats data. Could also fetch directly from ufc site but haven't tried it. Disclaimer: For educational, non-commercial uses only.


startTime = time.time()
base = Path('data')
jsonPath = base / (f"data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
base.mkdir(exist_ok=True)


wikipedia_fighter_list = 'https://en.wikipedia.org/wiki/List_of_current_UFC_fighters'
fighter_detail_url = 'http://ufcstats.com/fighter-details/'
fighter_list_url = 'http://ufcstats.com/statistics/fighters'


# scraperbox
# scraperbox_key = os.environ['SCRAPERBOX']
# scraperbox_base = f"https://api.scraperbox.com/scrape?token=%s{scraperbox_key}

# scraperapi
# scraperapi_key = os.environ['SCRAPERAPI']
# scraperapi_base = f'http://api.scraperapi.com/?api_key={key}&url='

# zenrows_base = os.environ['ZENROWS_PROXY']
# zenrows_proxy = {
#     "http": "http://",
#     "https": "http://"
# }

# zenrows_proxy = {
#     "http": f'{zenrows_base}',
#     "https": f'{zenrows_base}'
# }

session = requests.Session()
# session.proxies = zenrows_proxy
# session.verify = False



def checkProxy():
    # proxy_ip = "47.241.165.133"
    # proxy_port = "443"
    # proxies = {
    #     "http": f"http://{proxy_ip}:{proxy_port}/",
    #     "https": f"http://{proxy_ip}:{proxy_port}/"
    # }
    ipUrl = 'https://api.myip.com'
    # ipUrl = 'https://api.ipify.org'
    try:
        response = requests.get(ipUrl, verify=False)
        print(response.text)
        # assert response.text == proxy_ip
    except:
        print("Proxy does not work")




# urls_of_country_flag = yaml.safe_load(Path("list.yaml").read_text())
# hard coding instead for now
urls_of_country_flag = {
    "//upload.wikimedia.org/wikipedia/commons/thumb/8/85/Flag_of_Belarus.svg/23px-Flag_of_Belarus.svg.png": "Belarus",
    "//upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Flag_of_the_United_States.svg/23px-Flag_of_the_United_States.svg.png": "United States",
    "//upload.wikimedia.org/wikipedia/en/thumb/4/4c/Flag_of_Sweden.svg/23px-Flag_of_Sweden.svg.png": "Sweden",
    "//upload.wikimedia.org/wikipedia/en/thumb/0/05/Flag_of_Brazil.svg/23px-Flag_of_Brazil.svg.png": "Brazil",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Russia.svg/23px-Flag_of_Russia.svg.png": "Russia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Flag_of_Cameroon.svg/23px-Flag_of_Cameroon.svg.png": "Cameroon",
    "//upload.wikimedia.org/wikipedia/commons/thumb/5/53/Flag_of_Syria.svg/23px-Flag_of_Syria.svg.png": "Syria",
    "//upload.wikimedia.org/wikipedia/en/thumb/1/12/Flag_of_Poland.svg/23px-Flag_of_Poland.svg.png": "Poland",
    "//upload.wikimedia.org/wikipedia/en/thumb/b/b9/Flag_of_Australia.svg/23px-Flag_of_Australia.svg.png": "Australia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Bulgaria.svg/23px-Flag_of_Bulgaria.svg.png": "Bulgaria",
    "//upload.wikimedia.org/wikipedia/en/thumb/9/9a/Flag_of_Spain.svg/23px-Flag_of_Spain.svg.png": "Spain",
    "//upload.wikimedia.org/wikipedia/commons/thumb/6/60/Flag_of_Suriname.svg/23px-Flag_of_Suriname.svg.png": "Suriname",
    "//upload.wikimedia.org/wikipedia/commons/thumb/2/27/Flag_of_Moldova.svg/23px-Flag_of_Moldova.svg.png": "Moldova",
    "//upload.wikimedia.org/wikipedia/en/thumb/c/c3/Flag_of_France.svg/23px-Flag_of_France.svg.png": "France",
    "//upload.wikimedia.org/wikipedia/en/thumb/c/cf/Flag_of_Canada.svg/23px-Flag_of_Canada.svg.png": "Canada",
    "//upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/23px-Flag_of_England.svg.png": "England",
    "//upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/23px-Flag_of_Slovakia.svg.png": "Slovakia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Flag_of_Egypt.svg/23px-Flag_of_Egypt.svg.png": "Egypt",
    "//upload.wikimedia.org/wikipedia/commons/thumb/7/79/Flag_of_Nigeria.svg/23px-Flag_of_Nigeria.svg.png": "Nigeria",
    "//upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_the_Dominican_Republic.svg/23px-Flag_of_the_Dominican_Republic.svg.png": "Dominican Republic",
    "//upload.wikimedia.org/wikipedia/commons/thumb/5/56/Flag_of_Haiti.svg/23px-Flag_of_Haiti.svg.png": "Haiti",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/23px-Flag_of_Ukraine.svg.png": "Ukraine",
    "//upload.wikimedia.org/wikipedia/commons/thumb/1/10/Flag_of_Scotland.svg/23px-Flag_of_Scotland.svg.png": "Scotland",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Flag_of_Switzerland.svg/23px-Flag_of_Switzerland.svg.png": "Switzerland",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_Austria.svg/23px-Flag_of_Austria.svg.png": "Austria",
    "//upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/23px-Flag_of_Romania.svg.png": "Romania",
    "//upload.wikimedia.org/wikipedia/commons/thumb/0/09/Flag_of_South_Korea.svg/23px-Flag_of_South_Korea.svg.png": "South Korea",
    "//upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_Czech_Republic.svg/23px-Flag_of_the_Czech_Republic.svg.png": "Czech Republic",
    "//upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Flag_of_New_Zealand.svg/23px-Flag_of_New_Zealand.svg.png": "New Zealand",
    "//upload.wikimedia.org/wikipedia/en/thumb/0/03/Flag_of_Italy.svg/23px-Flag_of_Italy.svg.png": "Italy",
    "//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Flag_of_Norway.svg/23px-Flag_of_Norway.svg.png": "Norway",
    "//upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Flag_of_Wales.svg/23px-Flag_of_Wales.svg.png": "Wales",
    "//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Ghana.svg/23px-Flag_of_Ghana.svg.png": "Ghana",
    "//upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Flag_of_Morocco.svg/23px-Flag_of_Morocco.svg.png": "Morocco",
    "//upload.wikimedia.org/wikipedia/commons/thumb/8/84/Flag_of_Uzbekistan.svg/23px-Flag_of_Uzbekistan.svg.png": "Uzbekistan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/23px-Flag_of_Georgia.svg.png": "Georgia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Flag_of_Serbia.svg/23px-Flag_of_Serbia.svg.png": "Serbia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/a/af/Flag_of_South_Africa.svg/23px-Flag_of_South_Africa.svg.png": "South Africa",
    "//upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_Armenia.svg/23px-Flag_of_Armenia.svg.png": "Armenia",
    "//upload.wikimedia.org/wikipedia/en/thumb/b/ba/Flag_of_Germany.svg/23px-Flag_of_Germany.svg.png": "Germany",
    "//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Iceland.svg/23px-Flag_of_Iceland.svg.png": "Iceland",
    "//upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Argentina.svg/23px-Flag_of_Argentina.svg.png": "Argentina",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Flag_of_the_People%27s_Republic_of_China.svg/23px-Flag_of_the_People%27s_Republic_of_China.svg.png": "China",
    "//upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Denmark.svg/23px-Flag_of_Denmark.svg.png": "Denmark",
    "//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Jamaica.svg/23px-Flag_of_Jamaica.svg.png": "Jamaica",
    "//upload.wikimedia.org/wikipedia/en/thumb/9/9e/Flag_of_Japan.svg/23px-Flag_of_Japan.svg.png": "Japan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Flag_of_Tunisia.svg/23px-Flag_of_Tunisia.svg.png": "Tunisia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Flag_of_Kazakhstan.svg/23px-Flag_of_Kazakhstan.svg.png": "Kazakhstan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/9/99/Flag_of_Guyana.svg/23px-Flag_of_Guyana.svg.png": "Guyana",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/45/Flag_of_Ireland.svg/23px-Flag_of_Ireland.svg.png": "Ireland",
    "//upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Flag_of_Ecuador.svg/23px-Flag_of_Ecuador.svg.png": "Ecuador",
    "//upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/23px-Flag_of_Portugal.svg.png": "Portugal",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Flag_of_Mexico.svg/23px-Flag_of_Mexico.svg.png": "Mexico",
    "//upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Peru.svg/23px-Flag_of_Peru.svg.png": "Peru",
    "//upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Flag_of_Azerbaijan.svg/23px-Flag_of_Azerbaijan.svg.png": "Azerbaijan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/0/06/Flag_of_Venezuela.svg/23px-Flag_of_Venezuela.svg.png": "Venezuela",
    "//upload.wikimedia.org/wikipedia/commons/thumb/7/78/Flag_of_Chile.svg/23px-Flag_of_Chile.svg.png": "Chile",
    "//upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Israel.svg/23px-Flag_of_Israel.svg.png": "Israel",
    "//upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Flag_of_Finland.svg/23px-Flag_of_Finland.svg.png": "Finland",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Flag_of_Uganda.svg/23px-Flag_of_Uganda.svg.png": "Uganda",
    "//upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/23px-Flag_of_the_Netherlands.svg.png": "Netherlands",
    "//upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Flag_of_Mongolia.svg/23px-Flag_of_Mongolia.svg.png": "Mongolia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/0/07/Flag_of_Guam.svg/23px-Flag_of_Guam.svg.png": "Guam",
    "//upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Flag_of_Afghanistan_%282004%E2%80%932021%29.svg/23px-Flag_of_Afghanistan_%282004%E2%80%932021%29.svg.png": "Afghanistan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Iraq.svg/23px-Flag_of_Iraq.svg.png": "Iraq",
    "//upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/23px-Flag_of_Angola.svg.png": "Angola",
    "//upload.wikimedia.org/wikipedia/commons/thumb/2/21/Flag_of_Colombia.svg/23px-Flag_of_Colombia.svg.png": "Colombia",
    "//upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Lithuania.svg/23px-Flag_of_Lithuania.svg.png": "Lithuania",
    "//upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Flag_of_Panama.svg/23px-Flag_of_Panama.svg.png": "Panama",
    "//upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Flag_of_Kyrgyzstan.svg/23px-Flag_of_Kyrgyzstan.svg.png": "Kyrgyzstan",
    "//upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Flag_of_Thailand.svg/23px-Flag_of_Thailand.svg.png": "Thailand",
}

iso_list = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "American Samoa": "AS",
    "Andorra": "AD",
    "Angola": "AO",
    "Anguilla": "AI",
    "Antarctica": "AQ",
    "Antigua and Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Aruba": "AW",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Belize": "BZ",
    "Benin": "BJ",
    "Bermuda": "BM",
    "Bhutan": "BT",
    "Bolivia, Plurinational State of": "BO",
    "Bonaire, Sint Eustatius and Saba": "BQ",
    "Bosnia and Herzegovina": "BA",
    "Botswana": "BW",
    "Bouvet Island": "BV",
    "Brazil": "BR",
    "British Indian Ocean Territory": "IO",
    "Brunei Darussalam": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Burundi": "BI",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Cape Verde": "CV",
    "Cayman Islands": "KY",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China": "CN",
    "Christmas Island": "CX",
    "Cocos (Keeling) Islands": "CC",
    "Colombia": "CO",
    "Comoros": "KM",
    "Congo": "CG",
    "Congo, the Democratic Republic of the": "CD",
    "Cook Islands": "CK",
    "Costa Rica": "CR",
    "Croatia": "HR",
    "Cuba": "CU",
    "Curaçao": "CW",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Côte d'Ivoire": "CI",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominica": "DM",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Equatorial Guinea": "GQ",
    "England": "GB-ENG",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Ethiopia": "ET",
    "Falkland Islands (Malvinas)": "FK",
    "Faroe Islands": "FO",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "French Guiana": "GF",
    "French Polynesia": "PF",
    "French Southern Territories": "TF",
    "Gabon": "GA",
    "Gambia": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Greece": "GR",
    "Greenland": "GL",
    "Grenada": "GD",
    "Guadeloupe": "GP",
    "Guam": "GU",
    "Guatemala": "GT",
    "Guernsey": "GG",
    "Guinea": "GN",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Haiti": "HT",
    "Heard Island and McDonald Islands": "HM",
    "Holy See (Vatican City State)": "VA",
    "Honduras": "HN",
    "Hong Kong": "HK",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran, Islamic Republic of": "IR",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Isle of Man": "IM",
    "Israel": "IL",
    "Italy": "IT",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jersey": "JE",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Kiribati": "KI",
    "Korea, Democratic People's Republic of": "KP",
    "South Korea": "KR",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Lao People's Democratic Republic": "LA",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Lesotho": "LS",
    "Liberia": "LR",
    "Libya": "LY",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Macao": "MO",
    "Macedonia, the former Yugoslav Republic of": "MK",
    "Madagascar": "MG",
    "Malawi": "MW",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Mali": "ML",
    "Malta": "MT",
    "Marshall Islands": "MH",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mayotte": "YT",
    "Mexico": "MX",
    "Micronesia, Federated States of": "FM",
    "Moldova": "MD",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Montserrat": "MS",
    "Morocco": "MA",
    "Mozambique": "MZ",
    "Myanmar": "MM",
    "Namibia": "NA",
    "Nauru": "NR",
    "Nepal": "NP",
    "Netherlands": "NL",
    "New Caledonia": "NC",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "Niue": "NU",
    "Norfolk Island": "NF",
    "Northern Mariana Islands": "MP",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Palau": "PW",
    "Palestine, State of": "PS",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Pitcairn": "PN",
    "Poland": "PL",
    "Portugal": "PT",
    "Puerto Rico": "PR",
    "Qatar": "QA",
    "Romania": "RO",
    "Russia": "RU",
    "Rwanda": "RW",
    "Réunion": "RE",
    "Saint Barthélemy": "BL",
    "Saint Helena, Ascension and Tristan da Cunha": "SH",
    "Saint Kitts and Nevis": "KN",
    "Saint Lucia": "LC",
    "Saint Martin (French part)": "MF",
    "Saint Pierre and Miquelon": "PM",
    "Saint Vincent and the Grenadines": "VC",
    "Samoa": "WS",
    "San Marino": "SM",
    "Sao Tome and Principe": "ST",
    "Saudi Arabia": "SA",
    "Scotland": "GB-SCT",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Sierra Leone": "SL",
    "Singapore": "SG",
    "Sint Maarten (Dutch part)": "SX",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Solomon Islands": "SB",
    "Somalia": "SO",
    "South Africa": "ZA",
    "South Georgia and the South Sandwich Islands": "GS",
    "South Sudan": "SS",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Svalbard and Jan Mayen": "SJ",
    "Swaziland": "SZ",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Syria": "SY",
    "Taiwan, Province of China": "TW",
    "Tajikistan": "TJ",
    "Tanzania, United Republic of": "TZ",
    "Thailand": "TH",
    "Timor-Leste": "TL",
    "Togo": "TG",
    "Tokelau": "TK",
    "Tonga": "TO",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Turkmenistan": "TM",
    "Turks and Caicos Islands": "TC",
    "Tuvalu": "TV",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United Kingdom": "GB",
    "United States": "US",
    "United States Minor Outlying Islands": "UM",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Vanuatu": "VU",
    "Venezuela": "VE",
    "Viet Nam": "VN",
    "Virgin Islands, British": "VG",
    "Virgin Islands, U.S.": "VI",
    "Wales": "GB-WLS",
    "Wallis and Futuna": "WF",
    "Western Sahara": "EH",
    "Yemen": "YE",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
    "Åland Islands": "AX",
}




# Part 1. wikipedia ufc active roster
soup = BeautifulSoup(session.get(wikipedia_fighter_list).text, 'lxml')
tables = soup.select("table:nth-of-type(n+10)")
hard_coded_wiki_headers = [
    "iso",
    "name",
    "age",
    "height",
    "nickname",
    "status",
    "ref",
    "ufc_record",
    "mma_record",
]

def wikiNameException(name):
    # there isn't much consistency between the wiki names and ufc stats names. So this is a temporary fix.

    wikiNameDict = {
        'Jun Yong Park': ['Junyong', 'Park'],
        'Johnny Munoz Jr.': ['Johnny', 'Munoz'],
        'Aori Qileng': ['', 'Aoriqileng'],
        'Su Mudaerji': ['', 'Sumudaerji'],
        'Bruno Gustavo da Silva': ['Bruno', 'Silva'],
        'Zarah Fairn Dos Santos': ['Zarah', 'Fairn'],
        'Alateng Heili': ['', 'Alatengheili'],
        'Liu Pingyuan': ['Pingyuan', 'Liu'],
        'Hayisaer Maheshate': ['', 'Maheshate'],
        'Benoit Saint-Denis': ['Benoit', 'Saint Denis'],
        'Da Un Jung': ['Da-Un', 'Jung'],
        'Jung Chan-sung': ['Chan Sung', 'Jung'],
        'Choi Doo-ho': ['Dooho', 'Choi'],
        'Seung Woo Choi': ['SeungWoo', 'Choi'],
        'Martin Sano Jr.': ['Martin', 'Sano'],
        'Jinh Yu Frey': ['Jinh Yu', 'Frey'],
        'Kang Kyung-ho': ['Kyung Ho', 'Kang'],
        'Dricus du Plessis': ['Dricus', 'Du Plessis'],
        'A.J. Dobson': ['AJ', 'Dobson'],
        'Lupita Godinez': ['Loopy', 'Godinez'],
        'Ji Yeon Kim': ['Ji Yeon', 'Kim'],
        'Abusupiyan Magomedov': ['Abus', 'Magomedov'],
        'Sergey Spivak': ['Serghei', 'Spivac'],
        'Alexander Romanov': ['Alexandr', 'Romanov'],
        'Joseph Pyfer': ['Joe', 'Pyfer'],
        'Rafael dos Anjos': ['Rafael', 'Dos', 'Anjos'],
        'Gabriel Green': ['Gabe', 'Green'],
        'Philip Rowe': ['Phil', 'Rowe'],
        'Mike Mathetha': ['Blood', 'Diamond'],
        'Carlos Diego Ferreira': ['Diego', 'Ferreira'],
        'Joshua Culibao': ['Josh', 'Culibao'],
        'T.J. Brown': ['TJ', 'Brown'],
        'Daniel Argueta': ['Dan', 'Argueta'],
        'Danaa Batgerel': ['Batgerel', 'Danaa'],
        'Leomana Martinez': ['Mana', 'Martinez'],
        "Ode' Osbourne": ['Ode', 'Osbourne'],
        'Daniel da Silva': ['Daniel', 'Da Silva'],
        'C.J. Vergara': ['CJ', 'Vergara'],
        'Brogan Walker-Sanchez': ['Brogan', 'Walker'],
        'Michelle Waterson': ['Michelle', 'Waterson-Gomez'],
        'Mizuki Inoue': ['Inoue', 'Mizuki'],
        'Montserrat Ruiz': ['Montserrat', 'Conejo'],
        'Na Liang': ['Liang', 'Na']
    }
    if name in wikiNameDict:
        return wikiNameDict[name]
    else:
        output_str = ''.join(c for c in name if c.isprintable())
        return output_str.split(' ')
        

# Extract the data from the wiki tables
all_data = []
fighter_names = []
for index, table in enumerate(tables):
    weight = None

    if not weight:
        weight_class = table.find_previous("span", {"class": "mw-headline"}).text.strip()

        # another exception
        if weight_class == "Women's featherweights (145 lb, 65 kg)":
            weight_class = "Women's bantamweights (135 lb, 61 kg)"

        s_index = weight_class.find("(") - 2
        cleaned_weight_class = "{}{}".format(weight_class[:s_index], weight_class[s_index + 1 :])
        weight = cleaned_weight_class

    rows = table.find_all("tr")
    for row in rows[1::]:
        wiki_each_fighter_row_dict = {
            "iso": None,
            "first": None,
            "last": None,
            "weight_class": None,
            "name": None,
            "age": None,
            "height": None,
            "nickname": None,
            "status": None,
            "ufc_record": None,
            "mma_record": None,
        }

        wiki_each_fighter_row_dict["weight_class"] = weight
        
        cols = row.find_all("td")
        full_name = unidecode(cols[1].text.strip())
        full_name = re.sub('\s{2,}', ' ', full_name)
        # print("wiki:", full_name)

        cleanedName = re.sub(r'\(.*?\)|\*', '', full_name).strip()
        cleanedName = ud.normalize('NFD',cleanedName)
        # print("remove (c) and *:", cleanedName)
        
        full_name_string_processed = wikiNameException(cleanedName)
        # print("exception name:", full_name_string_processed)

        newFirst = full_name_string_processed[0]
        newLast =  " ".join(full_name_string_processed[1::])
        newName = f'{newFirst} {newLast}'
        # print("new name:", newName)

        cleanedName = re.sub(r'\(.*?\)|\*', '', newName)
        # print(f'ufcstats name: {cleanedName}')

        if cleanedName in fighter_names:
            # print(f'skipping {cleanedName} 2nd')
            # add to the existing record, but modify the weight class. This is for W featherweight -> W bantamweight
            wiki_each_fighter_row_dict['weight_class'] = weight
            continue
        
        # Extract the data from the td elements
        for index, td in enumerate(cols):
            if index == 6:
                continue
            if index == 0:
                # Get the src attribute of the img element
                img = td.find("img")
                if img:
                    src = img["src"]
                    wiki_each_fighter_row_dict['iso'] = iso_list[
                        urls_of_country_flag[src]
                    ]
            elif index == 1:
                wiki_each_fighter_row_dict['first'] = newFirst
                wiki_each_fighter_row_dict['last'] = newLast
                wiki_each_fighter_row_dict['name'] = newName
                fighter_names.append(cleanedName)
            else:
                # Get the text of the td element
                wiki_each_fighter_row_dict[hard_coded_wiki_headers[index]] = td.text.strip()
        all_data.append(wiki_each_fighter_row_dict)




















# part 2. ufc stats data
# get header data and return as list
def getHeader():
    soup = BeautifulSoup(session.get(fighter_list_url).text, 'lxml')
    table_head = soup.find(
        'thead', attrs={'class': 'b-statistics__table-caption'})
    table_headings = table_head.find('tr').text
    headers = table_headings.split()
    headers.insert(0, "path")
    return headers


hard_coded_headers = [
    'path',
    'Reach',
    'Stance',
    'W',
    'L',
    'D',
    'Belt',
    'Sig_Strike_/_min',
    'Sig_Strike_Accuracy',
    'Sig_Strike_absorbed_/_min',
    'Sig_Strike_defense',
    'Avg_Takedown_/_15_min',
    'Takedown_accuracy',
    'Takedown_defense',
    'Avg_sub_attempts_/_min'
]





# get all rows for each letter
def getAllPages():
    all_rows = []
    for character in string.ascii_lowercase:
        counter = 0
        # get A-Z list
        entire_list_url = f'{fighter_list_url}?char={character}&page=all'
        pageSoup = BeautifulSoup(session.get(entire_list_url).content, 'lxml')
        pageSoup_table = pageSoup.find(
            'table', attrs={'class': 'b-statistics__table'})
        pageSoup_table_body = pageSoup_table.find('tbody')
        pageSoup_table_rows = pageSoup_table_body.find_all('tr')[1::]

        # each row in A-Z list
        for row in pageSoup_table_rows:
            counter = counter + 1
            # print(f'on fighter #{counter}...')
            each_fighter_row_dict = {
                'path': None,
                'First': None,
                'Last': None,
                'Nickname': None,
                'Ht.': None,
                'Wt.': None,
                'Reach': None,
                'Stance': None,
                'W': None,
                'L': None,
                'D': None,
                'Belt': None,
                'Sig_Strike_/_min': None,
                'Sig_Strike_Accuracy': None,
                'Sig_Strike_absorbed_/_min': None,
                'Sig_Strike_defense': None,
                'Avg_Takedown_/_15_min': None,
                'Takedown_accuracy': None,
                'Takedown_defense': None,
                'Avg_sub_attempts_/_min': None
            }

            # basic data first
            fighterId = row.find('a', href=True)['href']
            fighterId = fighterId.replace(fighter_detail_url, "")
            # each_fighter_row_dict['path'] = fighterId

            cols = row.find_all('td')
            first_name = cols[0].text.strip()
            last_name = cols[1].text.strip()
            fighter_name = f'{first_name} {last_name}'
            
            if fighter_name in fighter_names:
                print(f'getting data for {fighter_name}')

                fighter_dict_ref = None
                fighter_dict_entries = [fighter for fighter in all_data if (fighter["first"] == first_name) and fighter['last'] == last_name]

                # if there are more than 2 entries due to same first and last name
                if (len(fighter_dict_entries) > 1):
                    ufcstatsNickname = cols[2]
                    nicknameFiltered = [fighter for fighter in fighter_dict_entries if fighter["nickname"] == ufcstatsNickname][0]
                    fighter_dict_ref = nicknameFiltered
                else:
                    fighter_dict_ref = fighter_dict_entries[0]

                last_item = cols[-1]
                for (index, element) in enumerate(cols[5::]):
                    # check for last td, it has belt
                    if element == last_item:
                        fighter_dict_ref['Belt'] = 'C' if element.find(
                            'img') else ''
                    else:
                        current_key = hard_coded_headers[index + 1]
                        fighter_dict_ref[current_key] = element.text.strip()

                # get detailed nested data, 8 different stats
                stat_dict = {
                    'SLpM': 'Sig_Strike_/_min',
                    'Str. Acc.': 'Sig_Strike_Accuracy',
                    'SApM': 'Sig_Strike_absorbed_/_min',
                    'Str. Def': 'Sig_Strike_defense',
                    'TD Avg.': 'Avg_Takedown_/_15_min',
                    'TD Acc.': 'Takedown_accuracy',
                    'TD Def.': 'Takedown_defense',
                    'Sub. Avg.': 'Avg_sub_attempts_/_min'
                }

                # get each stat column of the stats (2 ul's)
                fighter_url = f'{fighter_detail_url}{fighterId}'
                fighterSoup = BeautifulSoup(
                    session.get(fighter_url).content, 'lxml')

                fighterSoup_stats_ul = fighterSoup.select(
                    'div.b-list__info-box-left.clearfix li.b-list__box-list-item.b-list__box-list-item_type_block')

                for (index, stat) in enumerate(fighterSoup_stats_ul):
                    if index != 4:
                        stat_array = stat.get_text(strip=True).split(':')
                        stat_key = stat_array[0]
                        stat_key_alt = stat_dict[stat_key]
                        stat_value = stat_array[1]
                        fighter_dict_ref[stat_key_alt] = stat_value

                # each person's events
                if (fighterSoup.find('table')):
                    # if has an upcoming event
                    upcomingFight = fighterSoup.select(
                        'tr.b-fight-details__table-row.b-fight-details__table-row_type_first')
                    if upcomingFight:
                        upcomingFightDict = {}
                        upcomingFightRow = upcomingFight[0]
                        upcomingFightData = upcomingFightRow.select('td.b-fight-details__table-col.l-page_align_left')

                        opponent = upcomingFightData[0].select(
                            'p.b-fight-details__table-text')[1]
                        locationData = upcomingFightData[1].select('p.b-fight-details__table-text')
                        
                        upcomingFightEvent = locationData[0].text.strip()
                        upcomingFightDate = locationData[1].text.strip()
                        
                        upcomingFightDict['opponent'] = opponent.text.strip()
                        upcomingFightDict['event'] = upcomingFightEvent
                        upcomingFightDict['date'] = upcomingFightDate

                        fighter_dict_ref['next'] = upcomingFightDict

                    # get all events
                    fighterSoup_all_fights = fighterSoup.select(
                        'tr.b-fight-details__table-row.b-fight-details__table-row__hover.js-fight-details-click')

                    all_fights = []
                    for (index, fight) in enumerate(fighterSoup_all_fights):
                        # this is a single fight
                        # td index: 0, 1, 6, 7, 8, 9
                        single_fight = {
                            'result': None,
                            'opponent': None,
                            'event': None,
                            'forBelt': None,
                            'date': None,
                            'method': None,
                            'round': None,
                            'time': None,
                        }
                        fight_data = fight.select('td.b-fight-details__table-col')
                        del fight_data[2:6]
                        if (fight_data):
                            for (index, cell) in enumerate(fight_data):
                                if index == 0:
                                    single_fight['result'] = cell.text.strip()
                                if index == 1:
                                    opponent = cell.select(
                                        'p.b-fight-details__table-text')[1]
                                    single_fight['opponent'] = opponent.text.strip()
                                if index == 2:
                                    eventData = cell.select(
                                        'p.b-fight-details__table-text')
                                    event = eventData[0].text.strip()
                                    date = eventData[1].text.strip()
                                    single_fight['event'] = event
                                    single_fight['date'] = date
                                if index == 3:
                                    single_fight['method'] = cell.get_text(
                                        strip=True, separator=' ')
                                if index == 4:
                                    single_fight['round'] = cell.text.strip()
                                if index == 5:
                                    single_fight['time'] = cell.text.strip()
                        all_fights.append(single_fight)
                    fighter_dict_ref['events'] = all_fights
            else:
                print(f'{fighter_name} is not active. skipping to next row')
                continue
            # wait 2 seconds before accessing the next row
            time.sleep(2)

        # wait 4 seconds before accessing next letter
        time.sleep(2)
    
    # write to the JSON file
    with open(jsonPath, 'w') as fp:
        json.dump(all_data, fp, indent=4)


if __name__ == "__main__":
    checkProxy()
    getAllPages()

    executionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(executionTime))

    # client = MongoClient('mongokey')
    # db = client['PyToMongo']
    # mma_events = db['mma_events']
    # mma_events.insert_many(list_of_fighter_dict)
