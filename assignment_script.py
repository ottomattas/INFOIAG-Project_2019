#%%
import owlready2 as owl
import numpy as np
ONTOLOGY_FILE   = "./ontology_with_all_periods_set.owl"


#%%
onto = owl.get_ontology(ONTOLOGY_FILE)
onto.load()

#%%
all_courses = onto.search(type=onto.Course)
all_periods = onto.search(type=onto.Period)
all_hobbies = onto.search(type=onto.Hobby)
all_RM = onto.search(type=onto.ResearchMethodology)

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
    print("================")
    print(course)
    print(course.improves)
    print(len(course.improves))
    if len(course.improves) == 0:
        course.improves.append(np.random.choice(all_RM))

#%%
onto.save(file = "ontology_with_all_periods_set.owl", format = "rdfxml")

#%%
