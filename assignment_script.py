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
    len_property_items = len(course.uses)
    print(f"======== {len_property_items} items ========")
    if len_property_items == 0:
        random = np.random.choice(all_RM)
        print(f"{course}: {course.uses} items - Assigning: {random}")
        course.uses.append(random)
    else:
        print(course.uses)

#%%
onto.save(file = "ontology_with_all_periods_set.owl", format = "rdfxml")

#%%
merged_hobbies_onto = owl.get_ontology("./MERGEDHOBBIES.owl")
merged_hobbies_onto.load()
all_social_courses_from_merged = merged_hobbies_onto.search(iri="*SocialCourse")[0].instances()

#%%
onto_social_courses = onto.search(type=onto.SocialCourse)
#%%
onto_social_courses.extend(all_social_courses_from_merged)
# onto.save(file = "merged.owl", format = "rdfxml")


#%%
