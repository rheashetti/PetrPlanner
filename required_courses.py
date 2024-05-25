# Description: This file is used to test the websoc scraper. It will print out the titles of the courses in the websoc page. 
# Currently only prints out the titles of the courses in the lower division section.
import requests
from bs4 import BeautifulSoup

WEBSOC_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"



def get_websoc_request():
    headers = {"User-Agent": "Microsoft Edge/92.0.902.73"}
    return requests.get(WEBSOC_BASE_URL, headers=headers).content

        

html_doc = get_websoc_request()
soup = BeautifulSoup(html_doc, 'html.parser')

titles = [] # list of course titles

first_areaheader = soup.find('tr', class_='areaheader') # represents Lower division header 
second_areaheader = first_areaheader.find_next('tr', class_='areaheader') # represents upper div header

for link in second_areaheader.find_all_previous('a')[::-1]: # iterate through all the links between lower div and upper div headers

    title = link.get('title')
    if title:

        title = title.replace('\xa0', ' ')
        if title not in titles:
            titles.append(title)
        
print(titles)
