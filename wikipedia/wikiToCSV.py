from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import yaml
from pathlib import Path


# this file scrapes tables of the ufc wikioedia roster and produces a CSV file. This only gives you the basic data (no fight history, no detailed stats). Disclaimer: For educational, non-commercial uses only.


urls_of_country_flag = yaml.safe_load(Path('list.yaml').read_text())
iso_list = {'Afghanistan': 'AF',
            'Albania': 'AL',
            'Algeria': 'DZ',
            'American Samoa': 'AS',
            'Andorra': 'AD',
            'Angola': 'AO',
            'Anguilla': 'AI',
            'Antarctica': 'AQ',
            'Antigua and Barbuda': 'AG',
            'Argentina': 'AR',
            'Armenia': 'AM',
            'Aruba': 'AW',
            'Australia': 'AU',
            'Austria': 'AT',
            'Azerbaijan': 'AZ',
            'Bahamas': 'BS',
            'Bahrain': 'BH',
            'Bangladesh': 'BD',
            'Barbados': 'BB',
            'Belarus': 'BY',
            'Belgium': 'BE',
            'Belize': 'BZ',
            'Benin': 'BJ',
            'Bermuda': 'BM',
            'Bhutan': 'BT',
            'Bolivia, Plurinational State of': 'BO',
            'Bonaire, Sint Eustatius and Saba': 'BQ',
            'Bosnia and Herzegovina': 'BA',
            'Botswana': 'BW',
            'Bouvet Island': 'BV',
            'Brazil': 'BR',
            'British Indian Ocean Territory': 'IO',
            'Brunei Darussalam': 'BN',
            'Bulgaria': 'BG',
            'Burkina Faso': 'BF',
            'Burundi': 'BI',
            'Cambodia': 'KH',
            'Cameroon': 'CM',
            'Canada': 'CA',
            'Cape Verde': 'CV',
            'Cayman Islands': 'KY',
            'Central African Republic': 'CF',
            'Chad': 'TD',
            'Chile': 'CL',
            'China': 'CN',
            'Christmas Island': 'CX',
            'Cocos (Keeling) Islands': 'CC',
            'Colombia': 'CO',
            'Comoros': 'KM',
            'Congo': 'CG',
            'Congo, the Democratic Republic of the': 'CD',
            'Cook Islands': 'CK',
            'Costa Rica': 'CR',
            'Croatia': 'HR',
            'Cuba': 'CU',
            'Curaçao': 'CW',
            'Cyprus': 'CY',
            'Czech Republic': 'CZ',
            "Côte d'Ivoire": 'CI',
            'Denmark': 'DK',
            'Djibouti': 'DJ',
            'Dominica': 'DM',
            'Dominican Republic': 'DO',
            'Ecuador': 'EC',
            'Egypt': 'EG',
            'El Salvador': 'SV',
            'Equatorial Guinea': 'GQ',
            'England': 'GB-ENG',
            'Eritrea': 'ER',
            'Estonia': 'EE',
            'Ethiopia': 'ET',
            'Falkland Islands (Malvinas)': 'FK',
            'Faroe Islands': 'FO',
            'Fiji': 'FJ',
            'Finland': 'FI',
            'France': 'FR',
            'French Guiana': 'GF',
            'French Polynesia': 'PF',
            'French Southern Territories': 'TF',
            'Gabon': 'GA',
            'Gambia': 'GM',
            'Georgia': 'GE',
            'Germany': 'DE',
            'Ghana': 'GH',
            'Gibraltar': 'GI',
            'Greece': 'GR',
            'Greenland': 'GL',
            'Grenada': 'GD',
            'Guadeloupe': 'GP',
            'Guam': 'GU',
            'Guatemala': 'GT',
            'Guernsey': 'GG',
            'Guinea': 'GN',
            'Guinea-Bissau': 'GW',
            'Guyana': 'GY',
            'Haiti': 'HT',
            'Heard Island and McDonald Islands': 'HM',
            'Holy See (Vatican City State)': 'VA',
            'Honduras': 'HN',
            'Hong Kong': 'HK',
            'Hungary': 'HU',
            'Iceland': 'IS',
            'India': 'IN',
            'Indonesia': 'ID',
            'Iran, Islamic Republic of': 'IR',
            'Iraq': 'IQ',
            'Ireland': 'IE',
            'Isle of Man': 'IM',
            'Israel': 'IL',
            'Italy': 'IT',
            'Jamaica': 'JM',
            'Japan': 'JP',
            'Jersey': 'JE',
            'Jordan': 'JO',
            'Kazakhstan': 'KZ',
            'Kenya': 'KE',
            'Kiribati': 'KI',
            "Korea, Democratic People's Republic of": 'KP',
            'South Korea': 'KR',
            'Kuwait': 'KW',
            'Kyrgyzstan': 'KG',
            "Lao People's Democratic Republic": 'LA',
            'Latvia': 'LV',
            'Lebanon': 'LB',
            'Lesotho': 'LS',
            'Liberia': 'LR',
            'Libya': 'LY',
            'Liechtenstein': 'LI',
            'Lithuania': 'LT',
            'Luxembourg': 'LU',
            'Macao': 'MO',
            'Macedonia, the former Yugoslav Republic of': 'MK',
            'Madagascar': 'MG',
            'Malawi': 'MW',
            'Malaysia': 'MY',
            'Maldives': 'MV',
            'Mali': 'ML',
            'Malta': 'MT',
            'Marshall Islands': 'MH',
            'Martinique': 'MQ',
            'Mauritania': 'MR',
            'Mauritius': 'MU',
            'Mayotte': 'YT',
            'Mexico': 'MX',
            'Micronesia, Federated States of': 'FM',
            'Moldova': 'MD',
            'Monaco': 'MC',
            'Mongolia': 'MN',
            'Montenegro': 'ME',
            'Montserrat': 'MS',
            'Morocco': 'MA',
            'Mozambique': 'MZ',
            'Myanmar': 'MM',
            'Namibia': 'NA',
            'Nauru': 'NR',
            'Nepal': 'NP',
            'Netherlands': 'NL',
            'New Caledonia': 'NC',
            'New Zealand': 'NZ',
            'Nicaragua': 'NI',
            'Niger': 'NE',
            'Nigeria': 'NG',
            'Niue': 'NU',
            'Norfolk Island': 'NF',
            'Northern Mariana Islands': 'MP',
            'Norway': 'NO',
            'Oman': 'OM',
            'Pakistan': 'PK',
            'Palau': 'PW',
            'Palestine, State of': 'PS',
            'Panama': 'PA',
            'Papua New Guinea': 'PG',
            'Paraguay': 'PY',
            'Peru': 'PE',
            'Philippines': 'PH',
            'Pitcairn': 'PN',
            'Poland': 'PL',
            'Portugal': 'PT',
            'Puerto Rico': 'PR',
            'Qatar': 'QA',
            'Romania': 'RO',
            'Russia': 'RU',
            'Rwanda': 'RW',
            'Réunion': 'RE',
            'Saint Barthélemy': 'BL',
            'Saint Helena, Ascension and Tristan da Cunha': 'SH',
            'Saint Kitts and Nevis': 'KN',
            'Saint Lucia': 'LC',
            'Saint Martin (French part)': 'MF',
            'Saint Pierre and Miquelon': 'PM',
            'Saint Vincent and the Grenadines': 'VC',
            'Samoa': 'WS',
            'San Marino': 'SM',
            'Sao Tome and Principe': 'ST',
            'Saudi Arabia': 'SA',
            'Scotland': 'GB-SCT',
            'Senegal': 'SN',
            'Serbia': 'RS',
            'Seychelles': 'SC',
            'Sierra Leone': 'SL',
            'Singapore': 'SG',
            'Sint Maarten (Dutch part)': 'SX',
            'Slovakia': 'SK',
            'Slovenia': 'SI',
            'Solomon Islands': 'SB',
            'Somalia': 'SO',
            'South Africa': 'ZA',
            'South Georgia and the South Sandwich Islands': 'GS',
            'South Sudan': 'SS',
            'Spain': 'ES',
            'Sri Lanka': 'LK',
            'Sudan': 'SD',
            'Suriname': 'SR',
            'Svalbard and Jan Mayen': 'SJ',
            'Swaziland': 'SZ',
            'Sweden': 'SE',
            'Switzerland': 'CH',
            'Syria': 'SY',
            'Taiwan, Province of China': 'TW',
            'Tajikistan': 'TJ',
            'Tanzania, United Republic of': 'TZ',
            'Thailand': 'TH',
            'Timor-Leste': 'TL',
            'Togo': 'TG',
            'Tokelau': 'TK',
            'Tonga': 'TO',
            'Trinidad and Tobago': 'TT',
            'Tunisia': 'TN',
            'Turkey': 'TR',
            'Turkmenistan': 'TM',
            'Turks and Caicos Islands': 'TC',
            'Tuvalu': 'TV',
            'Uganda': 'UG',
            'Ukraine': 'UA',
            'United Arab Emirates': 'AE',
            'United Kingdom': 'GB',
            'United States': 'US',
            'United States Minor Outlying Islands': 'UM',
            'Uruguay': 'UY',
            'Uzbekistan': 'UZ',
            'Vanuatu': 'VU',
            'Venezuela': 'VE',
            'Viet Nam': 'VN',
            'Virgin Islands, British': 'VG',
            'Virgin Islands, U.S.': 'VI',
            'Wales': 'GB-WLS',
            'Wallis and Futuna': 'WF',
            'Western Sahara': 'EH',
            'Yemen': 'YE',
            'Zambia': 'ZM',
            'Zimbabwe': 'ZW',
            'Åland Islands': 'AX'
            }


# get the tables of weight classes
soup = BeautifulSoup(session.get(wikipedia_fighter_list).text, 'lxml')
tables = soup.select("table:nth-of-type(n+10)")


# Extract the data from the tables
data = []
headers_added = False
for index, table in enumerate(tables):
    # weight = None
    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if not cols:
            # This is a header row
            if not headers_added:
                # Add the headers to the data
                data.append(["iso", "weight_class", "name", "age", "height",
                            "nickname", "status", "ufc_record", "mma_record"])
                headers_added = True
        else:
            # This is a data row
            # Extract the data from the td elements
            row_data = []
            for i, td in enumerate(cols):
                if i != 6:
                    if i == 0:
                        # Get the src attribute of the img element
                        img = td.find("img")
                        if img:
                            src = img["src"]
                            row_data.append(
                                iso_list[urls_of_country_flag[src]].lower())
                        if not weight:
                            weight_class = table.find_previous(
                                'span', {'class': 'mw-headline'}).text.strip()
                            s_index = weight_class.find('(') - 2
                            cleaned_weight_class = weight_class[:s_index] + \
                                weight_class[s_index + 1:]
                            # weight_class = weight_class[:-1]
                            weight = cleaned_weight_class
                        row_data.append(weight)
                    else:
                        # Get the text of the td element
                        row_data.append(td.text.strip())
            data.append(row_data)
    weight = None


# Write the data to a CSV file
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)


# FlagCDN for JS (use iso code)
'''
<img
  src="https://flagcdn.com/16x12/{lowercase-code}.png"
  srcset="https://flagcdn.com/32x24/{lowercase-code}.png 2x,
    https://flagcdn.com/48x36/{lowercase-code}.png 3x"
  width="16"
  height="12"
  alt="Åland Islands">
'''
