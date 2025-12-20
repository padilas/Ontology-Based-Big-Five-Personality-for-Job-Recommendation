from owlready2 import *

onto = get_ontology("jobs.owl").load()

def calculate_compatibility(target_job_name, user_checked_skills, user_personality_scores):
    job_class = onto[target_job_name]
    if not job_class:
        return "Job tidak ditemukan"

    required_hard = []
    required_soft = []
    
    for prop in job_class.is_a:
        if isinstance(prop, Restriction):
            if prop.property == onto.requiresHardSkill:
                required_hard.append(prop.value.name)
            elif prop.property == onto.requiresSoftSkill:
                required_soft.append(prop.value.name)
    
    all_req_skills = required_hard + required_soft
    matched_skills = [s for s in user_checked_skills if s in all_req_skills]
    
    skill_score = (len(matched_skills) / len(all_req_skills)) * 100 if all_req_skills else 0

    # --- B. PERSONALITY MATCHING ---
    # Tarik trait yang dibutuhkan job dari mapping hasMatchCategory yang kita buat tadi
    required_traits = []
    for trait in job_class.hasMatchCategory:
        required_traits.append(trait.name) 

    relevant_scores = []
    for t in required_traits:
        if t in user_personality_scores:
            relevant_scores.append(user_personality_scores[t])
    
    if relevant_scores:
        avg_p_score = sum(relevant_scores) / len(relevant_scores)
        personality_score = (avg_p_score / 5.0) * 100
    else:
        personality_score = 0

    # --- C. FINAL SCORE (Weighting) ---
    final_score = (0.5 * skill_score) + (0.5 * personality_score)
    
    return {
        "job": target_job_name,
        "skill_match": round(skill_score, 2),
        "personality_match": round(personality_score, 2),
        "final_compatibility": round(final_score, 2),
        "matched_list": matched_skills,
        "required_traits": required_traits
    }

# --- SIMULASI PENGGUNAAN ---

target = "DataScientist"

user_skills = ["SQLSkill", "PythonSkill", "CriticalThinkingSkill"] 

user_scores = {
    "OpennessTrait": 4.8,
    "ConscientiousnessTrait": 4.2,
    "ExtraversionTrait": 2.5,
    "AgreeablenessTrait": 3.0,
    "NeuroticismTrait": 2.0
}

result = calculate_compatibility(target, user_skills, user_scores)

print(f"=== HASIL EVALUASI KANDIDAT: {target} ===")
print(f"Skill Match: {result['skill_match']}% (Cocok: {', '.join(result['matched_list'])})")
print(f"Personality Match: {result['personality_match']}% (Berdasarkan: {', '.join(result['required_traits'])})")
print("-" * 40)
print(f"SKOR TOTAL KECOCOKAN: {result['final_compatibility']}%")

if result['final_compatibility'] >= 75:
    print("KESIMPULAN: Anda SANGAT COCOK untuk posisi ini!")
elif result['final_compatibility'] >= 50:
    print("KESIMPULAN: Anda CUKUP COCOK, pertimbangkan untuk menambah skill.")
else:
    print("KESIMPULAN: Pekerjaan ini mungkin kurang pas dengan profil Anda.")