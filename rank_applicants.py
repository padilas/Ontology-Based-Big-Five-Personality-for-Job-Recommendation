#!/usr/bin/env python3
"""
Rank applicants based on job fit:
- Personality match (Big Five scores)
- Skills match (required hard/soft skills)
- Experience (years in field)
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from collections import defaultdict

# Define namespace
ONTO = Namespace("http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/recruitment-ontology#")

# Ideal Big Five profiles for jobs (based on research)
JOB_PERSONALITY_PROFILES = {
    'DataScientist': {
        'Agreeableness': 3.5,
        'Conscientiousness': 4.5,
        'Extraversion': 3.0,
        'Neuroticism': 2.0,
        'Openness': 5.0
    },
    'DataAnalyst': {
        'Agreeableness': 4.0,
        'Conscientiousness': 4.5,
        'Extraversion': 3.0,
        'Neuroticism': 2.0,
        'Openness': 4.5
    },
    'MarketingManager': {
        'Agreeableness': 4.0,
        'Conscientiousness': 4.0,
        'Extraversion': 4.5,
        'Neuroticism': 2.0,
        'Openness': 4.5
    },
    'SoftwareEngineer': {
        'Agreeableness': 3.5,
        'Conscientiousness': 4.5,
        'Extraversion': 3.0,
        'Neuroticism': 2.0,
        'Openness': 4.5
    }
}

def load_ontology(file_path):
    """Load the ontology from TTL file."""
    print(f"Loading ontology from {file_path}...")
    g = Graph()
    g.parse(file_path, format='turtle')
    print(f"Loaded {len(g)} triples\n")
    return g

def get_applications(g):
    """Get all Application individuals."""
    applications = []
    for app in g.subjects(RDF.type, ONTO.Application):
        app_data = {}
        
        # Get applicant
        for applicant in g.objects(app, ONTO.hasApplicant):
            app_data['applicant'] = applicant
            app_data['applicant_name'] = str(applicant).split('#')[-1]
        
        # Get job
        for job in g.objects(app, ONTO.forJob):
            app_data['job'] = job
            app_data['job_name'] = str(job).split('#')[-1]
        
        if 'applicant' in app_data and 'job' in app_data:
            applications.append(app_data)
    
    return applications

def get_person_scores(g, person):
    """Get Big Five scores for a person."""
    scores = {}
    
    score_properties = {
        'Agreeableness': ONTO.hasAgreeablenessScore,
        'Conscientiousness': ONTO.hasConscientiousnessScore,
        'Extraversion': ONTO.hasExtraversionScore,
        'Neuroticism': ONTO.hasNeuroticismScore,
        'Openness': ONTO.hasOpennessScore
    }
    
    for trait, prop in score_properties.items():
        for score in g.objects(person, prop):
            scores[trait] = float(score)
    
    return scores

def get_person_skills(g, person):
    """Get skills for a person."""
    hard_skills = set()
    soft_skills = set()
    
    for skill in g.objects(person, ONTO.hasHardSkill):
        hard_skills.add(str(skill).split('#')[-1])
    
    for skill in g.objects(person, ONTO.hasSoftSkill):
        soft_skills.add(str(skill).split('#')[-1])
    
    return hard_skills, soft_skills

def get_person_experience(g, person):
    """Get experience years for a person."""
    for exp in g.objects(person, ONTO.hasExperience):
        for years in g.objects(exp, ONTO.yearsOfExperience):
            return int(years)
    return 0

def get_job_required_skills(g, job):
    """Get required skills for a job."""
    hard_skills = set()
    soft_skills = set()
    
    for skill in g.objects(job, ONTO.requiresHardSkill):
        hard_skills.add(str(skill).split('#')[-1])
    
    for skill in g.objects(job, ONTO.requiresSoftSkill):
        soft_skills.add(str(skill).split('#')[-1])
    
    return hard_skills, soft_skills

def calculate_personality_match(person_scores, job_profile):
    """
    Calculate personality match score (0-100).
    Lower difference = better match.
    """
    if not person_scores or not job_profile:
        return 0
    
    total_diff = 0
    trait_count = 0
    
    for trait, ideal_score in job_profile.items():
        if trait in person_scores:
            diff = abs(person_scores[trait] - ideal_score)
            # Normalize: max diff is 4 (5-1), convert to 0-1 scale
            normalized_diff = diff / 4.0
            total_diff += normalized_diff
            trait_count += 1
    
    if trait_count == 0:
        return 0
    
    # Average difference, then convert to match score (0-100)
    avg_diff = total_diff / trait_count
    match_score = (1 - avg_diff) * 100
    
    return round(match_score, 2)

def calculate_skills_match(person_hard, person_soft, job_hard, job_soft):
    """
    Calculate skills match score (0-100).
    Based on percentage of required skills that applicant has.
    """
    if not job_hard and not job_soft:
        return 100  # No requirements = perfect match
    
    total_required = len(job_hard) + len(job_soft)
    hard_matched = len(person_hard & job_hard)
    soft_matched = len(person_soft & job_soft)
    total_matched = hard_matched + soft_matched
    
    match_score = (total_matched / total_required) * 100 if total_required > 0 else 0
    
    return round(match_score, 2)

def calculate_experience_score(years):
    """
    Calculate experience score (0-100).
    0-2 years: 50-70
    3-5 years: 70-90
    6+ years: 90-100
    """
    if years <= 2:
        return 50 + (years * 10)
    elif years <= 5:
        return 70 + ((years - 2) * 6.67)
    else:
        return min(100, 90 + ((years - 5) * 2))

def rank_applicants(g, applications):
    """Rank all applicants for their jobs."""
    results = []
    
    for app_data in applications:
        person = app_data['applicant']
        job = app_data['job']
        person_name = app_data['applicant_name']
        job_name = app_data['job_name']
        
        print(f"=== Evaluating {person_name} for {job_name} ===")
        
        # Get person data
        person_scores = get_person_scores(g, person)
        person_hard, person_soft = get_person_skills(g, person)
        person_exp = get_person_experience(g, person)
        
        # Get job requirements
        job_hard, job_soft = get_job_required_skills(g, job)
        job_profile = JOB_PERSONALITY_PROFILES.get(job_name, None)
        
        # Calculate scores
        personality_match = calculate_personality_match(person_scores, job_profile) if job_profile else 0
        skills_match = calculate_skills_match(person_hard, person_soft, job_hard, job_soft)
        experience_score = calculate_experience_score(person_exp)
        
        # Weighted total score (40% personality, 40% skills, 20% experience)
        total_score = (personality_match * 0.4) + (skills_match * 0.4) + (experience_score * 0.2)
        
        print(f"  Personality Match: {personality_match:.2f}/100")
        print(f"    Applicant scores: {person_scores}")
        print(f"    Ideal profile: {job_profile}")
        print(f"  Skills Match: {skills_match:.2f}/100")
        print(f"    Has: {len(person_hard)} hard, {len(person_soft)} soft skills")
        print(f"    Required: {len(job_hard)} hard, {len(job_soft)} soft skills")
        print(f"  Experience Score: {experience_score:.2f}/100 ({person_exp} years)")
        print(f"  📊 TOTAL SCORE: {total_score:.2f}/100\n")
        
        results.append({
            'person_name': person_name,
            'job_name': job_name,
            'personality_match': personality_match,
            'skills_match': skills_match,
            'experience_score': experience_score,
            'total_score': total_score,
            'person_scores': person_scores,
            'experience_years': person_exp
        })
    
    return results

def determine_top_percentage(results, threshold=10):
    """Determine which applicants are in top X%."""
    # Sort by total score (descending)
    sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
    
    # Calculate top X% cutoff
    total_applicants = len(sorted_results)
    top_count = max(1, int(total_applicants * (threshold / 100)))
    
    print(f"\n{'='*60}")
    print(f"RANKING RESULTS (Top {threshold}%)")
    print(f"{'='*60}\n")
    
    for i, result in enumerate(sorted_results, start=1):
        is_top = i <= top_count
        marker = "🌟 TOP" if is_top else "  "
        
        print(f"{marker} Rank #{i}: {result['person_name']} → {result['job_name']}")
        print(f"     Score: {result['total_score']:.2f} | Personality: {result['personality_match']:.2f} | Skills: {result['skills_match']:.2f} | Experience: {result['experience_score']:.2f}")
        
        if is_top:
            print(f"     ✅ IN TOP {threshold}%")
        print()
    
    print(f"{'='*60}")
    print(f"Top {threshold}% cutoff: {top_count} out of {total_applicants} applicants")
    print(f"{'='*60}\n")
    
    return sorted_results[:top_count]

def main():
    # Load ontology with scores
    g = load_ontology('jobs_with_scores.ttl')
    
    # Get all applications
    applications = get_applications(g)
    print(f"Found {len(applications)} applications\n")
    
    if not applications:
        print("❌ No applications found. Make sure you have:")
        print("   1. Added applicants (add_applicant.py)")
        print("   2. Calculated scores (calculate_bigfive.py)")
        return
    
    # Rank applicants
    results = rank_applicants(g, applications)
    
    # Determine top 10%
    top_applicants = determine_top_percentage(results, threshold=10)
    
    print("\n=== RECOMMENDATION ===")
    for applicant in top_applicants:
        print(f"✅ HIRE: {applicant['person_name']} for {applicant['job_name']} (Score: {applicant['total_score']:.2f})")

if __name__ == '__main__':
    main()
