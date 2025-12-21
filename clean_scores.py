from owlready2 import get_ontology
import os

onto_path = os.path.abspath("jobs_with_scores.owl")
onto = get_ontology(f"file://{onto_path}").load()

float_props = [
    "hasCategoryFitScore",
    "hasSkillMatchScore",
    "hasExperienceScore",
    "hasWeightedScore",
]

with onto:
    for person in onto.Person.instances():
        for prop_name in float_props:
            if hasattr(person, prop_name):
                vals = getattr(person, prop_name)
                if vals:
                    try:
                        # take first, coerce to float, overwrite
                        val = float(vals[0])
                        setattr(person, prop_name, [val])
                    except Exception:
                        # drop bad value
                        setattr(person, prop_name, [])
        # years of experience keep as int if present
        if hasattr(person, "hasYearsOfExperience"):
            vals = person.hasYearsOfExperience
            if vals:
                try:
                    person.hasYearsOfExperience = [int(float(vals[0]))]
                except Exception:
                    person.hasYearsOfExperience = []

onto.save(file="jobs_with_scores.owl", format="rdfxml")

# Use rdflib export to ensure Turtle file is populated (owlready2's turtle saver can emit empty files)
graph = onto.world.as_rdflib_graph()
graph.serialize(destination="jobs_with_scores.ttl", format="turtle")

print("Cleaned and saved jobs_with_scores.owl and jobs_with_scores.ttl")
