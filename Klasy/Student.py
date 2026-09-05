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

def passing_students(students):
    passed = []
    for i in students:
        if i.has_passed() == True:
            passed.append(i.name)
    return passed

def best_student(students):
    biggest = sum(students[0].grades)/len(students[0].grades)
    name = students[0].name
    for i in students:
        if sum(i.grades)/len(i.grades) > biggest:
            biggest = sum(i.grades)/len(i.grades)
            name = i.name
    return biggest, name

def student_names(students):
    names = []
    for i in students:
        names.append(i.name)
    return names

students = [
    Student("Adam", [5, 4, 3]),
    Student("Bartek", [2, 2, 3]),
    Student("Kasia", [5, 5, 4]),
    Student("Ola", [3, 2, 2]),
]

print(student_names(students))
print(passing_students(students))
print(best_student(students))
