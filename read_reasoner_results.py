"""
Contoh cara membaca hasil reasoner dari jobs_clean.ttl dalam aplikasi
"""

from owlready2 import *
import os

def load_reasoned_ontology():
    """
    Load ontology yang sudah berisi hasil reasoning
    """
    ontology_path = "jobs_clean.ttl"
    
    if not os.path.exists(ontology_path):
        print(f"❌ Error: File {ontology_path} tidak ditemukan!")
        return None
    
    print(f"📂 Loading reasoned ontology from: {ontology_path}")
    onto = get_ontology(f"file://{os.path.abspath(ontology_path)}").load()
    print("✅ Ontology loaded!\n")
    
    return onto


def get_person_fit_categories(person_name, onto):
    """
    Ambil kategori fit untuk seorang applicant
    
    Args:
        person_name (str): Nama person/applicant
        onto: Loaded ontology object
    
    Returns:
        list: List of fit categories yang cocok
    """
    try:
        person = onto[person_name]
        
        if person is None:
            print(f"⚠️  Person '{person_name}' tidak ditemukan")
            return []
        
        # List semua fit categories
        fit_categories = []
        
        # Cek apakah person termasuk dalam kategori fit
        fit_class_names = [
            "HighFitForAnalyticalRoles",
            "HighFitForTechnicalRoles",
            "HighFitForInterpersonalRoles", 
            "HighFitForSupportRoles",
            "HighFitForWritingRoles"
        ]
        
        for category_name in fit_class_names:
            try:
                category_class = onto[category_name]
                if category_class in person.is_a:
                    fit_categories.append(category_name)
            except:
                continue
        
        return fit_categories
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []


def get_recommended_jobs_for_person(person_name, onto):
    """
    Dapatkan rekomendasi job berdasarkan fit categories
    
    Args:
        person_name (str): Nama person/applicant
        onto: Loaded ontology object
    
    Returns:
        dict: Dictionary dengan kategori dan job yang cocok
    """
    fit_categories = get_person_fit_categories(person_name, onto)
    
    if not fit_categories:
        return {}
    
    # Mapping kategori ke job types
    job_mapping = {
        "HighFitForAnalyticalRoles": [
            "DataScientist", "DataAnalyst", "UIUXDesigner", 
            "UXResearcherJob", "ProductManager", "ContentStrategistJob"
        ],
        "HighFitForTechnicalRoles": [
            "SoftwareEngineer", "DevOpsEngineer", "QAEngineer",
            "SecurityAnalyst", "TaxOfficerJob", "FinanceAnalystJob"
        ],
        "HighFitForInterpersonalRoles": [
            "AccountExecutive", "SalesDevelopmentRepresentativeJob",
            "PublicRelationsSpecialist", "PartnerAcquisitionJob", "EventMarketingJob"
        ],
        "HighFitForSupportRoles": [
            "HRManager", "CustomerSuccessJob", "CustomerSupportJob", "PeopleAndCultureJob"
        ],
        "HighFitForWritingRoles": [
            "ContentWriter", "CopywriterJob", "UXWriterJob"
        ]
    }
    
    recommendations = {}
    for category in fit_categories:
        if category in job_mapping:
            recommendations[category] = job_mapping[category]
    
    return recommendations


def display_person_analysis(person_name, onto):
    """
    Tampilkan analisis lengkap untuk seorang person
    """
    print("="*70)
    print(f"👤 ANALYSIS FOR: {person_name}")
    print("="*70)
    
    try:
        person = onto[person_name]
        
        if person is None:
            print(f"⚠️  Person '{person_name}' tidak ditemukan")
            return
        
        # Tampilkan Big Five scores
        print("\n📊 BIG FIVE PERSONALITY SCORES:")
        if hasattr(person, 'hasOpennessScore') and person.hasOpennessScore:
            print(f"   - Openness: {person.hasOpennessScore[0]}")
        if hasattr(person, 'hasConscientiousnessScore') and person.hasConscientiousnessScore:
            print(f"   - Conscientiousness: {person.hasConscientiousnessScore[0]}")
        if hasattr(person, 'hasExtraversionScore') and person.hasExtraversionScore:
            print(f"   - Extraversion: {person.hasExtraversionScore[0]}")
        if hasattr(person, 'hasAgreeablenessScore') and person.hasAgreeablenessScore:
            print(f"   - Agreeableness: {person.hasAgreeablenessScore[0]}")
        if hasattr(person, 'hasNeuroticismScore') and person.hasNeuroticismScore:
            print(f"   - Neuroticism: {person.hasNeuroticismScore[0]}")
        
        # Tampilkan fit categories
        fit_categories = get_person_fit_categories(person_name, onto)
        print(f"\n🎯 FIT CATEGORIES ({len(fit_categories)}):")
        if fit_categories:
            for category in fit_categories:
                print(f"   ✓ {category}")
        else:
            print("   ⚠️  No fit categories found (scores may not meet thresholds)")
        
        # Tampilkan rekomendasi job
        recommendations = get_recommended_jobs_for_person(person_name, onto)
        print(f"\n💼 RECOMMENDED JOBS:")
        if recommendations:
            for category, jobs in recommendations.items():
                print(f"\n   📂 {category}:")
                for job in jobs:
                    print(f"      - {job}")
        else:
            print("   ⚠️  No job recommendations available")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def list_all_persons_with_fit(onto):
    """
    List semua person beserta fit categories mereka
    """
    print("="*70)
    print("📋 ALL PERSONS WITH FIT CLASSIFICATIONS")
    print("="*70)
    
    try:
        person_class = onto["Person"]
        persons = list(person_class.instances())
        
        if not persons:
            print("⚠️  No persons found")
            return
        
        print(f"\nTotal persons: {len(persons)}\n")
        
        for person in persons:
            fit_categories = get_person_fit_categories(person.name, onto)
            
            print(f"👤 {person.name}")
            if fit_categories:
                print(f"   ✓ Fit for {len(fit_categories)} category/categories:")
                for cat in fit_categories:
                    print(f"      - {cat}")
            else:
                print(f"   ⚠️  No fit categories")
            print()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


# ============================================================================
# CONTOH PENGGUNAAN
# ============================================================================

if __name__ == "__main__":
    # 1. Load ontology yang sudah di-reason
    onto = load_reasoned_ontology()
    
    if onto is None:
        print("❌ Failed to load ontology")
        exit(1)
    
    # 2. Contoh: Analisis untuk person tertentu
    # Ganti 'Ace' dengan nama person yang ada di ontology Anda
    print("\n" + "="*70)
    print("EXAMPLE 1: Analyze specific person")
    print("="*70)
    display_person_analysis("Ace", onto)
    
    # 3. Contoh: List semua person dengan fit categories
    print("\n" + "="*70)
    print("EXAMPLE 2: List all persons")  
    print("="*70)
    list_all_persons_with_fit(onto)
    
    # 4. Contoh: Get fit categories untuk person
    print("\n" + "="*70)
    print("EXAMPLE 3: Get fit categories programmatically")
    print("="*70)
    fit_cats = get_person_fit_categories("Ace", onto)
    print(f"Fit categories for Ace: {fit_cats}")
    
    # 5. Contoh: Get job recommendations
    print("\n" + "="*70)
    print("EXAMPLE 4: Get job recommendations programmatically")
    print("="*70)
    recommendations = get_recommended_jobs_for_person("Ace", onto)
    print(f"Job recommendations for Ace: {recommendations}")
    
    print("\n✨ Done!")
