import sqlite3
import Compiler as compiler

class CourseLabSorter:
    def __init__(self, compiler: compiler.Compiler):
        self.lectures = compiler.get_lectures_list()
        self.labs = compiler.get_labs_list()
        self.discussions = compiler.get_discussions_list()
        self.database_file = 'soc_database.db'
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()

    def create_columns_and_table(self) -> None:

        lecture_cols = sorter.create_lecture_columns()
        self.add_labs_to_corre_course(lecture_cols)
        self.add_discussions_to_corre_course(lecture_cols)
        self.create_table(lecture_cols)
    
    def create_lecture_columns(self) -> dict:
        """Iterates through lectures lists and creates dictionaries key = course name and value is section num"""

        lecture_cols = {}
        for lecture in self.lectures:
            course_name = lecture.get('course')   
            section_num = lecture.get('sectionNum')
            lecture_cols[(course_name, section_num)] = ([], [])

        return lecture_cols
    
    def add_labs_to_corre_course(self, lecture_cols: dict) -> None:
        """Iterates through labs and lectures list and """

        for lab in self.labs:
            corre_course_name = lab.get('course')
            section_num = lab.get('sectionNum')
            lecture_section_num = section_num[0]
            if (corre_course_name, lecture_section_num) in lecture_cols:
                for key in lecture_cols.keys():
                    if key[1] == lecture_section_num and key[0] == corre_course_name:
                        lecture_cols[key][0].append(section_num)


    def add_discussions_to_corre_course(self, lecture_cols: dict) -> None:

        for discussion in self.discussions:
            corre_course_name = discussion.get('course')
            section_num = discussion.get('sectionNum')
            if len(section_num) == 1:
                lecture_section_num = section_num[0]
            else:
                lecture_section_num = section_num[0] if section_num[0].isalpha() else section_num[1]
            if (corre_course_name, lecture_section_num) in lecture_cols:
                for key in lecture_cols.keys():
                    if key[1] == lecture_section_num and key[0] == corre_course_name:
                        lecture_cols[key][1].append(section_num)



    def fill_none(self, lecture_cols: dict) -> None:
        """Fills in the missing lab and discussion sections with None"""

        for key in lecture_cols.keys():
            if len(lecture_cols[key][0]) == 0:
                lecture_cols[key][0].append('N/A')
            if len(lecture_cols[key][1]) == 0:
                lecture_cols[key][1].append('N/A')

    def create_table(self, lecture_cols: dict) -> None:

        self.fill_none(lecture_cols)
        delete_table_statement = "DROP TABLE IF EXISTS courses"
        self.cursor.execute(delete_table_statement)

        create_table_statement = 'CREATE TABLE IF NOT EXISTS courses (course_name TEXT, lecture_section_num TEXT, lab_section_num TEXT, discussion_section_num TEXT, UNIQUE(course_name, lecture_section_num))'
        self.cursor.execute(create_table_statement)

        for (course_name, lecture_section_num), (lab_section_nums, discussion_section_nums)  in lecture_cols.items():
            lab_section_nums_str = ', '.join(lab_section_nums)
            discussion_section_nums_str = ', '.join(discussion_section_nums)
            insert_statement = f"INSERT OR IGNORE INTO courses VALUES ('{course_name}', '{lecture_section_num}', '{lab_section_nums_str}', '{discussion_section_nums_str}')"
            self.cursor.execute(insert_statement)

        self.connection.commit()
        self.cursor.execute('SELECT * FROM courses')
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)
        self.connection.close()


if __name__ == "__main__":
    comp = compiler.Compiler(compiler.WEBCAT_BASE_URL, compiler.APISOC_BASE_URL, compiler.APIPREREQ_BASE_URL)
    comp.set_quarter("Fall")
    comp.compile_everything()
    sorter = CourseLabSorter(comp)
    sorter.create_columns_and_table()