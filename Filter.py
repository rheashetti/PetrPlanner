import pandas as pd
import Compiler 
class Filter:
    def __init__(self, lectures_df: pd.DataFrame = None, labs_df: pd.DataFrame = None, discussions_df: pd.DataFrame = None, course_prereqs: dict = None, taken_courses: list[str] = None):
        self.filtered_lectures_df = lectures_df
        self.filtered_labs_df = labs_df
        self.filtered_discussions_df = discussions_df
        self.course_prereqs = course_prereqs
        self.taken_courses = taken_courses
    
    def get_filtered_lectures_df(self) -> pd.DataFrame:
        return self.filtered_lectures_df
    
    def filter_out_prereqs(self) -> None:
        mask = self.filtered_lectures_df['course'].apply(lambda course: course not in self.course_prereqs 
                                                         or all(prereq in self.taken_courses for prereq in self.course_prereqs[course]))
        self.filtered_lectures_df = self.filtered_lectures_df[mask]
        self.filtered_labs_df = self.filtered_labs_df[self.filtered_labs_df['course'].isin(self.filtered_lectures_df['course'])]
        self.filtered_discussions_df = self.filtered_discussions_df[self.filtered_discussions_df['course'].isin(self.filtered_lectures_df['course'])]

if __name__ == "__main__":
    WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

    APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
    APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"

    compiler = Compiler.Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()
    filter = Filter(lectures_df=compiler.get_lectures_df(), labs_df=compiler.get_labs_df(), discussions_df=compiler.get_discussions_df(), course_prereqs=compiler.get_course_prereqs(), taken_courses=['MATH 2A', 'AP CALCULUS AB', "AP CALCULUS BC","MATH 2B"])
    filter.filter_out_prereqs()
    print(filter.get_filtered_lectures_df())
    print(filter.filtered_labs_df)
    print(filter.filtered_discussions_df)
    