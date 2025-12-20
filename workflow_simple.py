#!/usr/bin/env python3
"""
Simple workflow: Calculate Big Five → Run Reasoner → Show Results
Uses Owlready2 for everything (faster than RDFLib for large files).
"""

from owlready2 import *
import os

def step1_calculate_scores():
    """Calculate Big Five scores from Answer individuals using Owlready2."""
    print("="*60)
    print("STEP 1: Calculate Big Five Scores")
    print("="*60)
    
    # Load ontology
    print("\nLoading jobs.owl...")
    onto = get_ontology("file://jobs.owl").load()
    print(f"✓ Loaded ontology: {onto.base_iri}")
    
    # Define trait mapping
    trait_mapping = {
        'Agreeableness': list(range(1, 7)),      # Q1-Q6
        'Conscientiousness': list(range(7, 13)),  # Q7-Q12
        'Extraversion': list(range(13, 19)),      # Q13-Q18
        'Neuroticism': list(range(19, 25)),       # Q19-Q24
        'Openness': list(range(25, 31))           # Q25-Q30
    }
    
    # Get all Person individuals
    with onto:
        Person = onto.Person
        persons = list(Person.instances())
        print(f"\n✓ Found {len(persons)} Person individuals")
        
        # Process each person
        for person in persons:
            print(f"\n  Processing: {person.name}")
            
            # Get answers
            if hasattr(person, 'hasAnswer'):
                answers = {}
                for answer in person.hasAnswer:
                    if hasattr(answer, 'forQuestion') and hasattr(answer, 'answerScore'):
                        q_name = answer.forQuestion[0].name if answer.forQuestion else None
                        score = answer.answerScore[0] if answer.answerScore else None
                        
                        if q_name and q_name.startswith('Q'):
                            q_num = int(q_name[1:])
                            answers[q_num] = score
                
                print(f"    Found {len(answers)} answers")
                
                # Calculate trait scores
                if answers:
                    trait_scores = {}
                    for trait, q_nums in trait_mapping.items():
                        scores = [answers[q] for q in q_nums if q in answers]
                        if scores:
                            avg_score = round(sum(scores) / len(scores), 2)
                            trait_scores[trait] = avg_score
                    
                    # Display scores
                    print(f"    Big Five scores:")
                    for trait, score in trait_scores.items():
                        print(f"      {trait}: {score}")
                    
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
                    
                    print(f"    ✓ Scores added to ontology")
                else:
                    print(f"    ⚠ No answers found")
            else:
                print(f"    ⚠ No hasAnswer property")
        
        # Save
        output_file = "jobs_with_scores.owl"
        print(f"\n✓ Saving to {output_file}...")
        onto.save(file=output_file, format="rdfxml")
        print(f"✓ Saved!")
    
    return output_file

def step2_run_reasoner(input_file):
    """Run Pellet reasoner on ontology."""
    print("\n" + "="*60)
    print("STEP 2: Run Reasoner")
    print("="*60)
    
    print(f"\nLoading {input_file}...")
    onto = get_ontology(f"file://{input_file}").load()
    print(f"✓ Loaded ontology")
    
    # Sync reasoner
    print("\n🔄 Running Pellet reasoner (this may take a while)...")
    try:
        with onto:
            sync_reasoner_pellet(infer_property_values=True)
        print("✓ Reasoning complete!")
        
        # Save reasoned ontology
        output_file = "jobs_reasoned.owl"
        onto.save(file=output_file, format="rdfxml")
        print(f"✓ Saved reasoned ontology to {output_file}")
        
        return output_file
    except Exception as e:
        print(f"❌ Error during reasoning: {e}")
        return None

def step3_show_results(reasoned_file):
    """Show classification results."""
    print("\n" + "="*60)
    print("STEP 3: Classification Results")
    print("="*60)
    
    print(f"\nLoading {reasoned_file}...")
    onto = get_ontology(f"file://{reasoned_file}").load()
    
    # Get all fit classes
    with onto:
        Person = onto.Person
        persons = list(Person.instances())
        
        print(f"\n✓ Found {len(persons)} persons\n")
        
        # Check each fit category
        fit_classes = [
            'HighFitForAnalyticalRoles',
            'HighFitForTechnicalRoles',
            'HighFitForInterpersonalRoles',
            'HighFitForSupportRoles',
            'HighFitForWritingRoles'
        ]
        
        for person in persons:
            print(f"\n{'='*40}")
            print(f"Person: {person.name}")
            print(f"{'='*40}")
            
            # Show Big Five scores
            if hasattr(person, 'hasOpennessScore'):
                print(f"\n📊 Big Five Scores:")
                if hasattr(person, 'hasOpennessScore') and person.hasOpennessScore:
                    print(f"  Openness: {person.hasOpennessScore[0]}")
                if hasattr(person, 'hasConscientiousnessScore') and person.hasConscientiousnessScore:
                    print(f"  Conscientiousness: {person.hasConscientiousnessScore[0]}")
                if hasattr(person, 'hasExtraversionScore') and person.hasExtraversionScore:
                    print(f"  Extraversion: {person.hasExtraversionScore[0]}")
                if hasattr(person, 'hasAgreeablenessScore') and person.hasAgreeablenessScore:
                    print(f"  Agreeableness: {person.hasAgreeablenessScore[0]}")
                if hasattr(person, 'hasNeuroticismScore') and person.hasNeuroticismScore:
                    print(f"  Neuroticism: {person.hasNeuroticismScore[0]}")
            else:
                print(f"\n⚠ No Big Five scores found")
            
            # Show inferred classes
            print(f"\n🎯 Fit Categories:")
            found_fit = False
            for cls_name in fit_classes:
                try:
                    cls = onto[cls_name]
                    if cls and person in cls.instances():
                        print(f"  ✓ {cls_name}")
                        found_fit = True
                except:
                    pass
            
            if not found_fit:
                print(f"  ℹ No fit categories inferred")

def main():
    """Run complete workflow."""
    print("\n" + "="*60)
    print("COMPLETE WORKFLOW: Big Five → Reasoner → Results")
    print("="*60)
    
    try:
        # Step 1: Calculate scores
        scores_file = step1_calculate_scores()
        
        # Step 2: Run reasoner
        reasoned_file = step2_run_reasoner(scores_file)
        
        if reasoned_file:
            # Step 3: Show results
            step3_show_results(reasoned_file)
        
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
