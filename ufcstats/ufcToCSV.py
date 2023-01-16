from bs4 import BeautifulSoup
import requests
import string
import csv
import time
import pymongo


# this file scrapes ufc stats site only (not wikipedia) and produces a CSV, then populates each entry with ufc stats data. Could also fetch directly from ufc site but haven't tried it. For educational, non-commercial uses only.


# proxy check
def checkProxy():
  proxy_ip = "47.241.165.133"
  proxy_port = "443"
  proxies = {
      "http": f"http://{proxy_ip}:{proxy_port}/",
      "https": f"http://{proxy_ip}:{proxy_port}/"
  }
  url = 'https://api.myip.com'
  try:
      response = requests.get(url)
      print('IP: {response.text.ip}\nCountry: {response.text.country}')
      # assert response.text == proxy_ip
  except:
      print("Proxy does not work")



session = requests.Session()
fighter_detail_url = 'http://ufcstats.com/fighter-details'
fighter_list_url = 'http://ufcstats.com/statistics/fighters'


# get header data and return as list
def getHeader():
  soup = BeautifulSoup(session.get(fighter_list_url).text, 'lxml')
  table_head = soup.find('thead', attrs={'class':'b-statistics__table-caption'})
  table_headings = table_head.find('tr').text
  headers = table_headings.split()
  headers.insert(0, "url_path")
  return headers






# get all rows for each letter
def getRowDataOfPage(headers):
  prev_headers = headers

  for character in string.ascii_lowercase:
    # get A-Z list
    entire_list_url = f'{fighter_list_url}?char={character}&page=all'
    pageSoup = BeautifulSoup(session.get(entire_list_url).content, 'lxml')
    pageSoup_table = pageSoup.find('table', attrs={'class':'b-statistics__table'})
    pageSoup_table_body = pageSoup_table.find('tbody')
    pageSoup_table_rows = pageSoup_table_body.find_all('tr')[1::]

    # each row in A-Z list
    row_data = []
    added_header_to_stats = False
    for row in pageSoup_table_rows:

      # basic data first
      fighterId = row.find('a', href=True)['href']
      fighterId = fighterId.replace(fighter_detail_url, "")
      cols = row.find_all('td')

      col_data = []
      col_data.insert(0, fighterId)

      last_item = cols[-1]
      for element in cols:
        # check for last td, it has belt
        if element == last_item:
          if element.find('img'):
            # col_data.append(element.img['src'])
            col_data.append('C')
          else:
            col_data.append('')
        else:
          col_data.append(element.text.strip())

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

      # get each column of the stats (2 ul)
      fighter_url = f'{fighter_detail_url}{fighterId}'
      fighterSoup = BeautifulSoup(session.get(fighter_url).content, 'lxml')
      fighterSoup_stats_ul = fighterSoup.select('ul.b-list__box-list.b-list__box-list_margin-top > li.b-list__box-list-item.b-list__box-list-item_type_block')
      del fighterSoup_stats_ul[4]

      
      for (index, stat) in enumerate(fighterSoup_stats_ul):
        stat_array = stat.get_text(strip = True).split(':')
        stat_key = stat_array[0]
        stat_new_key = stat_dict[stat_key]
        
        if not added_header_to_stats:
          prev_headers.append(stat_new_key)
        
        stat_value = stat_array[1]
        col_data.append(stat_value)

      # wait 20 seconds before accessing the next row
      print('waiting 20 seconds before accessing next row')
      time.sleep(3)

      added_header_to_stats = True
      row_data.append(col_data)
    
    # could probably add it to the end separately (csv.writerow)
    row_data.insert(0, prev_headers)

    # wait 45 seconds before accessing next letter
    print('waiting 45 seconds before accessing next page')
    time.sleep(45)
  return row_data


# # fighter list body
# table = soup.find('table', attrs={'class':'b-statistics__table'})
# table_body = table.find('tbody')
# table_rows = table_body.find_all('tr')[1::]

# data = []
# for row in table_rows:
#   link = row.find('a', href=True)['href']
#   link = link.replace(fighter_detail_url, "")
#   cols = row.find_all('td')
#   cols = [element.text.strip() for element in cols]
#   cols.insert(0, link)
#   print(cols)
#   # data.append([ele for ele in cols])

# # print(data)
# # print(*data, sep='\n')







# Write the data to a CSV file
def writeToFile(fileName, dataToWrite):
  with open(fileName, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(dataToWrite)






if __name__ == "__main__":
  checkProxy()
  time.sleep(3)

  col_headers = getHeader()
  dataToWrite = getRowDataOfPage(col_headers)
  writeToFile("ufcstats.com.csv", dataToWrite)


# napkin, pythonAnywhere