from owlready2 import *

onto = get_ontology("jobs.owl").load()

with onto:
    ace = onto.Ace
    ace.hasOpennessScore = [4.8]
    ace.hasConscientiousnessScore = [4.2]
    ace.hasExtraversionScore = [2.0]

    active_traits = []
    if ace.hasOpennessScore[0] >= 3.0:
        ace.hasMatchCategory.append(onto.OpennessTrait)
        active_traits.append(onto.OpennessTrait)
    if ace.hasConscientiousnessScore[0] >= 3.0:
        ace.hasMatchCategory.append(onto.ConscientiousnessTrait)
        active_traits.append(onto.ConscientiousnessTrait)

    recommended_jobs = []
    
    all_jobs = list(onto.JobOccupation.subclasses())
    
    for job_class in all_jobs:
        for trait in active_traits:
            if trait in job_class.hasMatchCategory:
                if job_class.name not in recommended_jobs:
                    recommended_jobs.append(job_class.name)

print(f"=== REKOMENDASI UNTUK {ace.name.upper()} ===")
print(f"Trait Aktif: {[t.name for t in active_traits]}")
print(f"Pekerjaan yang ditarik otomatis dari Ontologi:")
for job in recommended_jobs:
    print(f"-> {job}")