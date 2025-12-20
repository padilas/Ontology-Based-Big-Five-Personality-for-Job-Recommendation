#!/usr/bin/env python3
"""
Calculate Big Five personality scores from Answer individuals and write back to TTL.
"""

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from collections import defaultdict

# Define namespace
ONTO = Namespace("http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/recruitment-ontology#")

# Big Five trait mapping (question numbers to trait)
TRAIT_MAPPING = {
    'Agreeableness': list(range(1, 7)),      # Q1-Q6
    'Conscientiousness': list(range(7, 13)),  # Q7-Q12
    'Extraversion': list(range(13, 19)),      # Q13-Q18
    'Neuroticism': list(range(19, 25)),       # Q19-Q24
    'Openness': list(range(25, 31))           # Q25-Q30
}

def load_ontology(file_path):
    """Load the ontology from TTL file."""
    print(f"Loading ontology from {file_path}...")
    g = Graph()
    g.parse(file_path, format='turtle')
    print(f"Loaded {len(g)} triples")
    return g

def get_all_persons(g):
    """Get all Person individuals."""
    persons = set()
    for s in g.subjects(RDF.type, ONTO.Person):
        persons.add(s)
    print(f"Found {len(persons)} Person individuals")
    return persons

def get_person_answers(g, person):
    """Get all Answer individuals for a person."""
    answers = {}
    for answer in g.objects(person, ONTO.hasAnswer):
        # Get the question this answer is for
        for question in g.objects(answer, ONTO.forQuestion):
            # Get the score
            for score in g.objects(answer, ONTO.answerScore):
                # Extract question number from URI (e.g., Q1 -> 1)
                q_str = str(question).split('#')[-1]  # Get local name
                if q_str.startswith('Q'):
                    q_num = int(q_str[1:])
                    answers[q_num] = int(score)
    return answers

def calculate_trait_scores(answers):
    """Calculate average score for each Big Five trait."""
    trait_scores = {}
    
    for trait, question_nums in TRAIT_MAPPING.items():
        scores = [answers.get(q) for q in question_nums if q in answers]
        if scores:
            avg_score = sum(scores) / len(scores)
            trait_scores[trait] = round(avg_score, 2)
        else:
            print(f"  Warning: No answers found for {trait}")
    
    return trait_scores

def add_scores_to_graph(g, person, trait_scores):
    """Add calculated scores as triples to the graph."""
    score_properties = {
        'Agreeableness': ONTO.hasAgreeablenessScore,
        'Conscientiousness': ONTO.hasConscientiousnessScore,
        'Extraversion': ONTO.hasExtraversionScore,
        'Neuroticism': ONTO.hasNeuroticismScore,
        'Openness': ONTO.hasOpennessScore
    }
    
    for trait, score in trait_scores.items():
        prop = score_properties[trait]
        # Remove existing score if any
        g.remove((person, prop, None))
        # Add new score
        g.add((person, prop, Literal(score, datatype=XSD.decimal)))

def main():
    # Load ontology
    g = load_ontology('jobs_clean.ttl')
    
    # Get all persons
    persons = get_all_persons(g)
    
    # Calculate scores for each person
    for person in persons:
        person_name = str(person).split('#')[-1]
        print(f"\nProcessing {person_name}...")
        
        # Get answers
        answers = get_person_answers(g, person)
        print(f"  Found {len(answers)} answers")
        
        if answers:
            # Calculate trait scores
            trait_scores = calculate_trait_scores(answers)
            
            # Display scores
            print(f"  Big Five scores:")
            for trait, score in trait_scores.items():
                print(f"    {trait}: {score}")
            
            # Add to graph
            add_scores_to_graph(g, person, trait_scores)
        else:
            print(f"  Warning: No answers found for {person_name}")
    
    # Save updated ontology
    output_file = 'jobs_with_scores.ttl'
    print(f"\nSaving updated ontology to {output_file}...")
    g.serialize(destination=output_file, format='turtle')
    print(f"Done! Wrote {len(g)} triples")
    print(f"\n✅ Big Five scores calculated and saved to {output_file}")
    print(f"\n{'='*60}")
    print(f"NEXT STEPS - Reasoner Classification")
    print(f"{'='*60}")
    print(f"1. Open {output_file} in Protégé")
    print(f"2. Select reasoner: Reasoner → HermiT or ELK")
    print(f"3. Start reasoner: Reasoner → Start reasoner")
    print(f"4. Check inferred types:")
    print(f"   - HighFitApplicant: Conscientiousness ≥ 4.0, Openness ≥ 4.5, Neuroticism ≤ 2.5")
    print(f"   - MediumFitApplicant: Conscientiousness ≥ 3.0 (but not HighFit)")
    print(f"   - LowFitApplicant: Others")
    print(f"5. Run: python rank_applicants.py (for detailed ranking)")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
