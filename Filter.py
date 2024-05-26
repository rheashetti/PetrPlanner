import pandas as pd
import Compiler 
class Filter:
    def __init__(self, lectures_list, labs_list, discussions_list, course_prereqs: dict = None, taken_courses: list[str] = None):
        self.filtered_lectures_df = None
        self.filtered_labs_df = None
        self.filtered_discussions_df = None

        self.filtered_lectures_list = lectures_list
        self.filtered_labs_list = labs_list
        self.filtered_discussions_list = discussions_list

        self.course_prereqs = course_prereqs
        self.taken_courses = taken_courses
    
    def get_filtered_lectures_df(self) -> pd.DataFrame:
        return self.filtered_lectures_df

    def get_filtered_lectures_list(self) -> list[dict]:
        return self.filtered_lectures_list
    
    def compile_dfs(self) -> None:
        self.filtered_lectures_df = pd.DataFrame(self.filtered_lectures_list)
        self.filtered_labs_df = pd.DataFrame(self.filtered_labs_list)
        self.filtered_discussions_df = pd.DataFrame(self.filtered_discussions_list)
    
    def filter_out_prereqs(self) -> None:
        self.filtered_lectures_list = [lecture for lecture in self.filtered_lectures_list 
                                if lecture['course'] not in self.course_prereqs 
                                or all(prereq in self.taken_courses for prereq in self.course_prereqs[lecture['course']])]
        
        self.filtered_labs_list = [lab for lab in self.filtered_labs_list 
                            if lab['course'] in [lecture['course'] for lecture in self.filtered_lectures_list]]
        
        self.filtered_discussions_list = [discussion for discussion in self.filtered_discussions_list
                                    if discussion['course'] in [lecture['course'] for lecture in self.filtered_lectures_list]]
       
if __name__ == "__main__":
    WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

    APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
    APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"

    compiler = Compiler.Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()
    filter = Filter(lectures_list=compiler.get_lectures_list(), labs_list=compiler.get_labs_list(), discussions_list=compiler.get_discussions_list(), course_prereqs=compiler.get_course_prereqs(), taken_courses=['MATH 2A', 'AP CALCULUS AB', "AP CALCULUS BC","MATH 2B"])
    filter.filter_out_prereqs()
    filter.compile_dfs()
    print(filter.get_filtered_lectures_df())
    print(filter.filtered_labs_df)
    print(filter.filtered_discussions_df)
    