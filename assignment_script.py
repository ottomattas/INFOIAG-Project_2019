#%%
import owlready2 as owl
import numpy as np
ONTOLOGY_FILE   = "./merged_ontology.owl"


#%%
onto = owl.get_ontology(ONTOLOGY_FILE)
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
onto.save(file = "ultimate_ontology.owl", format = "rdfxml")

