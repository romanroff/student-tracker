import json
import os

class Course():
    def __init__(self, name, students=None, topics=None):
        self.name = name
        self.students = students if students is not None else []
        self.topics = topics if topics is not None else []
    
    def add_student(self, student: str):
        if student not in self.students:
            self.students.append(student)
        else:
            print(f"{student} is already in {self.name}")

    def remove_student(self, student: str):
        if student in self.students:
            self.students.remove(student)
        else:
            print(f'{student} is not in {self.name}')

    def get_all_students(self):
        sorted_students = sorted(self.students)
        for index, name in enumerate(sorted_students):
            print(f'{index + 1}. {name}')

    def add_topic(self, name: str, type: str, max_score: str):
        topic_dict = {}
        topic_dict['topic_name'] = name
        type = type.lower()
        if type == 'lecture' or type== 'practice':
            topic_dict['topic_type'] = type
        else:
            topic_dict['topic_type'] = None
            print('There is no such type!')
        topic_dict['topic_max_score'] = max_score
        self.topics.append(topic_dict)

    def get_all_topics(self) -> list[dict]:
        return self.topics
    
    def save_to_file(self, filename: str):
        data = {}
        data['name'] = self.name
        data['students'] = self.students
        data['topics'] = self.topics
        try:
            if os.path.exists(filename):
                with open(filename, 'w', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            else: 
                with open(filename, 'x', encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except PermissionError:
            print(f"Error: permission denied to write to {filename}.")
        except IOError as e:
            print(f"Input/Output error: {e}")

    def load_from_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                student_dict = json.load(f) 
                self.name = student_dict.get('name', None)
                self.students = student_dict.get('students', [])
                self.topics = student_dict.get('topics', [])
            print("Data successfully loaded from the file.")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except PermissionError:
            print(f"Error: Permission denied to read the file '{filename}'.")
        except json.JSONDecodeError as e:
            print(f"Error: The file '{filename}' contains invalid JSON. Details: {e}")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    from utils import read_students_from_file
    
    PATH = 'data/students_list.txt'
    students = read_students_from_file(PATH)
    tracker = Course(name ='Python for beginners', 
                     students=students)
    tracker.get_all_students()    

        