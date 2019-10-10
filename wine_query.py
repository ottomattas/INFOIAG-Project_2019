from owlready2 import *

# path to the wine ontology
onto = get_ontology("/home/sorin/Desktop/Intelligent Agents/Files/wine.rdf")
onto.load()

sync_reasoner()

# Wine and hasBody value Medium
# onto.Wine & onto.hasBody.value(Medium)
try:
    white_wines = onto.search(is_a=onto.WhiteWine)
    for w in white_wines:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

try:
    fullBody_wines = onto.search(is_a=onto.Wine & onto.WineBody.value(Full))
    for w in fullBody_wines:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

try:
    red_wines = onto.search(type=onto.Wine & onto.Wine.hasColor.value(Red))
    for w in red_wines:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

try:
    print(onto.hasWineDescriptor.get_relations())
except Exception as e:
    print(e)

print("-" * 60)

try:
    fullBody_wines = onto.search(is_a=onto.Wine, hasBody=onto.search(is_a=onto.WineBody))
    for w in fullBody_wines:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

try:
    fullBody_wines = onto.search(hasBody="*Full")
    for w in fullBody_wines:
        print(w)
except Exception as e:
    print(e)

print("-" * 60)

try:
    for i in onto.RedWine.instances(): print(i)
except Exception as e:
    print(e)

print("-" * 60)
