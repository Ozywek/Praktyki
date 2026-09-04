class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def average(self):
        return sum(self.grades) / len(self.grades)

    def has_passed(self):
        if self.average() > 3:
            return True
        else:
            return False
#
# def DO_SPYTANIA(students):
#     passed = []
#     for i in students:
#         if i.has_passed() == True:
#             passed.append(i)
#     return passed

def student_names(students):
    names = []
    for i in students:
        names.append(i)
    return names


students = [
    Student("Adam", [5, 4, 3]),
    Student("Bartek", [2, 2, 3]),
    Student("Kasia", [5, 5, 4]),
    Student("Ola", [3, 2, 2]),
]



