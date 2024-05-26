from flask import Flask, jsonify
from flask_cors import CORS
import Sorter, Sorting_Compiler, Compiler, Filter

app = Flask(__name__)
CORS(app)

@app.route('/api/data', methods=['GET'])
def get_data():
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

    
    sorted = Sorter.Sorter(sorting_parameters=["avg gpa", "avg rating", "avg difficulty", "would take again", "prereq frequency"], filtered_lectures_list=sorting.get_filtered_lectures_list(), gpa_dict=sorting.get_gpa_dict(), rating_dict=sorting.get_rating_dict(), difficulty_dict=sorting.get_difficulty_dict(), would_take_again_dict=sorting.get_would_take_again_dict(), prereq_freq_dict=compiler.get_prereq_freq())
    sorted.sort_list()

    data = sorted.get_sorted_lectures_list()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5001)