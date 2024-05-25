# Description: This file is used to test the websoc scraper. It will print out the titles of the courses in the websoc page. 
# Currently only prints out the titles of the courses in the lower division section.
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import json

WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"


WEBSOC_BASE_URL = "https://www.reg.uci.edu/perl/WebSoc" # easier to use rest api?
APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"

WEBPREREQ_BASE_URL = "https://www.reg.uci.edu/cob/prrqcgi" # can probs scrape directly from webpage

class Compiler:
    def __init__(self, webcat_url = None, apisoc_url = None, webprereq_url = None):
        self.webcat_url = webcat_url
        self.apisoc_url = apisoc_url
        self.webprereq_url = webprereq_url

        self.headers = {"User-Agent": "Microsoft Edge/92.0.902.73"}
        self.year = datetime.now().year
        self.quarter = None

        self._webcat_html_doc = None # might need for later
        # self._websoc_html_doc = None
        # self._webprereq_html_doc = None

        self._required_courses = []
        self._lectures = pd.DataFrame()
        self._labs_and_discussions = pd.DataFrame()
    
    def set_quarter(self, quarter: str) -> None:
        self.quarter = quarter

    def get_required_courses(self) -> list[str]:
        return self._required_courses
    
    def get_lectures(self) -> pd.DataFrame:
        return self._lectures
    
    def get_labs_and_discussions(self) -> pd.DataFrame:
        return self._labs_and_discussions

    def compile_html_docs(self) -> None:
        self._webcat_html_doc = self._get_request(self.webcat_url).content
        self._webprereq_html_doc = self._get_request(self.webprereq_url).content

    def compile_required_courses(self) -> None:
        html_parser = bs(self._webcat_html_doc, 'html.parser')
        first_areaheader = html_parser.find('tr', class_='areaheader') # represents Lower division header 
        second_areaheader = first_areaheader.find_next('tr', class_='areaheader') # represents upper div header

        for link in second_areaheader.find_all_previous('a')[::-1]: # iterate through all the links between lower div and upper div headers

            course_title = link.get('title')
            if course_title:

                course_title = course_title.replace('\xa0', ' ')
                if course_title not in self._required_courses:
                    self._required_courses.append(course_title)

    # def compile_available_required_courses(self):
    #     html_parser = bs(self._websoc_html_doc, 'html.parser')

    def compile_all_courses(self) -> None:
        for course in self._required_courses:
            try:
                self.compile_one_course(course)
            except:
                print("Course DNE: " + course)
    def compile_one_course(self, course: str) -> None:
        soc_list = self._get_soc_list_for_one_course(course)
        for course in soc_list:
            if course["sectionType"] == "Lec":
                self._lectures = self._lectures._append(course, ignore_index=True)
            else:
                self._labs_and_discussions = self._labs_and_discussions._append(course, ignore_index=True)


    def _get_soc_list_for_one_course(self, course: str) -> list[dict]:
        parameters = dict()
        department, course_num = course.rsplit(" ", 1)
        parameters["term"] = f'{self.year} {self.quarter}'

        parameters["department"] = department
        parameters["courseNumber"] = course_num
        
        data = self._get_request(self.apisoc_url, parameters).json()
        soc_list = data["schools"][0]["departments"][0]["courses"][0]["sections"]
        for course_dict in soc_list:
            course_dict["correCourse"] = course

        return soc_list

    
    # def _get_request(self, base_url, parameters=None) -> requests.Response:
    #     return requests.get(base_url, params = parameters, headers = self.headers).content
        

    def _get_request(self, base_url, parameters=None) -> requests.Response:
        from urllib.parse import urljoin, urlencode
        if parameters:
            full_url = urljoin(base_url, '?' + urlencode(parameters))
        else:
            full_url = base_url
        print(full_url)  # Outputs the full URL
        return requests.get(full_url, headers = self.headers)

if __name__ == "__main__":
    compiler = Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, WEBPREREQ_BASE_URL)
    compiler.compile_html_docs()
    compiler.compile_required_courses()
    print(compiler.get_required_courses())

    compiler.set_quarter("Fall")

    compiler.compile_all_courses()
    print(compiler._lectures)
    print(compiler._labs_and_discussions)
    # print(pd.DataFrame(data))