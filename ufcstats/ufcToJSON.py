from bs4 import BeautifulSoup
import requests
import string
import csv
import time
from pymongo import MongoClient
import os
import json


# this file scrapes ufc stats site only (not wikipedia), then populates each entry with ufc stats data. Could also fetch directly from ufc site but haven't tried it. For educational, non-commercial uses only.


key = os.environ["SECRET"]
base_api = f'http://api.scraperapi.com/?api_key={key}&url='


def checkProxy():
    proxy_ip = "47.241.165.133"
    proxy_port = "443"
    proxies = {
        "http": f"http://{proxy_ip}:{proxy_port}/",
        "https": f"http://{proxy_ip}:{proxy_port}/"
    }
    ipUrl = 'https://api.myip.com'
    try:
        response = requests.get(f'{base_api}{ipUrl}')
        print(response.text)
        # assert response.text == proxy_ip
    except:
        print("Proxy does not work")


session = requests.Session()
fighter_detail_url = 'http://ufcstats.com/fighter-details/'
fighter_list_url = 'http://ufcstats.com/statistics/fighters'

# get header data and return as list


def getHeader():
    soup = BeautifulSoup(session.get(base_api + fighter_list_url).text, 'lxml')
    table_head = soup.find(
        'thead', attrs={'class': 'b-statistics__table-caption'})
    table_headings = table_head.find('tr').text
    headers = table_headings.split()
    headers.insert(0, "path")
    return headers


hard_coded_headers = [
    'path',
    'First',
    'Last',
    'Nickname',
    'Ht.',
    'Wt.',
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
    'Avg._Takedown_/_15_min',
    'Takedown_accuracy',
    'Takedown_defense',
    'Avg_sub_attempts_/_min'
]


# get all rows for each letter
def getRowDataOfPage():
    counter = 0
    all_rows = []
    for character in string.ascii_lowercase:
        # get A-Z list
        entire_list_url = f'{base_api + fighter_list_url}?char={character}&page=all'
        pageSoup = BeautifulSoup(session.get(entire_list_url).content, 'lxml')
        pageSoup_table = pageSoup.find(
            'table', attrs={'class': 'b-statistics__table'})
        pageSoup_table_body = pageSoup_table.find('tbody')
        pageSoup_table_rows = pageSoup_table_body.find_all('tr')[1::]

        # each row in A-Z list
        added_header_to_stats = False
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
                'Avg._Takedown_/_15_min': None,
                'Takedown_accuracy': None,
                'Takedown_defense': None,
                'Avg_sub_attempts_/_min': None
            }

            # basic data first
            fighterId = row.find('a', href=True)['href']
            fighterId = fighterId.replace(fighter_detail_url, "")
            cols = row.find_all('td')

            each_fighter_row_dict['path'] = fighterId

            last_item = cols[-1]
            for (index, element) in enumerate(cols):
                # check for last td, it has belt
                if element == last_item:
                    # col_data.append(element.img['src'])
                    each_fighter_row_dict['Belt'] = 'C' if element.find(
                        'img') else ''
                else:
                    current_key = hard_coded_headers[index + 1]
                    each_fighter_row_dict[current_key] = element.text.strip()

            print(f'{counter}. ' + each_fighter_row_dict['First'] +
                  ' ' + each_fighter_row_dict['Last'])
            # get detailed nested data, 8 data points
            stat_dict = {
                'SLpM': 'Sig_Strike_/_min',
                'Str. Acc.': 'Sig_Strike_Accuracy',
                'SApM': 'Sig_Strike_absorbed_/_min',
                'Str. Def': 'Sig_Strike_defense',
                'TD Avg.': 'Avg._Takedown_/_15_min',
                'TD Acc.': 'Takedown_accuracy',
                'TD Def.': 'Takedown_defense',
                'Sub. Avg.': 'Avg_sub_attempts_/_min'
            }

            # get each stat column of the stats (2 ul's)
            fighter_url = f'{base_api + fighter_detail_url}{fighterId}'
            fighterSoup = BeautifulSoup(
                session.get(fighter_url).content, 'lxml')

            # fighterSoup_stats_ul = fighterSoup.select(
            #     'ul.b-list__box-list.b-list__box-list_margin-top > li.b-list__box-list-item.b-list__box-list-item_type_block')

            # del fighterSoup_stats_ul[4]
            # print(fighterSoup_stats_ul)
            # print(len(fighterSoup_stats_ul))

            fighterSoup_stats_ul = fighterSoup.select(
                'div.b-list__info-box-left.clearfix li.b-list__box-list-item.b-list__box-list-item_type_block')
            # print(len(fighterSoup_stats_ul))

            for (index, stat) in enumerate(fighterSoup_stats_ul):
                if index != 4:
                    stat_array = stat.get_text(strip=True).split(':')
                    stat_key = stat_array[0]
                    stat_key_alt = stat_dict[stat_key]
                    stat_value = stat_array[1]
                    each_fighter_row_dict[stat_key_alt] = stat_value

            # each person's events
            if (fighterSoup.find('table')):
                # if has an upcoming event
                latestEvent = fighterSoup.select(
                    'tr.b-fight-details__table-row.b-fight-details__table-row_type_first')
                if latestEvent:
                    opponent_col = latestEvent[0].select(
                        'td.b-fight-details__table-col')[1]
                    next_opponent = opponent_col.select(
                        'p.b-fight-details__table-text')[1]
                    each_fighter_row_dict['next'] = next_opponent.text.strip()

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
                    # pprint.PrettyPrinter(depth=4).pprint(single_fight)

            each_fighter_row_dict['events'] = all_fights
            # wait 20 seconds before accessing the next row
            # print('waiting 20 seconds before accessing next row')
            # time.sleep(5)

            # append a single row
            all_rows.append(each_fighter_row_dict)

        # wait 45 seconds before accessing next letter
        # print('waiting 45 seconds before accessing next page')
        # time.sleep(5)

    with open('newresult.json', 'w') as fp:
        json.dump(all_rows, fp, indent=4)

    return all_rows


if __name__ == "__main__":
    # checkProxy()
    list_of_fighter_dict = getRowDataOfPage()
    
    # client = MongoClient('mongodb+srv://[DATABASE]?retryWrites=true&w=majority')
    # db = client['PyToMongo']
    # mma_events = db['mma_events']
    # mma_events.insert_many(list_of_fighter_dict)
