from owlready2 import *
import warnings

warnings.filterwarnings("ignore")
print("\033c")

# path to the wine ontology
onto = get_ontology("./model.owl")
onto.load()

with onto:
    sync_reasoner(infer_property_values=True)

with onto:
    class prop(ObjectProperty): pass
    class Weekday(Thing): pass

print(Weekday().prop)

print("-" * 60)
# Wine and hasBody value Medium
# onto.Wine & onto.hasBody.value(Medium)
try:
    student = onto.search(is_a=onto.Student)
    for w in student:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

stud1 = onto.Student1.get_properties()
    #for w in stud1:
print(stud1)
print(type(onto.Student))

print("-" * 60)

#array_stud = [onto.search(is_a=onto.Student)]
for stud in student[1:]:
    for prop in stud.get_properties():
        for value in prop[stud]:
            print("Student:", stud, prop, ": ", value)

print("-" * 60)

stud1 = student[1]

AdvCourses = onto.search(is_a=onto.AdvancedCourse)[1:]

for course in stud1.hasTaken:
    l = [i for i in AdvCourses if course in i.hasPreliminary]

print("Student {} {} can take advanced courses: ".format(stud1.firstName[0], stud1.secondName[0]), l)

print("-" * 60)

print("Studen has skills: ", stud1.hasSkill)
print("Student is busy on: ", stud1.isBusyOn)

print("-" * 60)

stud2 = student[2]

print(Weekday("Mo"))

newcourse = onto.Course("DataMining")

stud2.takes.append(newcourse)

print(stud2.takes)

print("-" * 60)
