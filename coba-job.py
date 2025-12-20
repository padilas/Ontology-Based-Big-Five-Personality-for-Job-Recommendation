from owlready2 import *

onto = get_ontology("jobs.owl").load()

def get_job_requirements(job_name):
    job_class = onto[job_name]
    if not job_class:
        return None, None

    hard_skills = []
    soft_skills = []

    for prop in job_class.is_a:
        if isinstance(prop, Restriction):
            if prop.property == onto.requiresHardSkill:
                if hasattr(prop, "value") and prop.value:
                    hard_skills.append(prop.value.name)
            elif prop.property == onto.requiresSoftSkill:
                if hasattr(prop, "value") and prop.value:
                    soft_skills.append(prop.value.name)
    
    return hard_skills, soft_skills


pilihan_job = "DataAnalyst"
h_req, s_req = get_job_requirements(pilihan_job)

print(f"--- DAFTAR SKILL UNTUK {pilihan_job} ---")
print("Silakan centang skill yang Anda miliki:")

print("\n[Hard Skills]")
for i, s in enumerate(h_req):
    print(f"[{i}] {s}")

print("\n[Soft Skills]")
for i, s in enumerate(s_req):
    print(f"[{i+len(h_req)}] {s}")

user_checked_indices = [0, 1, 4] 
all_skills = h_req + s_req
user_has_skills = [all_skills[idx] for idx in user_checked_indices]

with onto:
    ace = onto.Ace
    ace.hasHardSkill = []
    ace.hasSoftSkill = []
    
    for s_name in user_has_skills:
        skill_individual = onto[s_name]
        # Masukkan ke properti yang sesuai di ontologi
        if isinstance(skill_individual, onto.HardSkill):
                ace.hasHardSkill.append(skill_individual)
        elif isinstance(skill_individual, onto.SoftSkill):
                ace.hasSoftSkill.append(skill_individual)
                
print("\n--- BERHASIL DISIMPAN ---")
print(f"Skill Ace sekarang di Ontologi: {[s.name for s in ace.hasHardSkill + ace.hasSoftSkill]}")