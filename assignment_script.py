# %%
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.cluster import KMeans
import owlready2 as owl
import numpy as np
import random
import names
ONTOLOGY_FILE = "./dev_ontology.owl"
ONTOLOGY_FILE2 = "./ultimate_ontology.owl"



# %%
onto = owl.get_ontology(ONTOLOGY_FILE2)
onto.load()

all_topics = onto.Topic.instances()
all_courses = onto.Course.instances()
no_topics = len(all_topics)
no_courses = len(all_courses)
prep_topic_to_idx = {topic.name: idx for idx, topic in enumerate(all_topics)}
prep_idx_to_topic = {prep_topic_to_idx[topic]: topic for topic, idx in prep_topic_to_idx.items()}
X = np.zeros([no_courses, no_topics])

for idx, course in enumerate(all_courses):
    for topic in course.covers:
        X[idx, prep_topic_to_idx[topic.name]] = 1

Xdf = pd.DataFrame(X, index=[course.name for course in all_courses], columns=[topic.name for topic in all_topics])
no_clusters = 21
kmeans = KMeans(no_clusters)
kmeans.fit(Xdf)
# %%
all_courses = onto.search(type=onto.Course)
all_hobbies = onto.search(type=onto.Hobby)
all_RM = onto.search(type=onto.ResearchMethodology)
onto_social_courses = onto.search(type=onto.SocialCourse)

# %%
for course in all_courses:
    print("================")
    print(course)
    print(course.isTaughtOnPeriod)
    print(len(course.isTaughtOnPeriod))
    if len(course.isTaughtOnPeriod) == 0:
        course.isTaughtOnPeriod.append(np.random.choice(all_periods))


# %%
for course in all_courses:
    len_property_items = len(course.uses)
    print(f"======== {len_property_items} items ========")
    if len_property_items == 0:
        random = np.random.choice(all_RM)
        print(f"{course}: {course.uses} items - Assigning: {random}")
        course.uses.append(random)
    else:
        print(course.uses)

# %%
# TODO: All courses need 2 Weekdays
import random
all_courses = onto.search(type=onto.Course)
all_weekdays = onto.search(type=onto.Weekday)
for course in all_courses:
    len_property_items = len(course.isTaughtOnWeekday)
    print(f"======== {len_property_items} items ========")
    if len_property_items < 3:
        random_days = random.sample(all_weekdays, 2-len_property_items)
        print(f"{course}: {course.isTaughtOnWeekday} items - Assigning: {random_days}")
        course.isTaughtOnWeekday.extend(random_days)
    else:
        print(course.isTaughtOnWeekday)

# %%
# TODO: All hobbies need a day
import random
all_hobbies = onto.search(type=onto.Hobby)
all_weekdays = onto.search(type=onto.Weekday)
for hobby in all_hobbies:
    len_property_items = len(hobby.isPracticedOnWeekday)
    print(f"======== {len_property_items} items ========")
    if len_property_items < 1:
        random_days = np.random.choice(all_weekdays)
        print(f"{hobby}: {hobby.isPracticedOnWeekday} items - Assigning: {random_days}")
        hobby.isPracticedOnWeekday.append(random_days)
    else:
        print(hobby.isPracticedOnWeekday)
# %%
# import mca


def return_topics_from_course_vector(idx, data, mapping):
    return [mapping[x] for x in data[1].nonzero()[0]]


all_topics = onto.Topic.instances()
all_courses = onto.Course.instances()
no_topics = len(all_topics)
no_courses = len(all_courses)
prep_topic_to_idx = {topic.name: idx for idx, topic in enumerate(all_topics)}
prep_idx_to_topic = {prep_topic_to_idx[topic]: topic for topic, idx in prep_topic_to_idx.items()}
X = np.zeros([no_courses, no_topics])

for idx, course in enumerate(all_courses):
    for topic in course.covers:
        X[idx, prep_topic_to_idx[topic.name]] = 1

Xdf = pd.DataFrame(X, index=[course.name for course in all_courses], columns=[topic.name for topic in all_topics])
no_clusters = 21
kmeans = KMeans(no_clusters)
kmeans.fit(Xdf)

for idx in range(no_clusters):
    print([all_courses[course_idx] for course_idx in np.where(kmeans.labels_ == idx)[0]])

#%%
import names

no_of_required_teachers = len(range(30)) 
if len(onto.Teacher.instances()) < no_of_required_teachers:
    for num in range(len(onto.Teacher.instances()), no_of_required_teachers):
        temp_teacher = onto.Teacher(f"Teacher{num+1}")
        temp_teacher.firstName.append(names.get_first_name())
        temp_teacher.secondName.append(names.get_last_name())
        temp_teacher.teacherID.append(num)
        print(temp_teacher)
else:
    print("Not necessary to add a Teacher")
# TODO: Teachers and their subjects per period
import numpy as np
all_periods = onto.search(type=onto.Period)
all_teachers = onto.search(type=onto.Teacher)
all_courses = onto.search(type=onto.Course)
# for i in range(6):
for period in all_periods:
    for teacher in all_teachers:
        # if len(teacher.teaches) > 3:
        #     break
        prefix = f"Teacher {teacher.name}: "
        print(prefix + f"For period {period.name}")
        if len(teacher.teaches) < 4:
            print(prefix + f"Needs to teach an additional course")
            if (period not in [p.name for course in teacher.teaches for p in course.isTaughtOnPeriod]):
                print(prefix + f"Will pick a course for period {period.name}")
                if len(teacher.teaches) < 1:
                    print(prefix + "Pick random")
                    picked_course = np.random.choice(all_courses)
                    print(prefix + f"Picked => {picked_course}")
                    teacher.teaches.append(picked_course)
                else:
                    random_course_of_teacher = np.random.choice(teacher.teaches).name
                    print(prefix + f"Pick nearest of random for: '{random_course_of_teacher}'")
                    picked_courses = [all_courses[course_idx] for course_idx in np.where(kmeans.labels_ == kmeans.predict(Xdf.loc[[random_course_of_teacher]])[0])[0]]
                    print(teacher.teaches)
                    print(picked_courses[0].isTaughtOnPeriod)
                    filtered_courses = set(picked_courses) - set(teacher.teaches)
                    print(filtered_courses)
                    isBusyOn = [p for x in teacher.teaches for p in x.isTaughtOnPeriod]
                    filtered_courses = [c for c in picked_courses if c.isTaughtOnPeriod[0] not in isBusyOn]
                    print(filtered_courses)
                    print(prefix + f"These are the candidate courses {picked_courses}")
                    if len(filtered_courses):
                        picked_course = np.random.choice(filtered_courses)
                        print(prefix + f"Picked => {picked_course}")
                        teacher.teaches.append(picked_course)
                    else:
                        print(prefix + f"Couldn't set a course!")


# %%
# TODO: Generate Students up to ten students
no_of_required_students = len(range(30)) 
all_courses = onto.Course.instances()
all_hobbies = onto.Hobby.instances()
all_students = onto.Student.instances()

if len(onto.Student.instances()) < no_of_required_students:
    for num in range(len(onto.Student.instances()), no_of_required_students):
        # picked_courses = [all_courses[course_idx] for course_idx in np.where(kmeans.labels_ == kmeans.predict(Xdf.loc[[random_course_of_teacher]])[0])[0]]
        temp_student = onto.Student(f"Student{num+1}")
        temp_student.firstName.append(names.get_first_name())
        temp_student.secondName.append(names.get_last_name())
        temp_student.studentID.append(num)
        print(temp_student)
else:
    print("Not necessary to add a Student")


#%%
all_courses = onto.Course.instances()
all_students = onto.Student.instances()

for temp_student in all_students:
    if len(onto.Student.hasTaken) < 1:
        took = random.sample(all_courses, 1)

        # temp_student.hasTaken.append(took[0])
        print(f"Student has taken: {took[0]}")



#%%

all_courses = onto.Course.instances()
all_hobbies = onto.Hobby.instances()
all_students = onto.Student.instances()
temp_student = all_students[1]
for temp_student in all_students:
    # temp_student.hasTaken
    try:
        predicted_courses = kmeans.predict(Xdf.loc[Xdf.index==temp_student.hasTaken[0].name])[0]
        get_group = np.where(kmeans.labels_ == predicted_courses)
        if len(get_group):
            candidate_courses = get_group[0]
            candidate_courses_labelled = [all_courses[idx] for idx in candidate_courses]
            print(f"Student {temp_student.name}: with {temp_student.hasTaken[0]} has following candidate courses {candidate_courses_labelled}")
            selected_courses_taken = random.sample(candidate_courses_labelled, random.randrange(2))
            print(f"Took: {selected_courses_taken}")
            temp_student.hasTaken.extend(selected_courses_taken)
    except Exception as e:
        print(e)


#%%
all_courses = onto.Course.instances()
all_hobbies = onto.Hobby.instances()
all_students = onto.Student.instances()
temp_student = all_students[1]
for temp_student in all_students:
    # temp_student.hasTaken
    candidate_friends = set(random.sample(all_students, random.randrange(2))) - set([temp_student])
    print(f"Student {temp_student.name}: has {candidate_friends} as friends")
    # print(f"Took: {selected_courses_taken}")
    temp_student.hasFriend.extend(candidate_friends)

# =================================================================
# %%
onto.save(file="ultimate_ontology.owl", format="rdfxml")

# %%
