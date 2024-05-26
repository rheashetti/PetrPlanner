import pandas as pd
import Compiler, Filter, Sorting_Compiler
import json

class Sorter:
    def __init__(self, sorting_parameters: list[str] = None, filtered_lectures_list:list[dict] = None, gpa_dict = None, rating_dict = None, difficulty_dict = None, would_take_again_dict = None, prereq_freq_dict: dict = None):
        self.sorting_parameters = sorting_parameters #avg gpa, avg rating, avg difficulty, would take again, prereq frequency
        self.sorted_lectures_list = filtered_lectures_list
        self.gpa_dict = gpa_dict
        self.rating_dict = rating_dict
        self.difficulty_dict = difficulty_dict
        self.would_take_again_dict = would_take_again_dict
        self.prereq_freq_dict = prereq_freq_dict
    
    # def get_avg_score(self):
    #     self.sorted_lectures_df.loc[:, 'instructors'] = self.sorted_lectures_df['instructors'].apply(lambda x: x[0] if x else None)
    #     # Convert dictionaries to Series for vectorized operations
    #     gpa_series = pd.Series(self.gpa_dict)
    #     rating_series = pd.Series(self.rating_dict)
    #     difficulty_series = pd.Series(self.difficulty_dict)
    #     would_take_again_series = pd.Series(self.would_take_again_dict)
    #     prereq_freq_series = pd.Series(self.prereq_freq_dict)

    #     # Initialize score and div as zero
    #     self.sorted_lectures_df['score'] = 0
    #     div = 0

    #     # Update score and div based on sorting parameters
    #     if "avg gpa" in self.sorting_parameters:
    #         self.sorted_lectures_df.loc[:, 'score'] += self.sorted_lectures_df['instructors'].map(gpa_series).fillna(2.0)
    #         div += 1
    #     if "avg rating" in self.sorting_parameters:
    #         self.sorted_lectures_df.loc[:,'score'] += self.sorted_lectures_df['instructors'].map(rating_series).fillna(2.5)
    #         div += 1
    #     if "avg difficulty" in self.sorting_parameters:
    #         self.sorted_lectures_df.loc[:,'score'] -= self.sorted_lectures_df['instructors'].map(difficulty_series).fillna(2.5)
    #         div += 1
    #     if "would take again" in self.sorting_parameters:
    #         self.sorted_lectures_df.loc[:,'score'] += self.sorted_lectures_df['instructors'].map(would_take_again_series).fillna(50)
    #         div += 1
    #     if "prereq frequency" in self.sorting_parameters:
    #         self.sorted_lectures_df.loc[:,'score'] += self.sorted_lectures_df['course'].map(prereq_freq_series).fillna(0)
    #         div += 1

    #     # Calculate average score
    #     self.sorted_lectures_df.loc[:,'score'] /= div
    def get_sorted_lectures_list(self) -> list[dict]:
        return self.sorted_lectures_list
    
    def get_sorted_lectures_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.sorted_lectures_list)
    
    def get_sorted_lectures_json(self) -> str:
        return json.dumps(self.sorted_lectures_list)
    
    def get_avg_score(self):
        for lecture in self.sorted_lectures_list:
            lecture['score'] = 0
            instructor = lecture['instructors'][0] if lecture['instructors'] else None

            if "avg gpa" in self.sorting_parameters:
                lecture['score'] += self.gpa_dict.get(instructor, 2.0)
            if "avg rating" in self.sorting_parameters:
                lecture['score'] += self.rating_dict.get(instructor, 2.5)
            if "avg difficulty" in self.sorting_parameters:
                lecture['score'] -= self.difficulty_dict.get(instructor, 2.5)
            if "would take again" in self.sorting_parameters:
                lecture['score'] += self.would_take_again_dict.get(instructor, 50)
            if "prereq frequency" in self.sorting_parameters:
                lecture['score'] += self.prereq_freq_dict.get(lecture['course'], 0)

            lecture['score'] /= len(self.sorting_parameters)
    
    def sort_list(self) -> None:
        self.get_avg_score()
        print(type(self.sorted_lectures_list))
        self.sorted_lectures_list.sort(key=lambda x: x['score'], reverse=True)

if __name__ == "__main__":
    WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

    APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
    APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"
    compiler = Compiler.Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()

    filter = Filter.Filter(lectures_list=compiler.get_lectures_list(), labs_list=compiler.get_labs_list(), discussions_list=compiler.get_discussions_list(), course_prereqs=compiler.get_course_prereqs(), taken_courses=['MATH 2A', 'AP CALCULUS AB', "AP CALCULUS BC","MATH 2B"])
    filter.filter_out_prereqs()
    
    sorting = Sorting_Compiler.Sorting_Compiler(filtered_lectures_list= filter.get_filtered_lectures_list(), apigpa_url = "https://api.peterportal.org/rest/v0/grades/raw")
    sorting.compile_all_avg_gpa()
    sorting.compile_all_rmp_course_info()

    
    sorted = Sorter(sorting_parameters=["avg gpa", "avg rating", "avg difficulty", "would take again", "prereq frequency"], filtered_lectures_list=sorting.get_filtered_lectures_list(), gpa_dict=sorting.get_gpa_dict(), rating_dict=sorting.get_rating_dict(), difficulty_dict=sorting.get_difficulty_dict(), would_take_again_dict=sorting.get_would_take_again_dict(), prereq_freq_dict=compiler.get_prereq_freq())

    sorted.sort_list()
    print(sorted.get_sorted_lectures_df())