# Description: This file is used to test the websoc scraper. It will print out the titles of the courses in the websoc page. 
# Currently only prints out the titles of the courses in the lower division section.
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin, urlencode

WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"


class Compiler:
    def __init__(self, webcat_url = None, apisoc_url = None, apiprereq_url = None):
        self.webcat_url = webcat_url
        self.apisoc_url = apisoc_url
        self.apiprereq_url = apiprereq_url

        self.session = requests.Session()
        self.headers = {"User-Agent": "Microsoft Edge/92.0.902.73"}
        self.year = datetime.now().year
        self.quarter = None

        self._webcat_html_doc = None # might need for later

        self._required_courses = []
        self._lectures_df = pd.DataFrame() # makes things pretty
        self._labs_df = pd.DataFrame() # makes things pretty
        self._discussions_df = pd.DataFrame() # makes things pretty

        self._lectures_list = [] # for relational db
        self._labs_list = [] # for relational db
        self._discussions_list = [] # for relational db
 
        self._course_prereqs = dict() # key: course, value: list of prereqs
        self._prereq_freq = dict() # key: prereq, value: frequency of prereq, use for ranking later
    
    def set_quarter(self, quarter: str) -> None:
        self.quarter = quarter

    def get_required_courses(self) -> list[str]:
        return self._required_courses
    
    def get_lectures_df(self) -> pd.DataFrame: 
        return self._lectures_df
    
    def get_labs_df(self) -> pd.DataFrame: 
        return self._labs_df
    
    def get_discussions_df(self) -> pd.DataFrame: 
        return self._discussions_df

    def get_lectures_list(self) -> list[dict]: 
        return self._lectures_list
    
    def get_labs_list(self) -> list[dict]:
        return self._labs_list
    
    def get_discussions_list(self) -> list[dict]: 
        return self._discussions_list

    def get_course_prereqs(self) -> dict:
        return self._course_prereqs
    
    def get_prereq_freq(self) -> dict: 
        return self._prereq_freq
    
    def compile_everything(self) -> None:
        self.compile_html_docs()
        self.compile_required_courses()
        self.compile_all_courses()

    def compile_html_docs(self) -> None:
        self._webcat_html_doc = self._get_request(self.webcat_url).content


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

    def compile_all_courses(self) -> None:
        for course in self._required_courses:
            try:
                self.compile_one_course(course)
            except:
                print("Course DNE: " + course)
        self._lectures_df = pd.DataFrame(self._lectures_list)
        self._labs_df = pd.DataFrame(self._labs_list)
        self._discussions_df = pd.DataFrame(self._discussions_list)

    def compile_one_course(self, course: str) -> None:
        prereq_list, prereq_freq = self._get_preq_list_and_preq_freq_for_one_course(course)
        self._course_prereqs[course], self._prereq_freq[course] = prereq_list, prereq_freq

        soc_list = self._get_soc_list_for_one_course(course)
        self._lectures_list += [course_dict for course_dict in soc_list if course_dict["sectionType"] == "Lec"]
        self._labs_list += [course_dict for course_dict in soc_list if course_dict["sectionType"] == "Lab"]
        self._discussions_list += [course_dict for course_dict in soc_list if course_dict["sectionType"] =="Dis"]

    def _get_preq_list_and_preq_freq_for_one_course(self, course: str) -> tuple[list[str], int]:
        data = self._get_request(self.apiprereq_url + '/' + course.replace(" ", "")).json()
        prereq_list = data["prerequisite_list"]
        prereq_freq = len(data["prerequisite_for"])
        return prereq_list, prereq_freq

    def _get_soc_list_for_one_course(self, course: str) -> list[dict]:
        parameters = dict()
        department, course_num = course.rsplit(" ", 1)
        parameters["term"] = f'{self.year} {self.quarter}'

        parameters["department"] = department
        parameters["courseNumber"] = course_num
        
        data = self._get_request(self.apisoc_url, parameters).json()
        soc_list = data["schools"][0]["departments"][0]["courses"][0]["sections"]
        soc_list = [dict(course=course, **course_dict) for course_dict in soc_list]
        
        return soc_list

    def _get_request(self, base_url, parameters=None) -> requests.Response:
        if parameters:
            full_url = urljoin(base_url, '?' + urlencode(parameters))
        else:
            full_url = base_url
        return self.session.get(full_url, headers = self.headers)

if __name__ == "__main__":
    compiler = Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()
    print(compiler.get_required_courses())
    print(compiler.get_lectures_df())
    print(compiler.get_labs_df())
    print(compiler.get_discussions_df())
    print(compiler.get_course_prereqs())
    print(compiler.get_prereq_freq())