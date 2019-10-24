#%%
import owlready2 as owl
import numpy as np
ONTOLOGY_FILE   = "./dev_ontology.owl"
ONTOLOGY_FILE2   = "./ultimate_ontology.owl"


#%%
onto = owl.get_ontology(ONTOLOGY_FILE2)
onto.load()

#%%
all_courses = onto.search(type=onto.Course)
all_periods = onto.search(type=onto.Period)
all_hobbies = onto.search(type=onto.Hobby)
all_RM = onto.search(type=onto.ResearchMethodology)
onto_social_courses = onto.search(type=onto.SocialCourse)

#%%
for course in all_courses:
    print("================")
    print(course)
    print(course.isTaughtOnPeriod)
    print(len(course.isTaughtOnPeriod))
    if len(course.isTaughtOnPeriod) == 0:
        course.isTaughtOnPeriod.append(np.random.choice(all_periods))

#%%
for course in all_courses:
    len_property_items = len(course.uses)
    print(f"======== {len_property_items} items ========")
    if len_property_items == 0:
        random = np.random.choice(all_RM)
        print(f"{course}: {course.uses} items - Assigning: {random}")
        course.uses.append(random)
    else:
        print(course.uses)

#%%
# onto.save(file = "ultimate_ontology.owl", format = "rdfxml")
no_of_required_teachers = len(onto.Course.instances())//5
if len(onto.Teacher.instances()) <= no_of_required_teachers:
    print(f"Not enough teachers")

#%%
from sklearn.cluster import KMeans
import numpy as np
# import mca
import pandas as pd

def return_topics_from_course_vector(idx, data, mapping):
    return [mapping[x] for x in data[1].nonzero()[0]]

all_topics = onto.Topic.instances()
all_courses = onto.Course.instances()
no_topics = len(all_topics)
no_courses = len(all_courses)
prep_topic_to_idx = {topic.name:idx for idx,topic in enumerate(all_topics)}
prep_idx_to_topic = {prep_topic_to_idx[topic]:topic for topic,idx in prep_topic_to_idx.items()}
X = np.zeros([no_courses,no_topics])

for idx, course in enumerate(all_courses):
    for topic in course.covers:
        X[idx, prep_topic_to_idx[topic.name]] = 1
#%%
return_topics_from_course_vector(1, X, prep_idx_to_topic)

#%%
Xdf = pd.DataFrame(X, index=[course.name for course in all_courses], columns=[topic.name for topic in all_topics])

#%%
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
kmeans = KMeans(17)
kmeans.fit(Xdf)
# print(kmeans.predict(X[1]))
#%%


#%%
# group2 = 
# print(group2)
[all_courses[course_idx] for course_idx in np.where(kmeans.labels_ == 2)[0]]
#%%
