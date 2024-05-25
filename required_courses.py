# Description: This file is used to test the websoc scraper. It will print out the titles of the courses in the websoc page. 
# Currently only prints out the titles of the courses in the lower division section.
import requests
from bs4 import BeautifulSoup as bs

WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

class Compiler:
    def __init__(self, webcat_url = None, websoc_url = None, webprereq_url = None):
        self.webcat_url = webcat_url
        self.websoc_url = websoc_url
        self.webprereq_url = webprereq_url

        self._webcat_html_doc = None
        self._websoc_html_doc = None
        self._webprereq_html_doc = None

        self._required_courses = []

    def get_required_courses(self):
        return self._required_courses

    def compile_html_docs(self):
        self._webcat_html_doc = self._get_request(self.webcat_url)
        # self._websoc_html_doc = self._get_request(self.websoc_url)
        # self._webprereq_html_doc = self._get_request(self.webprereq_url)

    def compile_required_courses(self):
        html_parser = bs(self._webcat_html_doc, 'html.parser')
        first_areaheader = html_parser.find('tr', class_='areaheader') # represents Lower division header 
        second_areaheader = first_areaheader.find_next('tr', class_='areaheader') # represents upper div header

        for link in second_areaheader.find_all_previous('a')[::-1]: # iterate through all the links between lower div and upper div headers

            course_title = link.get('title')
            if course_title:

                course_title = course_title.replace('\xa0', ' ')
                if course_title not in self._required_courses:
                    self._required_courses.append(course_title)

    

    def _get_request(self, base_url):
        headers = {"User-Agent": "Microsoft Edge/92.0.902.73"}
        return requests.get(base_url, headers=headers).content


if __name__ == "__main__":
    compiler = Compiler(WEBCAT_BASE_URL)
    compiler.compile_html_docs()
    compiler.compile_required_courses()
    print(compiler.get_required_courses())
