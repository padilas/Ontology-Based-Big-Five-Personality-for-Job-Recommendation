#!/usr/bin/env python3
"""
Add new applicant to the ontology.
Can be used interactively or with JSON input.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL
import json
import sys

# Define namespace
ONTO = Namespace("http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/recruitment-ontology#")

def add_applicant_to_graph(g, applicant_data):
    """
    Add a new applicant with answers, experience, and skills to the graph.
    
    applicant_data = {
        'name': 'John',
        'answers': [4, 5, 3, ...],  # 30 scores (1-5)
        'experience': {
            'field': 'DataScience',
            'years': 4
        },
        'skills': {
            'hard_skills': ['PythonSkill', 'SQLSkill', 'MachineLearningSkill'],
            'soft_skills': ['AnalyticalThinkingSkill', 'CommunicationSkill']
        },
        'job': 'DataScientist'  # Job applying for
    }
    """
    
    name = applicant_data['name']
    person_uri = ONTO[name]
    
    # 1. Create Person individual
    g.add((person_uri, RDF.type, OWL.NamedIndividual))
    g.add((person_uri, RDF.type, ONTO.Person))
    
    print(f"✅ Created Person: {name}")
    
    # 2. Create Answer individuals (Q1-Q30)
    answers = applicant_data.get('answers', [])
    if len(answers) != 30:
        print(f"⚠️  Warning: Expected 30 answers, got {len(answers)}")
        return False
    
    for i, score in enumerate(answers, start=1):
        answer_uri = ONTO[f"{name}Ans_Q{i}"]
        question_uri = ONTO[f"Q{i}"]
        
        g.add((answer_uri, RDF.type, OWL.NamedIndividual))
        g.add((answer_uri, RDF.type, ONTO.Answer))
        g.add((answer_uri, ONTO.forQuestion, question_uri))
        g.add((answer_uri, ONTO.answerScore, Literal(score, datatype=XSD.integer)))
        
        # Link answer to person
        g.add((person_uri, ONTO.hasAnswer, answer_uri))
    
    print(f"✅ Created 30 Answer individuals")
    
    # 3. Create Experience
    if 'experience' in applicant_data:
        exp_data = applicant_data['experience']
        exp_uri = ONTO[f"{name}Experience"]
        field_uri = ONTO[exp_data['field']]
        
        g.add((exp_uri, RDF.type, OWL.NamedIndividual))
        g.add((exp_uri, RDF.type, ONTO.Experience))
        g.add((exp_uri, ONTO.experienceInField, field_uri))
        g.add((exp_uri, ONTO.yearsOfExperience, Literal(exp_data['years'], datatype=XSD.integer)))
        
        # Link experience to person
        g.add((person_uri, ONTO.hasExperience, exp_uri))
        
        print(f"✅ Created Experience: {exp_data['years']} years in {exp_data['field']}")
    
    # 4. Add Skills
    if 'skills' in applicant_data:
        skills = applicant_data['skills']
        
        # Hard skills
        for skill_name in skills.get('hard_skills', []):
            skill_uri = ONTO[skill_name]
            g.add((person_uri, ONTO.hasHardSkill, skill_uri))
        
        # Soft skills
        for skill_name in skills.get('soft_skills', []):
            skill_uri = ONTO[skill_name]
            g.add((person_uri, ONTO.hasSoftSkill, skill_uri))
        
        total_skills = len(skills.get('hard_skills', [])) + len(skills.get('soft_skills', []))
        print(f"✅ Added {total_skills} skills")
    
    # 5. Create Application
    app_uri = ONTO[f"{name}Application"]
    job_uri = ONTO[applicant_data.get('job', 'DataScientist')]
    
    g.add((app_uri, RDF.type, OWL.NamedIndividual))
    g.add((app_uri, RDF.type, ONTO.Application))
    g.add((app_uri, ONTO.hasApplicant, person_uri))
    g.add((app_uri, ONTO.forJob, job_uri))
    
    print(f"✅ Created Application for job: {applicant_data.get('job')}")
    
    return True

def interactive_input():
    """Interactive mode to input applicant data."""
    print("\n=== Add New Applicant ===\n")
    
    name = input("Applicant name: ").strip()
    
    print("\nBig Five Personality Test (30 questions)")
    print("Answer with scores 1-5 (1=Strongly Disagree, 5=Strongly Agree)\n")
    
    trait_names = [
        "Agreeableness (Q1-Q6)",
        "Conscientiousness (Q7-Q12)",
        "Extraversion (Q13-Q18)",
        "Neuroticism (Q19-Q24)",
        "Openness (Q25-Q30)"
    ]
    
    answers = []
    for trait_idx, trait in enumerate(trait_names):
        print(f"\n{trait}:")
        for q in range(1, 7):
            q_num = trait_idx * 6 + q
            while True:
                try:
                    score = int(input(f"  Q{q_num}: "))
                    if 1 <= score <= 5:
                        answers.append(score)
                        break
                    else:
                        print("    Please enter 1-5")
                except ValueError:
                    print("    Please enter a number")
    
    print("\n--- Experience ---")
    exp_field = input("Experience field (e.g., DataScience, Marketing, Finance): ").strip()
    exp_years = int(input("Years of experience: "))
    
    print("\n--- Skills ---")
    print("Hard skills (comma-separated, e.g., PythonSkill,SQLSkill,MachineLearningSkill):")
    hard_skills_str = input("  ").strip()
    hard_skills = [s.strip() for s in hard_skills_str.split(',') if s.strip()]
    
    print("Soft skills (comma-separated, e.g., AnalyticalThinkingSkill,CommunicationSkill):")
    soft_skills_str = input("  ").strip()
    soft_skills = [s.strip() for s in soft_skills_str.split(',') if s.strip()]
    
    print("\n--- Application ---")
    job = input("Job applying for (e.g., DataScientist, MarketingManager): ").strip()
    
    return {
        'name': name,
        'answers': answers,
        'experience': {
            'field': exp_field,
            'years': exp_years
        },
        'skills': {
            'hard_skills': hard_skills,
            'soft_skills': soft_skills
        },
        'job': job
    }

def main():
    # Check if JSON file provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"Loading applicant data from {json_file}...")
        with open(json_file, 'r') as f:
            applicant_data = json.load(f)
    else:
        # Interactive mode
        applicant_data = interactive_input()
    
    print("\n=== Loading ontology ===")
    g = Graph()
    g.parse('jobs.ttl', format='turtle')
    print(f"Loaded {len(g)} triples")
    
    print("\n=== Adding applicant ===")
    success = add_applicant_to_graph(g, applicant_data)
    
    if success:
        # Save to new file
        output_file = 'jobs_clean.ttl'
        print(f"\n=== Saving to {output_file} ===")
        g.serialize(destination=output_file, format='turtle')
        print(f"✅ Saved {len(g)} triples")
        
        print("\n=== Next Steps ===")
        print("1. Run: python calculate_bigfive.py")
        print("2. Open jobs_with_scores.ttl in Protégé")
        print("3. Run HermiT or ELK reasoner")
        print("4. Query for top 10% applicants")
    else:
        print("\n❌ Failed to add applicant")

if __name__ == '__main__':
    main()
