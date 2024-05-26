import pandas as pd
import ratemyprofessor as rmp
import requests
from urllib.parse import urljoin, urlencode
import Filter, Compiler

class Sorting_Compiler:
    def __init__(self, sorting_parameters: list[str] = None, filtered_lectures_list = None, apigpa_url: str = None):
        self.sorting_parameters = sorting_parameters #avg gpa, avg rating, avg difficulty, would take again, prereq frequency

        self.filtered_lectures_list = filtered_lectures_list
        self.headers = {"User-Agent": "Microsoft Edge/92.0.902.73"}
        self.apigpa_url = apigpa_url
        
        self.gpa_dict = dict()
        self.rating_dict = dict()
        self.difficulty_dict = dict()
        self.would_take_again_dict = dict()
 
    def get_filtered_lectures_list(self) -> list[dict]:
        return self.filtered_lectures_list

    def get_gpa_dict(self) -> dict:
        return self.gpa_dict
    
    def get_rating_dict(self) -> dict:
        return self.rating_dict
    
    def get_difficulty_dict(self) -> dict:
        return self.difficulty_dict
    
    def get_would_take_again_dict(self) -> dict:
        return self.would_take_again_dict
    
    def get_prereq_freq_dict(self) -> dict:
        return self.prereq_freq_dict
    
    def compile_everything(self) -> None:
        self.compile_all_avg_gpa()
        self.compile_all_rmp_course_info()

    def compile_all_avg_gpa(self) -> None:
        [self.compile_avg_gpa_for_one_course(lecture["course"], lecture["instructors"][0]) for lecture in self.filtered_lectures_list]

    def compile_all_rmp_course_info(self) -> None:
        [self.compile_rmp_course_info_for_one_course(lecture["instructors"][0]) for lecture in self.filtered_lectures_list]
    # def compile_all_avg_gpa(self) -> None:
    #     self.filtered_lectures_df.apply(lambda row: self.compile_avg_gpa_for_one_course(row["course"], row["instructors"][0]), axis=1)

    # def compile_all_rmp_course_info(self) -> None:
    #     self.filtered_lectures_df.apply(lambda row: self.compile_rmp_course_info_for_one_course(row["instructors"][0]), axis=1)
    
    def compile_avg_gpa_for_one_course(self, course, instructor) -> float:
        parameters = dict()
        department, course_num = course.rsplit(" ", 1)

        parameters["department"] = department
        parameters["courseNumber"] = course_num
        parameters["instructor"] = instructor
        full_url = urljoin(self.apigpa_url, '?' + urlencode(parameters))
        response = requests.get(full_url, headers = self.headers).json()
        if instructor not in self.gpa_dict:
            sum_gpa = 0
            len = 0
            try:
                for gpa_dict in response:
                    if gpa_dict["averageGPA"] is not None:
                        sum_gpa += gpa_dict["averageGPA"]
                        len += 1
                self.gpa_dict[instructor] = sum_gpa / len
            except:
                print("No data for " + course + " " + instructor)
        
    
    def compile_rmp_course_info_for_one_course(self, instructor) -> None:
        professor = rmp.get_professor_by_school_and_name(
            rmp.get_school_by_name("UC Irvine"), instructor)
        if professor is not None and instructor not in self.rating_dict:
            self.rating_dict[instructor] = professor.rating if professor.rating is not None else 0
            self.difficulty_dict[instructor] = professor.difficulty if professor.difficulty is not None else 0
            self.would_take_again_dict[instructor] = professor.would_take_again if professor.would_take_again is not None else 0

    

if __name__ == "__main__":
    WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

    APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
    APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"

    compiler = Compiler.Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()

    filter = Filter.Filter(lectures_list=compiler.get_lectures_list(), labs_list=compiler.get_labs_list(), discussions_list=compiler.get_discussions_list(), course_prereqs=compiler.get_course_prereqs(), taken_courses=['MATH 2A', 'AP CALCULUS AB', "AP CALCULUS BC","MATH 2B"])
    filter.filter_out_prereqs()
    
    sorting = Sorting_Compiler(filtered_lectures_list= filter.get_filtered_lectures_list(), apigpa_url = "https://api.peterportal.org/rest/v0/grades/raw")
    sorting.compile_all_avg_gpa()
    sorting.compile_all_rmp_course_info()
    print(sorting.get_gpa_dict())
    print(sorting.get_rating_dict())
    print(sorting.get_difficulty_dict())
    print(sorting.get_would_take_again_dict())
    