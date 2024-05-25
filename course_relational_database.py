import sqlite3

class CourseLabSorter:
    def __init__(self, lectures: list[dict], labs_and_discussions: list[dict]):
        self.lectures = lectures #list[dict] key=headings for all lectures
        self.labs_and_discussions = labs_and_discussions #key=headings for labs and discussions
        self.database_file = 'soc_database.db'
        self.connection = sqlite3.connect(self.database_file)
        self.cursor = self.connection.cursor()
    
    def create_lecture_columns(self) -> dict:
        """Iterates through lectures lists and creates dictionaries key = course name and value is section num"""

        lecture_cols = {}
        for lecture in self.lectures:
            course_name = lecture.get('correCourse')   
            section_num = lecture.get('sectionNum')
            lecture_cols[(course_name, section_num)] = []

        return lecture_cols
    
    def add_labs_to_corre_course(self, lecture_cols: dict) -> None:
        """Iterates through labs and lectures list and """

        for lab in self.labs_and_discussions:
            corre_course_name = lab.get('correCourse')
            section_num = lab.get('sectionNum')
            lecture_section_num = section_num[0]
            if (corre_course_name, lecture_section_num) in lecture_cols:
                for key in lecture_cols.keys():
                    if key[1] == lecture_section_num and key[0] == corre_course_name:
                        lecture_cols[key].append(section_num)

        print('corre cols', lecture_cols)

    def create_table(self, lecture_cols: dict) -> None:

        create_table_statement = 'CREATE TABLE IF NOT EXISTS courses (course_name TEXT, lecture_section_num TEXT, lab_section_nums TEXT, UNIQUE(course_name, lecture_section_num))'
        self.cursor.execute(create_table_statement)

        for (course_name, lecture_section_num), lab_section_nums in lecture_cols.items():
            lab_section_nums_str = ', '.join(lab_section_nums)
            insert_statement = f"INSERT OR IGNORE INTO courses VALUES ('{course_name}', '{lecture_section_num}', '{lab_section_nums_str}')"
            self.cursor.execute(insert_statement)

        self.connection.commit()
        self.cursor.execute('SELECT * FROM courses')
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)
        self.connection.close()

if __name__ == "__main__":
    lectures = [{'correCourse': 'ICS31', 'sectionNum': 'A'}, {'correCourse': 'ICS31', 'sectionNum': 'B'}, {'correCourse': 'ICS32', 'sectionNum': 'A'}]
    labs_and_discussions = [{'correCourse': 'ICS31', 'sectionNum': 'A1'}, {'correCourse': 'ICS31', 'sectionNum': 'A2'}, {'correCourse': 'ICS31', 'sectionNum': 'B1'}, {'correCourse': 'ICS32', 'sectionNum': 'A1'}]
    sorter = CourseLabSorter(lectures, labs_and_discussions)
    lecture_cols = sorter.create_lecture_columns()
    sorter.add_labs_to_corre_course(lecture_cols)
    sorter.create_table(lecture_cols)


