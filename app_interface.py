#!/usr/bin/env python3
"""
Streamlit Web Interface for Ontology-Based Job Recommendation System
"""

import streamlit as st
from owlready2 import *
import pandas as pd
from datetime import datetime
import tempfile
import os
import plotly.graph_objects as go

# Clear owlready2 cache on startup to prevent stale data
try:
    from owlready2 import default_world
    default_world.graph.destroy()
except:
    pass

# Page config
st.set_page_config(
    page_title="Job Recommendation System",
    page_icon="💼",
    layout="wide"
)

# Trait mapping for Big Five
TRAIT_MAPPING = {
    'Openness': list(range(1, 7)),           # Q1-Q6
    'Conscientiousness': list(range(7, 13)), # Q7-Q12
    'Extraversion': list(range(13, 19)),     # Q13-Q18
    'Agreeableness': list(range(19, 25)),    # Q19-Q24
    'Neuroticism': list(range(25, 31))       # Q25-Q30
}

# Questions for Big Five assessment (Indonesian)
QUESTIONS = {
    # Openness (Q1-Q6)
    1: "Saya tertarik mencoba hal-hal baru meskipun belum pernah ada yang saya kenal mencobanya.",
    2: "Saya menikmati membaca atau menonton hal-hal yang membuat saya banyak berpikir.",
    3: "Saya sering membayangkan berbagai kemungkinan dan ide kreatif dalam hidup saya.",
    4: "Saya merasa bosan jika harus melakukan hal yang itu-itu saja terus-menerus.",
    5: "Saya tertarik dengan seni, musik, atau karya kreatif lainnya.",
    6: "Saya senang mempelajari sudut pandang atau budaya yang berbeda dari yang biasa saya temui.",
    
    # Conscientiousness (Q7-Q12)
    7: "Saya biasanya menyelesaikan tugas sampai tuntas sebelum beralih ke hal lain.",
    8: "Saya merencanakan kegiatan saya terlebih dahulu, bukan menjalani hari secara asal.",
    9: "Saya berusaha tepat waktu dalam janji atau tenggat (deadline).",
    10: "Saya jarang menunda pekerjaan penting hingga mendekati batas waktu.",
    11: "Saya merasa terganggu jika pekerjaan dilakukan dengan asal-asalan.",
    12: "Saya menjaga barang-barang dan lingkungan saya tetap rapi dan tertata.",
    
    # Extraversion (Q13-Q18)
    13: "Saya merasa bersemangat ketika bertemu dan berinteraksi dengan banyak orang.",
    14: "Dalam suatu kelompok, saya cenderung aktif berbicara daripada hanya mendengarkan.",
    15: "Saya menikmati menjadi pusat perhatian dalam situasi sosial tertentu.",
    16: "Saya mudah memulai obrolan dengan orang yang baru saya kenal.",
    17: "Saya lebih merasa berenergi setelah berkumpul dengan orang lain daripada sendirian.",
    18: "Saya suka terlibat dalam kegiatan atau acara yang ramai dan penuh orang.",
    
    # Agreeableness (Q19-Q24)
    19: "Saya berusaha memahami perasaan orang lain sebelum menilai tindakan mereka.",
    20: "Saya mudah merasa iba ketika melihat orang lain kesulitan.",
    21: "Saya bersedia mengalah demi menjaga hubungan yang baik dengan orang lain.",
    22: "Saya berusaha bersikap sopan dan menghargai orang lain, bahkan ketika saya tidak setuju.",
    23: "Orang lain dapat mengandalkan saya ketika mereka membutuhkan bantuan.",
    24: "Saya mencoba melihat sisi baik dari orang lain, meskipun mereka memiliki kekurangan.",
    
    # Neuroticism (Q25-Q30)
    25: "Saya sering merasa khawatir terhadap banyak hal, bahkan hal-hal kecil.",
    26: "Perasaan saya mudah berubah-ubah sepanjang hari.",
    27: "Saya sering memikirkan kesalahan atau kegagalan saya di masa lalu.",
    28: "Saya mudah merasa tegang atau gelisah dalam situasi yang tidak pasti.",
    29: "Ketika ada masalah kecil, saya cenderung langsung kepikiran yang terburuk.",
    30: "Saya sering merasa lelah secara emosional setelah melalui hari yang berat."
}

JOB_CATEGORIES = {
    'HighFitForAnalyticalRoles': {
        'name': 'Analytical Roles',
        'jobs': ['Data Analyst', 'Data Scientist', 'Product Manager', 'UX Researcher', 'Security Analyst', 'Finance Analyst'],
        'description': 'Roles requiring strong analytical thinking and problem-solving',
        'icon': '📊'
    },
    'HighFitForTechnicalRoles': {
        'name': 'Technical Roles',
        'jobs': ['Software Engineer', 'DevOps Engineer', 'QA Engineer', 'UI/UX Designer', 'Tax Officer'],
        'description': 'Technical positions requiring precision and technical expertise',
        'icon': '💻'
    },
    'HighFitForSupportRoles': {
        'name': 'Support Roles',
        'jobs': ['Customer Success', 'Customer Support', 'HR Manager', 'People & Culture'],
        'description': 'People-oriented roles focused on support and relationships',
        'icon': '🤝'
    },
    'HighFitForWritingRoles': {
        'name': 'Writing Roles',
        'jobs': ['Content Writer', 'Copywriter', 'UX Writer', 'Content Strategist'],
        'description': 'Creative roles focused on written communication',
        'icon': '✍️'
    },
    'HighFitForInterpersonalRoles': {
        'name': 'Interpersonal Roles',
        'jobs': ['Sales Manager', 'Account Manager', 'Community Manager'],
        'description': 'Roles requiring strong interpersonal and communication skills',
        'icon': '💬'
    }
}

def get_job_fields():
    """Get all job fields from ontology"""
    try:
        # Force fresh load
        world = World()
        onto_path = os.path.abspath("jobs.owl")
        onto = world.get_ontology(f"file://{onto_path}").load()
        
        fields = []
        with onto:
            JobField = onto.JobField
            if JobField:
                for field in JobField.instances():
                    fields.append(field.name)
        return sorted(fields)
    except Exception as e:
        st.error(f"Error loading job fields: {str(e)}")
        return []

def get_occupations_with_fields():
    """Get all job occupations with their corresponding fields"""
    try:
        # Force fresh load
        world = World()
        onto_path = os.path.abspath("jobs.owl")
        onto = world.get_ontology(f"file://{onto_path}").load()
        
        occupations = {}
        with onto:
            JobOccupation = onto.JobOccupation
            if JobOccupation:
                for cls in JobOccupation.subclasses():
                    # Check restrictions for inJobField
                    for restriction in cls.is_a:
                        if hasattr(restriction, 'value') and hasattr(restriction, 'property'):
                            if restriction.property.name == 'inJobField':
                                field_name = restriction.value.name
                                occ_name = cls.name
                                if occ_name not in occupations:
                                    occupations[occ_name] = field_name
                                break
        return occupations
    except Exception as e:
        st.error(f"Error loading occupations: {str(e)}")
        return {}

def get_job_required_skills(job_name):
    """Get required skills for a specific job occupation from ontology"""
    required_skills = {
        'hard_skills': [],
        'soft_skills': []
    }
    
    try:
        world = World()
        onto_path = os.path.abspath("jobs_with_scores.owl")
        if not os.path.exists(onto_path):
            onto_path = os.path.abspath("jobs.owl")
        onto = world.get_ontology(f"file://{onto_path}").load()
        
        with onto:
            # Find the job occupation class
            job_class = None
            for cls in onto.classes():
                if cls.name == job_name:
                    job_class = cls
                    break
            
            if job_class:
                # Get required skills from restrictions
                for restriction in job_class.is_a:
                    if hasattr(restriction, 'value') and hasattr(restriction, 'property'):
                        prop_name = restriction.property.name
                        if 'requiresSkill' in prop_name or 'needsSkill' in prop_name:
                            skill = restriction.value
                            if hasattr(skill, 'name'):
                                skill_name = skill.name
                                # Check if it's a hard skill or soft skill
                                skill_instance = onto.search_one(iri=f"*{skill_name}")
                                if skill_instance:
                                    if hasattr(onto, 'HardSkill') and isinstance(skill_instance, onto.HardSkill):
                                        required_skills['hard_skills'].append(skill_name)
                                    elif hasattr(onto, 'SoftSkill') and isinstance(skill_instance, onto.SoftSkill):
                                        required_skills['soft_skills'].append(skill_name)
    except Exception as e:
        pass  # Silent fail, return empty lists
    
    return required_skills

def calculate_skill_match(applicant_skills, applicant_soft_skills, job_name):
    """Calculate skill match percentage between applicant and job requirements"""
    if not job_name:
        return 0, {'matched': [], 'missing': []}
    
    required = get_job_required_skills(job_name)
    all_required = required['hard_skills'] + required['soft_skills']
    all_applicant = applicant_skills + applicant_soft_skills
    
    if not all_required:
        # If no required skills defined, consider all skills as relevant
        return 100, {'matched': all_applicant, 'missing': []}
    
    # Convert to lowercase for comparison
    required_lower = [s.lower() for s in all_required]
    applicant_lower = [s.lower() for s in all_applicant]
    
    # Find matched skills
    matched = [skill for skill in all_applicant if skill.lower() in required_lower]
    missing = [skill for skill in all_required if skill.lower() not in applicant_lower]
    
    # Calculate percentage
    match_percentage = (len(matched) / len(all_required) * 100) if all_required else 0
    
    return round(match_percentage, 1), {'matched': matched, 'missing': missing}

def calculate_big_five(answers):
    """Calculate Big Five personality scores from answers (adapted from calculate_big_five.py)"""
    trait_scores = {}
    
    for trait, question_nums in TRAIT_MAPPING.items():
        scores = [answers.get(q) for q in question_nums if q in answers]
        if scores:
            avg_score = sum(scores) / len(scores)
            trait_scores[trait] = round(avg_score, 2)
        else:
            print(f"Warning: No answers found for {trait}")
    
    return trait_scores

def get_soft_skills():
    """Get all soft skills from ontology"""
    try:
        # Force fresh load
        world = World()
        onto_path = os.path.abspath("jobs.owl")
        onto = world.get_ontology(f"file://{onto_path}").load()
        
        skills = set()  # Use set to avoid duplicates
        with onto:
            SoftSkill = onto.SoftSkill
            if SoftSkill:
                for skill in SoftSkill.instances():
                    skills.add(skill.name)
        return sorted(list(skills))
    except Exception as e:
        st.error(f"Error loading soft skills: {str(e)}")
        return []

def get_hard_skills():
    """Get all hard skills from ontology"""
    try:
        # Force fresh load
        world = World()
        onto_path = os.path.abspath("jobs.owl")
        onto = world.get_ontology(f"file://{onto_path}").load()
        
        skills = set()  # Use set to avoid duplicates
        with onto:
            HardSkill = onto.HardSkill
            if HardSkill:
                for skill in HardSkill.instances():
                    skills.add(skill.name)
        return sorted(list(skills))
    except Exception as e:
        st.error(f"Error loading hard skills: {str(e)}")
        return []

def create_radar_chart(scores):
    """Create a radar chart for Big Five personality scores"""
    categories = list(scores.keys())
    values = list(scores.values())
    
    # Close the radar chart by repeating the first value
    categories += [categories[0]]
    values += [values[0]]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Personality Scores',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickvals=[0, 1, 2, 3, 4, 5],
                ticktext=['0', '1', '2', '3', '4', '5']
            )
        ),
        showlegend=False,
        title="Big Five Personality Profile",
        title_x=0.5,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def add_applicant_to_ontology(name, answers, job_field=None, job_occupation=None, years_experience=None, soft_skills=None, hard_skills=None):
    """Add new applicant with answers and job details to ontology"""
    try:
        print(f"\n{'='*60}")
        print(f"Adding applicant: {name}")
        print(f"  Job Field: {job_field}")
        print(f"  Job Occupation: {job_occupation}")
        print(f"  Years Experience: {years_experience}")
        print(f"  Soft Skills: {soft_skills}")
        print(f"  Hard Skills: {hard_skills}")
        print(f"  Total Answers: {len(answers)}")
        print(f"{'='*60}\n")
        
        # Load ontology from jobs_with_scores.owl (main working file)
        onto_path = os.path.abspath("jobs_with_scores.owl")
        if not os.path.exists(onto_path):
            # Fallback to jobs.owl if jobs_with_scores doesn't exist yet
            onto_path = os.path.abspath("jobs.owl")
        onto = get_ontology(f"file://{onto_path}").load()
        
        with onto:
            # Create Person individual
            person_name = name.replace(" ", "_")
            Person = onto.Person
            new_person = Person(person_name)
            
            # Create Answer individuals for each question
            print(f"Creating {len(answers)} answer individuals...")
            for q_num, score in answers.items():
                answer_name = f"{person_name}Ans_Q{q_num}"
                Answer = onto.Answer
                new_answer = Answer(answer_name)
                
                # Set answer properties
                new_answer.answerScore = [score]
                
                # Link to question
                question_name = f"Q{q_num}"
                if hasattr(onto, question_name):
                    new_answer.forQuestion = [onto[question_name]]
                
                # Link answer to person
                if not hasattr(new_person, 'hasAnswer'):
                    new_person.hasAnswer = []
                new_person.hasAnswer.append(new_answer)
            print(f"✓ Created all {len(answers)} answers")
            
            # Add job field
            if job_field and hasattr(onto, job_field):
                new_person.inJobField = [onto[job_field]]
                print(f"✓ Added job field: {job_field}")
            
            # Add job occupation
            if job_occupation and hasattr(onto, job_occupation):
                new_person.hasJobOccupation = [onto[job_occupation]]
                print(f"✓ Added job occupation: {job_occupation}")
            
            # Add years of experience
            if years_experience is not None:
                new_person.hasYearsOfExperience = [years_experience]
                print(f"✓ Added years of experience: {years_experience}")
            
            # Add soft skills
            if soft_skills:
                print(f"Adding soft skills: {soft_skills}")
                for skill in soft_skills:
                    # Try to find the skill in ontology
                    skill_obj = None
                    if hasattr(onto, skill):
                        skill_obj = onto[skill]
                    else:
                        # Try searching for skill
                        skill_obj = onto.search_one(iri=f"*{skill}")
                    
                    if skill_obj:
                        if not hasattr(new_person, 'hasSoftSkill'):
                            new_person.hasSoftSkill = []
                        new_person.hasSoftSkill.append(skill_obj)
                        print(f"  ✓ Added soft skill: {skill}")
                    else:
                        print(f"  ✗ Soft skill not found in ontology: {skill}")
            
            # Add hard skills
            if hard_skills:
                print(f"Adding hard skills: {hard_skills}")
                for skill in hard_skills:
                    # Try to find the skill in ontology
                    skill_obj = None
                    if hasattr(onto, skill):
                        skill_obj = onto[skill]
                    else:
                        # Try searching for skill
                        skill_obj = onto.search_one(iri=f"*{skill}")
                    
                    if skill_obj:
                        if not hasattr(new_person, 'hasHardSkill'):
                            new_person.hasHardSkill = []
                        new_person.hasHardSkill.append(skill_obj)
                        print(f"  ✓ Added hard skill: {skill}")
                    else:
                        print(f"  ✗ Hard skill not found in ontology: {skill}")
        
        # Calculate Big Five scores immediately
        print(f"\nCalculating Big Five scores...")
        trait_scores = calculate_big_five(answers)
        print(f"Trait scores: {trait_scores}")
        
        # Save scores as data properties
        if 'Agreeableness' in trait_scores:
            new_person.hasAgreeablenessScore = [trait_scores['Agreeableness']]
        if 'Conscientiousness' in trait_scores:
            new_person.hasConscientiousnessScore = [trait_scores['Conscientiousness']]
        if 'Extraversion' in trait_scores:
            new_person.hasExtraversionScore = [trait_scores['Extraversion']]
        if 'Neuroticism' in trait_scores:
            new_person.hasNeuroticismScore = [trait_scores['Neuroticism']]
        if 'Openness' in trait_scores:
            new_person.hasOpennessScore = [trait_scores['Openness']]
        
        # Calculate weighted overall score
        applicant_data_for_score = {
            'scores': trait_scores,
            'categories': [],
            'job_occupation': job_occupation,
            'hard_skills': hard_skills if hard_skills else [],
            'soft_skills': soft_skills if soft_skills else [],
            'years_experience': years_experience if years_experience else 0,
            'job_field': job_field
        }
        overall_score = calculate_overall_fit_score(applicant_data_for_score)
        new_person.hasWeightedScore = [float(overall_score)]
        print(f"✓ Overall weighted score: {overall_score}")
        
        # Save component scores to ontology
        score_breakdown = applicant_data_for_score.get('score_breakdown', {})
        new_person.hasCategoryFitScore = [float(score_breakdown.get('category_fit', 0.0))]
        new_person.hasSkillMatchScore = [float(score_breakdown.get('skill_match', 0.0))]
        new_person.hasExperienceScore = [float(score_breakdown.get('experience', 0.0))]
        print(f"✓ Category fit score: {score_breakdown.get('category_fit', 0.0)}")
        print(f"✓ Skill match score: {score_breakdown.get('skill_match', 0.0)}")
        print(f"✓ Experience score: {score_breakdown.get('experience', 0.0)}")
        
        print(f"\n{'='*60}")
        print(f"All data saved for: {name}")
        print(f"{'='*60}\n")
        
        # Save to jobs_with_scores.owl (working file)
        onto.save(file="jobs_with_scores.owl", format="rdfxml")
        print("✓ Saved to jobs_with_scores.owl")
        
        # Sync to jobs_with_scores.ttl for viewing only (DON'T touch jobs_clean.ttl)
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse("jobs_with_scores.owl", format="xml")
            
            # Bind namespaces
            g.bind("owl", OWL)
            g.bind("rdf", RDF)
            g.bind("rdfs", RDFS)
            g.bind("", Namespace("http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/recruitment-ontology#"))
            
            # Save to TTL for viewing
            g.serialize(destination="jobs_with_scores.ttl", format="turtle", encoding="utf-8")
            print("✓ Synced to jobs_with_scores.ttl (for viewing)")
        except Exception as e:
            print(f"Warning: Could not sync to TTL: {e}")
        
        return True, "Applicant added! Data in jobs_with_scores.owl, viewable in jobs_with_scores.ttl"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def run_complete_workflow():
    """Run complete workflow: calculate scores + reasoning"""
    try:
        # Load ontology from jobs_with_scores.owl (working file)
        onto_path = os.path.abspath("jobs_with_scores.owl")
        if not os.path.exists(onto_path):
            # Fallback to jobs.owl
            onto_path = os.path.abspath("jobs.owl")
        onto = get_ontology(f"file://{onto_path}").load()
        
        # Calculate Big Five scores
        with onto:
            Person = onto.Person
            persons = list(Person.instances())
            
            for person in persons:
                if hasattr(person, 'hasAnswer'):
                    answers = {}
                    for answer in person.hasAnswer:
                        if hasattr(answer, 'forQuestion') and hasattr(answer, 'answerScore'):
                            q_name = answer.forQuestion[0].name if answer.forQuestion else None
                            score = answer.answerScore[0] if answer.answerScore else None
                            
                            if q_name and q_name.startswith('Q'):
                                q_num = int(q_name[1:])
                                answers[q_num] = score
                    
                    if answers:
                        trait_scores = calculate_big_five(answers)
                        
                        # Add scores as data properties
                        if 'Agreeableness' in trait_scores:
                            person.hasAgreeablenessScore = [trait_scores['Agreeableness']]
                        if 'Conscientiousness' in trait_scores:
                            person.hasConscientiousnessScore = [trait_scores['Conscientiousness']]
                        if 'Extraversion' in trait_scores:
                            person.hasExtraversionScore = [trait_scores['Extraversion']]
                        if 'Neuroticism' in trait_scores:
                            person.hasNeuroticismScore = [trait_scores['Neuroticism']]
                        if 'Openness' in trait_scores:
                            person.hasOpennessScore = [trait_scores['Openness']]
                        
                        # Calculate and save weighted overall score
                        applicant_data = {
                            'scores': trait_scores,
                            'categories': [],
                            'job_occupation': person.hasJobOccupation[0].name if hasattr(person, 'hasJobOccupation') and person.hasJobOccupation else None,
                            'hard_skills': [s.name for s in person.hasHardSkill] if hasattr(person, 'hasHardSkill') else [],
                            'soft_skills': [s.name for s in person.hasSoftSkill] if hasattr(person, 'hasSoftSkill') else [],
                            'years_experience': person.hasYearsOfExperience[0] if hasattr(person, 'hasYearsOfExperience') and person.hasYearsOfExperience else 0,
                            'job_field': person.inJobField[0].name if hasattr(person, 'inJobField') and person.inJobField else None
                        }
                        
                        overall_score = calculate_overall_fit_score(applicant_data)
                        person.hasWeightedScore = [float(overall_score)]
                        
                        # Save component scores to ontology
                        score_breakdown = applicant_data.get('score_breakdown', {})
                        if 'category_fit' in score_breakdown:
                            person.hasCategoryFitScore = [float(score_breakdown['category_fit'])]
                        if 'skill_match' in score_breakdown:
                            person.hasSkillMatchScore = [float(score_breakdown['skill_match'])]
                        if 'experience' in score_breakdown:
                            person.hasExperienceScore = [float(score_breakdown['experience'])]
                        
                        # Save years of experience
                        if applicant_data['years_experience'] is not None:
                            person.hasYearsOfExperience = [int(applicant_data['years_experience'])]
        
        # Save to jobs_with_scores.owl (working file)
        onto.save(file="jobs_with_scores.owl", format="rdfxml")
        print("✓ Saved to jobs_with_scores.owl")
        
        # Sync to jobs_with_scores.ttl for viewing
        try:
            from rdflib import Graph, Namespace
            from rdflib.namespace import RDF, RDFS, OWL
            
            g = Graph()
            g.parse("jobs_with_scores.owl", format="xml")
            
            # Bind namespaces
            g.bind("owl", OWL)
            g.bind("rdf", RDF)
            g.bind("rdfs", RDFS)
            g.bind("", Namespace("http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/recruitment-ontology#"))
            
            # Save to TTL for viewing
            g.serialize(destination="jobs_with_scores.ttl", format="turtle", encoding="utf-8")
            print("✓ Synced to jobs_with_scores.ttl (for viewing)")
        except ImportError:
            print("rdflib not available, TTL sync skipped")
        except Exception as e:
            print(f"Warning: Could not sync to TTL: {e}")
        
        print("Reasoning skipped due to technical issues with Java/Pellet")
        
        return True, "Analysis complete! Results in jobs_with_scores.owl and jobs_with_scores.ttl"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_all_applicants():
    """Get all applicants with their scores and classifications"""
    try:
        # Load from jobs_with_scores.owl (working file with all data)
        # Force fresh load with new world to avoid cache
        world = World()
        onto_path = os.path.abspath("jobs_with_scores.owl")
        if not os.path.exists(onto_path):
            onto_path = os.path.abspath("jobs.owl")
        
        onto = world.get_ontology(f"file://{onto_path}").load()
        print(f"\n[VIEW RESULTS] Loading from: {onto_path}")
        
        applicants = []
        seen_names = set()  # Track seen names to avoid duplicates
        with onto:
            Person = onto.Person
            persons = list(Person.instances())
            print(f"[VIEW RESULTS] Found {len(persons)} persons in ontology")
            
            for person in persons:
                if person.name in seen_names:
                    continue  # Skip duplicates
                seen_names.add(person.name)
                applicant_data = {
                    'name': person.name,
                    'scores': {},
                    'categories': [],
                    'job_field': None,
                    'job_occupation': None,
                    'years_experience': None,
                    'soft_skills': [],
                    'hard_skills': []
                }
                
                # Get Big Five scores
                if hasattr(person, 'hasOpennessScore') and person.hasOpennessScore:
                    applicant_data['scores']['Openness'] = person.hasOpennessScore[0]
                if hasattr(person, 'hasConscientiousnessScore') and person.hasConscientiousnessScore:
                    applicant_data['scores']['Conscientiousness'] = person.hasConscientiousnessScore[0]
                if hasattr(person, 'hasExtraversionScore') and person.hasExtraversionScore:
                    applicant_data['scores']['Extraversion'] = person.hasExtraversionScore[0]
                if hasattr(person, 'hasAgreeablenessScore') and person.hasAgreeablenessScore:
                    applicant_data['scores']['Agreeableness'] = person.hasAgreeablenessScore[0]
                if hasattr(person, 'hasNeuroticismScore') and person.hasNeuroticismScore:
                    applicant_data['scores']['Neuroticism'] = person.hasNeuroticismScore[0]
                
                # Get job field
                if hasattr(person, 'inJobField') and person.inJobField:
                    applicant_data['job_field'] = person.inJobField[0].name
                
                # Get job occupation
                if hasattr(person, 'hasJobOccupation') and person.hasJobOccupation:
                    applicant_data['job_occupation'] = person.hasJobOccupation[0].name
                
                # Get years of experience
                if hasattr(person, 'hasYearsOfExperience') and person.hasYearsOfExperience:
                    applicant_data['years_experience'] = person.hasYearsOfExperience[0]
                
                # Get soft skills
                if hasattr(person, 'hasSoftSkill'):
                    applicant_data['soft_skills'] = [skill.name for skill in person.hasSoftSkill]
                
                # Get hard skills
                if hasattr(person, 'hasHardSkill'):
                    applicant_data['hard_skills'] = [skill.name for skill in person.hasHardSkill]
                
                # Load component scores from ontology
                # If these exist, prefer them and build a score_breakdown so UI can display without recomputing
                if hasattr(person, 'hasCategoryFitScore') and person.hasCategoryFitScore:
                    applicant_data['category_fit_score'] = float(person.hasCategoryFitScore[0])
                if hasattr(person, 'hasSkillMatchScore') and person.hasSkillMatchScore:
                    applicant_data['skill_match_score'] = float(person.hasSkillMatchScore[0])
                if hasattr(person, 'hasExperienceScore') and person.hasExperienceScore:
                    applicant_data['experience_score'] = float(person.hasExperienceScore[0])
                if hasattr(person, 'hasWeightedScore') and person.hasWeightedScore:
                    applicant_data['overall_fit_score'] = float(person.hasWeightedScore[0])
                # Build breakdown when ontology already stores component scores
                if ('category_fit_score' in applicant_data or 'skill_match_score' in applicant_data or 'experience_score' in applicant_data):
                    breakdown = {
                        'category_fit': applicant_data.get('category_fit_score', 0.0),
                        'skill_match': applicant_data.get('skill_match_score', 0.0),
                        'experience': applicant_data.get('experience_score', 0.0),
                        'personality': 0.0,
                        'years_experience': applicant_data.get('years_experience', 0)
                    }
                    if applicant_data['scores']:
                        avg_personality = sum(applicant_data['scores'].values()) / len(applicant_data['scores'])
                        breakdown['personality'] = round((avg_personality / 5.0) * 25, 2)
                    applicant_data['score_breakdown'] = breakdown
                
                # Calculate skill match if job occupation exists
                if applicant_data['job_occupation']:
                    match_pct, _ = calculate_skill_match(
                        applicant_data['hard_skills'],
                        applicant_data['soft_skills'],
                        applicant_data['job_occupation']
                    )
                    applicant_data['skill_match_percentage'] = match_pct
                else:
                    applicant_data['skill_match_percentage'] = 0
                
                # Get fit categories (mock for now since reasoning is disabled)
                # In a real implementation, this would come from reasoned ontology
                if applicant_data['scores']:
                    # Simple rule-based classification based on scores
                    openness = applicant_data['scores'].get('Openness', 0)
                    conscientiousness = applicant_data['scores'].get('Conscientiousness', 0)
                    extraversion = applicant_data['scores'].get('Extraversion', 0)
                    agreeableness = applicant_data['scores'].get('Agreeableness', 0)
                    neuroticism = applicant_data['scores'].get('Neuroticism', 0)
                    
                    if conscientiousness >= 4.0 and openness >= 4.5 and neuroticism <= 2.5:
                        applicant_data['categories'].append('HighFitForAnalyticalRoles')
                    elif conscientiousness >= 3.0:
                        applicant_data['categories'].append('HighFitForTechnicalRoles')
                    elif agreeableness >= 4.0 and extraversion >= 3.5:
                        applicant_data['categories'].append('HighFitForSupportRoles')
                    elif openness >= 4.0:
                        applicant_data['categories'].append('HighFitForWritingRoles')
                    elif extraversion >= 4.0:
                        applicant_data['categories'].append('HighFitForInterpersonalRoles')
                
                applicants.append(applicant_data)
        
        return applicants
        
    except Exception as e:
        st.error(f"Error loading applicants: {str(e)}")
        return []

def get_score_interpretation(score):
    """Get interpretation for overall fit score"""
    if score >= 80:
        return "Excellent Match", "🟢 Highly Recommended", "success"
    elif score >= 65:
        return "Good Match", "🟡 Recommended", "warning"
    elif score >= 50:
        return "Fair Match", "🟠 Consider with Interview", "info"
    elif score >= 35:
        return "Weak Match", "🔴 Additional Assessment Needed", "error"
    else:
        return "Poor Match", "⚫ Not Recommended", "error"

def calculate_overall_fit_score(applicant):
    """Calculate overall fit score with weighted components for job-relevant skills and experience"""
    score = 0
    breakdown = {}
    job_occupation = applicant.get('job_occupation')
    normalized_job = job_occupation.replace(" ", "").replace("_", "").lower() if job_occupation else ""

    analytical_roles = {
        "dataanalyst", "datascientist", "productmanager", "uxresearcher", "securityanalyst",
        "financeanalyst", "financialanalyst"
    }
    technical_roles = {
        "softwareengineer", "devopsengineer", "qaengineer", "uiuxdesigner", "taxofficer",
        "dataengineer", "backenddeveloper", "frontenddeveloper"
    }
    support_roles = {"customersuccess", "customersupport", "hrmanager", "peopleandculture", "customersupportjob"}
    writing_roles = {"contentwriter", "copywriter", "uxwriter", "contentstrategist"}
    interpersonal_roles = {"salesmanager", "accountmanager", "accountmanagerjob", "communitymanager"}
    
    # 1. Personality score component (25% weight) - Reduced to give more weight to skills
    if applicant['scores']:
        avg_personality = sum(applicant['scores'].values()) / len(applicant['scores'])
        personality_score = (avg_personality / 5.0) * 25
        score += personality_score
        breakdown['personality'] = round(personality_score, 2)
    else:
        breakdown['personality'] = 0
    
    # 2. Category Fit score component (20% weight) - Based on personality match with job category
    category_score = 0
    if applicant['scores'] and normalized_job:
        scores = applicant['scores']
        
        # Define ideal personality profiles for each category
        if normalized_job in analytical_roles:
            # Analytical roles: high Conscientiousness & Openness, low Neuroticism
            category_score = ((scores.get('Conscientiousness', 0) / 5.0) * 8 + 
                            (scores.get('Openness', 0) / 5.0) * 8 + 
                            ((5 - scores.get('Neuroticism', 5)) / 5.0) * 4)
        elif normalized_job in technical_roles:
            # Technical roles: high Conscientiousness
            category_score = ((scores.get('Conscientiousness', 0) / 5.0) * 12 + 
                            (scores.get('Openness', 0) / 5.0) * 8)
        elif normalized_job in support_roles:
            # Support roles: high Agreeableness & Extraversion
            category_score = ((scores.get('Agreeableness', 0) / 5.0) * 10 + 
                            (scores.get('Extraversion', 0) / 5.0) * 10)
        elif normalized_job in writing_roles:
            # Writing roles: high Openness
            category_score = ((scores.get('Openness', 0) / 5.0) * 15 + 
                            (scores.get('Conscientiousness', 0) / 5.0) * 5)
        elif normalized_job in interpersonal_roles:
            # Interpersonal roles: high Extraversion
            category_score = ((scores.get('Extraversion', 0) / 5.0) * 12 + 
                            (scores.get('Agreeableness', 0) / 5.0) * 8)
        else:
            # Default: balanced scoring
            category_score = (sum(scores.values()) / len(scores) / 5.0) * 20
    
    score += category_score
    breakdown['category_fit'] = round(category_score, 2)

    # 3. Skill Match component (35% weight) - HIGHEST PRIORITY
    job_occupation = applicant.get('job_occupation')
    if job_occupation:
        required_skills = get_job_required_skills(job_occupation)
        all_required = required_skills['hard_skills'] + required_skills['soft_skills']
        all_applicant = applicant.get('hard_skills', []) + applicant.get('soft_skills', [])
        
        if all_required:
            # Required skills matched (20 points)
            required_lower = [s.lower() for s in all_required]
            applicant_lower = [s.lower() for s in all_applicant]
            matched = [s for s in all_applicant if s.lower() in required_lower]
            
            matched_score = (len(matched) / len(all_required)) * 20
            
            # Additional relevant skills (10 points) - bonus for extra skills
            additional_skills = [s for s in all_applicant if s.lower() not in required_lower]
            additional_score = min(len(additional_skills) * 0.5, 10)
            
            # Skill proficiency bonus (5 points) - if high match rate
            proficiency_bonus = 0
            if len(matched) >= len(all_required) * 0.8:  # 80% or more matched
                proficiency_bonus = 5
            
            skill_score = matched_score + additional_score + proficiency_bonus
            score += skill_score
            breakdown['skill_match'] = round(skill_score, 2)
            breakdown['matched_skills'] = len(matched)
            breakdown['required_skills'] = len(all_required)
        else:
            # If no required skills defined, use basic scoring
            basic_skill_score = min(len(all_applicant) * 1.5, 35)
            score += basic_skill_score
            breakdown['skill_match'] = round(basic_skill_score, 2)
    else:
        breakdown['skill_match'] = 0
    
    # 4. Experience component (20% weight) - NEW weighted component
    years_exp = applicant.get('years_experience') or 0  # Handle None or missing value
    job_field = applicant.get('job_field')
    
    # Years of experience score (10 points)
    years_score = min((years_exp / 10.0) * 10, 10)  # Max 10 points for 10+ years
    
    # Relevant experience bonus (10 points) - if has experience AND applying to same field
    relevant_bonus = 0
    if years_exp >= 1 and job_field and job_occupation:
        # Bonus if has at least 1 year experience
        relevant_bonus = 10
    elif years_exp >= 2:
        # Smaller bonus for 2+ years experience even without field match
        relevant_bonus = 5
    
    experience_score = years_score + relevant_bonus
    score += experience_score
    breakdown['experience'] = round(experience_score, 2)
    breakdown['years_experience'] = years_exp
    
    # Store breakdown for detailed display
    applicant['score_breakdown'] = breakdown
    
    return round(score, 2)

# Main App
st.title("Job Recommendation System")
st.markdown("### Ontology-Based Personality Assessment & Job Matching")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation", 
    ["Home", "Add Applicant", "Run Analysis", "View Results"],
    help="Select menu to navigate"
)

if page == "Home":
    st.header("Welcome to Job Recommendation System")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Job Categories", "5")
    with col2:
        st.metric("Assessment Questions", "30")
    with col3:
        st.metric("Big Five Dimensions", "5")
    
    st.markdown("---")
    
    st.subheader("Job Categories")
    cols = st.columns(2)
    for idx, (key, cat) in enumerate(JOB_CATEGORIES.items()):
        with cols[idx % 2]:
            with st.expander(f"{cat['name']}"):
                st.write(f"**Description:** {cat['description']}")
                st.write(f"**Jobs:** {', '.join(cat['jobs'])}")
    
    st.markdown("---")
    st.subheader("System Workflow")
    st.markdown("""
    1. **Add Applicant** - Enter applicant data and complete 30 Big Five personality assessment questions
       - ✅ Scores are calculated automatically
       - ✅ Overall fit score is computed instantly
       - ✅ All data saved to ontology immediately
    
    2. **View Results** - Review personality scores, matching job categories, and applicant classifications
       - View Big Five personality profiles
       - See skill match analysis
       - Check overall fit scores
    
    3. **Run Analysis** (Optional) - Re-calculate scores for existing applicants if needed
    
    **Scoring System:**
    - **Skill Match** (35%) - Highest priority - matching hard & soft skills with job requirements
    - **Personality** (25%) - Average Big Five score normalized to 0-25 scale
    - **Experience** (20%) - Years of experience with relevance bonus
    - **Category Fit** (20%) - Personality match with job category profile
    """)
    
    st.success("✨ **New:** Scores are now calculated automatically when adding applicants!")

elif page == "Add Applicant":
    st.header("Add New Applicant")
    
    with st.form("add_applicant_form"):
        st.subheader("Applicant Information")
        name = st.text_input("Full Name*", placeholder="e.g., John Doe")
        
        col1, col2 = st.columns(2)
        with col1:
            years_exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
        with col2:
            # Get available hard skills from ontology
            available_hard_skills = get_hard_skills()
            selected_hard_skills = st.multiselect(
                "Hard Skills",
                options=available_hard_skills,
                default=[],
                help="Select technical skills from the list"
            )
        
        # Get available soft skills from ontology
        available_soft_skills = get_soft_skills()
        selected_soft_skills = st.multiselect(
            "Soft Skills",
            options=available_soft_skills,
            default=[],
            help="Select interpersonal skills from the list"
        )
        
        st.markdown("---")
        st.subheader("Job Preferences")
        
        occupations_with_fields = get_occupations_with_fields()
        occupation_options = [""] + list(occupations_with_fields.keys())
        
        selected_occupation = st.selectbox(
            "Select Job Position:",
            options=occupation_options,
            format_func=lambda x: f"{x.replace('_', ' ').title()}" if x else "Select job position...",
            key="job_occupation"
        )
        
        selected_field = occupations_with_fields.get(selected_occupation, "") if selected_occupation else ""
        
        st.markdown("---")
        st.subheader("Big Five Personality Assessment")
        st.markdown("**Scale:** 1 = Sangat Tidak Setuju | 5 = Sangat Setuju")
        
        answers = {}
        likert_options = {
            1: "Sangat Tidak Setuju",
            2: "Tidak Setuju",
            3: "Netral",
            4: "Setuju",
            5: "Sangat Setuju"
        }
        
        # All 30 questions displayed sequentially
        for q_num in range(1, 31):
            st.markdown(f"**{q_num}.** {QUESTIONS[q_num]}")
            answers[q_num] = st.radio(
                "Pilih jawaban:",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: likert_options[x],
                index=2,
                key=f"q{q_num}",
                horizontal=True,
                label_visibility="collapsed"
            )
            st.markdown("")
        
        submitted = st.form_submit_button("Save Applicant Data", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("Applicant name is required!")
            elif not selected_occupation:
                st.error("Job position must be selected!")
            else:
                with st.spinner("Saving applicant data and calculating scores..."):
                    success, message = add_applicant_to_ontology(
                        name, answers, selected_field, selected_occupation, 
                        years_exp, selected_soft_skills, selected_hard_skills
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.success("✅ Big Five scores calculated and saved!")
                        st.success("✅ Overall fit score calculated and saved!")
                        st.balloons()
                        st.info("**Next step:** Go to 'View Results' to see the analysis!")
                    else:
                        st.error(f"{message}")

elif page == "Run Analysis":
    st.header("Re-calculate Scores (Optional)")
    
    st.info("""
    ℹ️ **Note:** Scores are now calculated automatically when adding applicants.
    
    Use this only if you want to **re-calculate all scores** for existing applicants.
    """)
    
    st.markdown("""
    This process will:
    1. Re-calculate Big Five scores for ALL applicants
    2. Re-calculate weighted overall scores
    3. Update all results in ontology files
    """)
    
    st.warning("⚠️ This will overwrite existing scores!")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Run Complete Analysis", type="primary", use_container_width=True):
            with st.spinner("Processing analysis..."):
                success, message = run_complete_workflow()
                if success:
                    st.success(f"{message}")
                    st.balloons()
                    st.info("""
                    **Results saved to:**
                    - `jobs_with_scores.owl` - OWL file with complete scores
                    """)
                else:
                    st.error(f"{message}")

elif page == "View Results":
    st.header("Applicant Analysis Results")
    
    # Load applicants once so filters and sorting stay in sync
    applicants = get_all_applicants()

    # Pull ontology-based field/occupation list so dropdowns are never empty
    ontology_fields = get_job_fields()
    ontology_occ_map = get_occupations_with_fields()  # {occupation: field}

    # Collect seen fields from applicants too (union)
    applicant_fields = {a.get('job_field') for a in applicants if a.get('job_field')}
    job_fields = sorted(set(ontology_fields).union(applicant_fields))

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_field = st.selectbox(
            "Filter Field:",
            options=["All Fields"] + job_fields,
            key="filter_field"
        )

    with col2:
        if selected_field != "All Fields":
            occ_candidates = [occ for occ, field in ontology_occ_map.items() if field == selected_field]
        else:
            occ_candidates = list(ontology_occ_map.keys())

        occupation_options = ["All Positions"] + sorted(occ_candidates)
        filter_job = st.selectbox(
            "Filter Position:",
            options=occupation_options,
            format_func=lambda x: "All Positions" if x == "All Positions" else (x.replace('_', ' ').title() if x else "Unspecified Position"),
            key="filter_job"
        )

    with col3:
        sort_by = st.selectbox(
            "Sort By:",
            options=["Highest Score", "Skill Match", "Name (A-Z)", "Personality Score"],
            key="sort_by"
        )
        if st.button("Refresh", use_container_width=True):
            st.rerun()

    try:
        # Apply filters
        if selected_field != "All Fields":
            applicants = [app for app in applicants if app.get('job_field') == selected_field]
        if filter_job != "All Positions":
            applicants = [app for app in applicants if app.get('job_occupation') == filter_job]
        
        for app in applicants:
            # If ontology already has overall/component scores, keep them; otherwise compute fresh
            if 'overall_fit_score' not in app or app['overall_fit_score'] is None:
                app['overall_fit_score'] = calculate_overall_fit_score(app)
            elif 'score_breakdown' not in app:
                # Still compute breakdown for UI if missing
                calculate_overall_fit_score(app)
        
        if sort_by == "Highest Score":
            applicants.sort(key=lambda x: x.get('overall_fit_score', 0), reverse=True)
        elif sort_by == "Skill Match":
            applicants.sort(key=lambda x: x.get('skill_match_percentage', 0), reverse=True)
        elif sort_by == "Name (A-Z)":
            applicants.sort(key=lambda x: x['name'])
        else:
            applicants.sort(key=lambda x: sum(x['scores'].values()) / len(x['scores']) if x['scores'] else 0, reverse=True)
        
        if not applicants:
            st.info("No applicant data available!")
        else:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Applicants", len(applicants))
            with col2:
                avg_skill = sum(app.get('skill_match_percentage', 0) for app in applicants) / len(applicants)
                st.metric("Avg Skill Match", f"{avg_skill:.1f}%")
            with col3:
                avg_overall = sum(app.get('overall_fit_score', 0) for app in applicants) / len(applicants)
                st.metric("Avg Overall Score", f"{avg_overall:.1f}")
            with col4:
                high_match = len([app for app in applicants if app.get('skill_match_percentage', 0) >= 75])
                st.metric("High Match (≥75%)", high_match)
            
            st.markdown("---")
            
            for idx, applicant in enumerate(applicants):
                overall_score = applicant.get('overall_fit_score', 0)
                interpretation, recommendation, status_type = get_score_interpretation(overall_score)
                
                with st.expander(f"{applicant['name']} | {interpretation}: {overall_score}/100 {recommendation}", expanded=False):
                    # TOP SECTION - Applicant Info (Left) and Big Five Plot (Right)
                    col_top_left, col_top_right = st.columns([1, 1])
                    
                    with col_top_left:
                        st.subheader(f"{applicant['name']}")
                        
                        # Job Preferences
                        if applicant['job_field'] or applicant['job_occupation']:
                            st.markdown("**Job Preferences**")
                            col1, col2 = st.columns(2)
                            with col1:
                                if applicant['job_field']:
                                    st.info(f"**Field:** {applicant['job_field'].replace('_', ' ').title()}")
                            with col2:
                                if applicant['job_occupation']:
                                    st.info(f"**Position:** {applicant['job_occupation'].replace('_', ' ').title()}")
                        
                        # Total Score
                        st.markdown("**Overall Fit Score**")
                        total_score = overall_score
                        
                        if total_score >= 80:
                            st.success(f"# {total_score}/100")
                            st.caption("Excellent Match")
                        elif total_score >= 65:
                            st.warning(f"# {total_score}/100")
                            st.caption("Good Match")
                        elif total_score >= 50:
                            st.info(f"# {total_score}/100")
                            st.caption("Fair Match")
                        else:
                            st.error(f"# {total_score}/100")
                            st.caption("Weak Match")
                    
                    with col_top_right:
                        if applicant['scores']:
                            st.subheader("Big Five Personality")
                            
                            # Radar chart
                            radar_fig = create_radar_chart(applicant['scores'])
                            st.plotly_chart(radar_fig, use_container_width=True, key=f"radar_{idx}_{applicant['name']}")
                            
                            # Find dominant trait
                            dominant_trait = max(applicant['scores'], key=applicant['scores'].get)
                            dominant_score = applicant['scores'][dominant_trait]
                            st.info(f"**Dominant Trait:** {dominant_trait} ({dominant_score:.2f}/5.00)")
                        else:
                            st.warning("No Big Five scores calculated yet. Run analysis first!")
                    
                    st.markdown("---")
                    
                    # MIDDLE SECTION - Score Breakdown
                    if 'score_breakdown' in applicant:
                        st.subheader("Score Breakdown (Weighted)")
                        breakdown = applicant['score_breakdown']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Personality (25%)", f"{breakdown.get('personality', 0):.1f}/25")
                        with col2:
                            st.metric("Category Fit (20%)", f"{breakdown.get('category_fit', 0):.1f}/20")
                        with col3:
                            matched = breakdown.get('matched_skills', 0)
                            required = breakdown.get('required_skills', 0)
                            skill_label = f"Skills (35%)"
                            if required > 0:
                                skill_label += f" [{matched}/{required}]"
                            st.metric(skill_label, f"{breakdown.get('skill_match', 0):.1f}/35")
                        with col4:
                            years = breakdown.get('years_experience', 0)
                            st.metric(f"Experience (20%) [{years}yr]", f"{breakdown.get('experience', 0):.1f}/20")
                        
                        st.markdown("")
                        st.caption("**Score Distribution:**")
                        score_data = {
                            'Personality': breakdown.get('personality', 0),
                            'Category Fit': breakdown.get('category_fit', 0),
                            'Skill Match': breakdown.get('skill_match', 0),
                            'Experience': breakdown.get('experience', 0)
                        }
                        max_scores = {'Personality': 25, 'Category Fit': 20, 'Skill Match': 35, 'Experience': 20}
                        
                        for component, score_val in score_data.items():
                            max_val = max_scores[component]
                            pct = (score_val / max_val) * 100 if max_val > 0 else 0
                            st.progress(pct / 100, text=f"{component}: {score_val:.1f}/{max_val} ({pct:.0f}%)")
                        
                        st.markdown("---")
                    elif 'category_fit_score' in applicant or 'skill_match_score' in applicant or 'experience_score' in applicant:
                        # Display scores loaded from ontology
                        st.subheader("Score Breakdown (from Ontology)")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            # Calculate personality score from Big Five averages
                            if applicant['scores']:
                                avg = sum(applicant['scores'].values()) / len(applicant['scores'])
                                personality_score = (avg / 5.0) * 25
                                st.metric("Personality (25%)", f"{personality_score:.1f}/25")
                        with col2:
                            category_score = applicant.get('category_fit_score', 0)
                            st.metric("Category Fit (20%)", f"{category_score:.1f}/20")
                        with col3:
                            skill_score = applicant.get('skill_match_score', 0)
                            st.metric("Skills (35%)", f"{skill_score:.1f}/35")
                        with col4:
                            exp_score = applicant.get('experience_score', 0)
                            years = applicant.get('years_experience', 0)
                            st.metric(f"Experience (20%) [{years}yr]", f"{exp_score:.1f}/20")
                        
                        st.markdown("---")
                    
                    # BOTTOM SECTION - Experience & Skills
                    # BOTTOM SECTION - Experience & Skills
                    if applicant['years_experience'] is not None or applicant['soft_skills'] or applicant['hard_skills']:
                        st.subheader("Experience & Skills")
                        
                        # Show skill match details if job occupation is selected
                        if applicant.get('job_occupation'):
                            match_pct, match_details = calculate_skill_match(
                                applicant.get('hard_skills', []),
                                applicant.get('soft_skills', []),
                                applicant['job_occupation']
                            )
                            
                            if match_details['matched']:
                                matched_display = ', '.join([s.replace('_', ' ').title() for s in match_details['matched'][:5]])
                                if len(match_details['matched']) > 5:
                                    matched_display += f" ... (+{len(match_details['matched'])-5} more)"
                                st.success(f"**Matched Skills ({len(match_details['matched'])}):** {matched_display}")
                                
                                # Show all matched skills if more than 5
                                if len(match_details['matched']) > 5:
                                    all_matched = ', '.join([s.replace('_', ' ').title() for s in match_details['matched']])
                                    st.caption(f"All matched: {all_matched}")
                            
                            if match_details['missing']:
                                missing_display = ', '.join([s.replace('_', ' ').title() for s in match_details['missing'][:5]])
                                if len(match_details['missing']) > 5:
                                    missing_display += f" ... (+{len(match_details['missing'])-5} more)"
                                st.warning(f"**Missing Required Skills ({len(match_details['missing'])}):** {missing_display}")
                                
                                # Show all missing skills if more than 5
                                if len(match_details['missing']) > 5:
                                    all_missing = ', '.join([s.replace('_', ' ').title() for s in match_details['missing']])
                                    st.caption(f"All missing: {all_missing}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if applicant['years_experience'] is not None:
                                st.metric("Years of Experience", f"{applicant['years_experience']} years")
                        with col2:
                            if applicant['soft_skills']:
                                st.write("**Soft Skills:**")
                                for skill in applicant['soft_skills'][:3]:  # Show first 3
                                    st.caption(f"• {skill.replace('_', ' ').title()}")
                                if len(applicant['soft_skills']) > 3:
                                    st.caption(f"+{len(applicant['soft_skills'])-3} more")
                        with col3:
                            if applicant['hard_skills']:
                                st.write("**Hard Skills:**")
                                for skill in applicant['hard_skills'][:3]:  # Show first 3
                                    st.caption(f"• {skill.replace('_', ' ').title()}")
                                if len(applicant['hard_skills']) > 3:
                                    st.caption(f"+{len(applicant['hard_skills'])-3} more")
    
    except FileNotFoundError:
        st.error("Reasoned ontology file not found. Please run analysis first!")

elif page == "🔄 Run Analysis":
    st.header("Run Analysis & Reasoning")
    
    st.markdown("""
    This will:
    1. Calculate Big Five personality scores for all applicants
    2. Run OWL reasoner to classify applicants into job categories
    3. Generate recommendations based on personality traits
    """)
    
    if st.button("🚀 Run Complete Analysis", type="primary"):
        with st.spinner("Running analysis... This may take 10-15 seconds..."):
            progress_bar = st.progress(0)
            
            # Step 1
            st.info("Step 1/3: Calculating Big Five scores...")
            progress_bar.progress(33)
            
            # Step 2
            st.info("Step 2/3: Running OWL reasoner...")
            progress_bar.progress(66)
            
            success, message = run_complete_workflow()
            
            progress_bar.progress(100)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                st.info("💡 Go to 'View Applicants' to see the results!")
            else:
                st.error(f"❌ {message}")

# Footer
st.markdown("---")
st.caption("Built with Owlready2 & Streamlit | Big Five Personality Model | OWL 2 DL Reasoning")