import pandas as pd
import Compiler, Filter, Sorting_Compiler
class Sorter:
    def __init__(self, sorting_parameters: list[str] = None, filtered_lectures_df: pd.DataFrame = None, gpa_dict = None, rating_dict = None, difficulty_dict = None, would_take_again_dict = None, prereq_freq_dict: dict = None):
        self.sorting_parameters = sorting_parameters #avg gpa, avg rating, avg difficulty, would take again, prereq frequency
        self.sorted_lectures_df = filtered_lectures_df
        self.gpa_dict = gpa_dict
        self.rating_dict = rating_dict
        self.difficulty_dict = difficulty_dict
        self.would_take_again_dict = would_take_again_dict
        self.prereq_freq_dict = prereq_freq_dict
    
    def get_avg_score(self):
        self.sorted_lectures_df['instructors'] = self.sorted_lectures_df['instructors'].apply(lambda x: x[0] if x else None)
        # Convert dictionaries to Series for vectorized operations
        gpa_series = pd.Series(self.gpa_dict)
        rating_series = pd.Series(self.rating_dict)
        difficulty_series = pd.Series(self.difficulty_dict)
        would_take_again_series = pd.Series(self.would_take_again_dict)
        prereq_freq_series = pd.Series(self.prereq_freq_dict)

        # Initialize score and div as zero
        self.sorted_lectures_df['score'] = 0
        div = 0

        # Update score and div based on sorting parameters
        if "avg gpa" in self.sorting_parameters:
            self.sorted_lectures_df['score'] += self.sorted_lectures_df['instructors'].map(gpa_series).fillna(2)
            div += 1
        if "avg rating" in self.sorting_parameters:
            self.sorted_lectures_df['score'] += self.sorted_lectures_df['instructors'].map(rating_series).fillna(2.5)
            div += 1
        if "avg difficulty" in self.sorting_parameters:
            self.sorted_lectures_df['score'] -= self.sorted_lectures_df['instructors'].map(difficulty_series).fillna(2.5)
            div += 1
        if "would take again" in self.sorting_parameters:
            self.sorted_lectures_df['score'] += self.sorted_lectures_df['instructors'].map(would_take_again_series).fillna(50)
            div += 1
        if "prereq frequency" in self.sorting_parameters:
            self.sorted_lectures_df['score'] += self.sorted_lectures_df['course'].map(prereq_freq_series).fillna(0)
            div += 1

        # Calculate average score
        self.sorted_lectures_df['score'] /= div
        # for index, row in self.sorted_lectures_df.iterrows():
        #     course = row["course"]
        #     instructor = row["instructors"][0]
        #     score = 0
        #     div = 0
        #     if "avg gpa" in self.sorting_parameters and instructor in self.gpa_dict.keys():
        #         score += self.gpa_dict[instructor] 
        #         div += 1
        #     if "avg rating" in self.sorting_parameters and instructor in self.rating_dict.keys():
        #         score += self.rating_dict[instructor]
        #         div += 1
        #     if "avg difficulty" in self.sorting_parameters and instructor in self.difficulty_dict.keys():
        #         score -= self.difficulty_dict[instructor]
        #         div += 1
        #     if "would take again" in self.sorting_parameters and instructor in self.would_take_again_dict.keys():
        #         score += self.would_take_again_dict[instructor]
        #         div += 1
        #     if "prereq frequency" in self.sorting_parameters and course in self.prereq_freq_dict.keys():
        #         score += self.prereq_freq_dict[course]
        #         div += 1
            # self.sorted_lectures_df.at[index, "score"] = score/div
    
    def sort(self) -> None:
        self.get_avg_score()
        self.sorted_lectures_df = self.sorted_lectures_df.sort_values(by=['score'], ascending=False)
if __name__ == "__main__":
    WEBCAT_BASE_URL = "https://catalogue.uci.edu/donaldbrenschoolofinformationandcomputersciences/departmentofcomputerscience/computerscience_bs/#requirementstext"

    APISOC_BASE_URL = "https://api.peterportal.org/rest/v0/schedule/soc"
    APIPREREQ_BASE_URL = "https://api.peterportal.org/rest/v0/courses"

    compiler = Compiler.Compiler(WEBCAT_BASE_URL, APISOC_BASE_URL, APIPREREQ_BASE_URL)
    compiler.set_quarter("Fall")
    compiler.compile_everything()
    filter = Filter.Filter(lectures_df=compiler.get_lectures_df(), labs_df=compiler.get_labs_df(), discussions_df=compiler.get_discussions_df(), course_prereqs=compiler.get_course_prereqs(), taken_courses=['MATH 2A', 'AP CALCULUS AB', "AP CALCULUS BC","MATH 2B"])
    filter.filter_out_prereqs()
    sorting = Sorting_Compiler.Sorting_Compiler(filtered_lectures_df= filter.get_filtered_lectures_df(), apigpa_url = "https://api.peterportal.org/rest/v0/grades/raw")
    sorting.compile_all_avg_gpa()
    sorting.compile_all_rmp_course_info()
    sorted = Sorter(sorting_parameters=["avg gpa", "avg rating", "avg difficulty", "would take again", "prereq frequency"], filtered_lectures_df=sorting.get_filtered_lectures_df(), gpa_dict=sorting.get_gpa_dict(), rating_dict=sorting.get_rating_dict(), difficulty_dict=sorting.get_difficulty_dict(), would_take_again_dict=sorting.get_would_take_again_dict(), prereq_freq_dict=compiler.get_prereq_freq())
    sorted.sort()
    print(sorted.sorted_lectures_df[['course', 'instructors', 'score']])


    