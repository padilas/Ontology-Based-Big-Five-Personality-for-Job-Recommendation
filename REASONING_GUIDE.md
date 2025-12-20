# 🧠 Ontology Reasoning & Classification System

## 📋 Overview

Sistem ini menggunakan **OWL reasoning** untuk mengklasifikasikan applicant berdasarkan **Big Five Personality scores** dan merekomendasikan job yang sesuai.

---

## 🎯 Fit Categories

### GROUP 1: Analytical & Creative Roles
**Kriteria:**
- Openness ≥ 4.0
- Conscientiousness ≥ 4.0
- Neuroticism ≤ 2.5

**Jobs:**
- Data Scientist
- Data Analyst
- UI/UX Designer
- UX Researcher
- Product Manager
- Content Strategist

---

### GROUP 2: Technical & Structured Roles
**Kriteria:**
- Conscientiousness ≥ 4.2
- Neuroticism ≤ 2.0

**Jobs:**
- Software Engineer
- DevOps Engineer
- QA Engineer
- Security Analyst
- Tax Officer
- Finance Analyst

---

### GROUP 3: Interpersonal & Outgoing Roles
**Kriteria:**
- Extraversion ≥ 4.0
- Agreeableness ≥ 3.5

**Jobs:**
- Account Executive
- Sales Development Representative
- Public Relations Specialist
- Partner Acquisition
- Event Marketing

---

### GROUP 4: People & Support Roles
**Kriteria:**
- Agreeableness ≥ 4.2
- Extraversion ≥ 3.5

**Jobs:**
- HR Manager
- Customer Success
- Customer Support
- People and Culture

---

### GROUP 5: Content & Writing Roles
**Kriteria:**
- Openness ≥ 4.0
- Conscientiousness ≥ 3.5

**Jobs:**
- Content Writer
- Copywriter
- UX Writer

---

## 🚀 Cara Menggunakan

### 1️⃣ Jalankan Reasoner

Jalankan reasoner untuk mengklasifikasikan semua applicant:

```bash
python run_reasoner.py
```

**Output:**
- Menampilkan statistik ontology sebelum & sesudah reasoning
- Menampilkan semua inferred classifications
- **Menyimpan hasil reasoning langsung ke `jobs_clean.ttl`**

**Proses:**
1. Load `jobs_clean.ttl`
2. Jalankan HermiT/Pellet reasoner
3. Infer classifications berdasarkan Big Five scores
4. Save semua hasil ke `jobs_clean.ttl`

---

### 2️⃣ Baca Hasil Reasoning di Aplikasi

Setelah reasoning selesai, gunakan script ini untuk membaca hasilnya:

```bash
python read_reasoner_results.py
```

**Fungsi yang tersedia:**

#### A. Analisis Person Tertentu
```python
from read_reasoner_results import *

onto = load_reasoned_ontology()
display_person_analysis("Ace", onto)
```

**Output:**
```
👤 ANALYSIS FOR: Ace
📊 BIG FIVE PERSONALITY SCORES:
   - Openness: 4.5
   - Conscientiousness: 4.2
   - Extraversion: 3.0
   - Agreeableness: 3.8
   - Neuroticism: 2.0

🎯 FIT CATEGORIES (1):
   ✓ HighFitForAnalyticalRoles

💼 RECOMMENDED JOBS:
   📂 HighFitForAnalyticalRoles:
      - DataScientist
      - DataAnalyst
      - UIUXDesigner
      - ProductManager
```

#### B. List Semua Person
```python
list_all_persons_with_fit(onto)
```

#### C. Get Fit Categories Programmatically
```python
fit_categories = get_person_fit_categories("Ace", onto)
# Returns: ['HighFitForAnalyticalRoles']
```

#### D. Get Job Recommendations
```python
recommendations = get_recommended_jobs_for_person("Ace", onto)
# Returns: {'HighFitForAnalyticalRoles': ['DataScientist', 'DataAnalyst', ...]}
```

---

## 📁 File Structure

```
jobs_clean.ttl              # Ontology utama + Rules + Hasil reasoning
run_reasoner.py             # Script untuk jalankan reasoner
read_reasoner_results.py    # Script untuk baca hasil reasoning
REASONING_GUIDE.md          # Dokumentasi ini
```

---

## 🔧 Requirements

Install dependencies:

```bash
pip install owlready2
```

**Note:** Owlready2 sudah include HermiT reasoner. Tidak perlu install tambahan.

---

## 📊 Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    REASONING WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘

1. Add applicant data (Big Five scores) ke jobs_clean.ttl
   ↓
2. Run: python run_reasoner.py
   ↓
3. Reasoner infer classifications berdasarkan rules
   ↓
4. Hasil disimpan ke jobs_clean.ttl
   ↓
5. Load jobs_clean.ttl di aplikasi Anda
   ↓
6. Query hasil reasoning untuk recommendations
```

---

## 💡 Tips & Best Practices

### 1. **Jalankan Reasoning Setelah Add Applicant**
Setiap kali ada applicant baru atau update Big Five scores, jalankan ulang reasoner:
```bash
python run_reasoner.py
```

### 2. **Load Once, Query Many Times**
Di aplikasi production, load ontology sekali saja:
```python
onto = load_reasoned_ontology()  # Load once

# Query berkali-kali
for person_name in person_list:
    recommendations = get_recommended_jobs_for_person(person_name, onto)
```

### 3. **Cache Results**
Untuk performance, cache hasil reasoning:
```python
# Cache fit categories
fit_cache = {}
for person in persons:
    fit_cache[person.name] = get_person_fit_categories(person.name, onto)
```

### 4. **Validate Scores Before Reasoning**
Pastikan Big Five scores valid (0.0 - 5.0):
```python
def validate_scores(scores):
    for trait, score in scores.items():
        if not (0.0 <= score <= 5.0):
            raise ValueError(f"Invalid {trait} score: {score}")
```

---

## 🐛 Troubleshooting

### Problem: "No fit categories found"
**Cause:** Scores tidak memenuhi threshold kriteria.

**Solution:** 
- Cek Big Five scores applicant
- Sesuaikan threshold di rules (edit `jobs_clean.ttl`)

---

### Problem: Reasoning terlalu lama
**Cause:** Ontology terlalu besar atau rules kompleks.

**Solution:**
- Gunakan Pellet reasoner (lebih cepat untuk data besar)
- Optimasi rules (simplify restrictions)

---

### Problem: "HermiT failed"
**Cause:** HermiT tidak support beberapa OWL constructs.

**Solution:**
- Script otomatis fallback ke Pellet
- Atau edit `run_reasoner.py` untuk langsung pakai Pellet

---

## 📚 Example Use Cases

### Use Case 1: Job Recommendation System
```python
onto = load_reasoned_ontology()

def recommend_jobs(applicant_name):
    recommendations = get_recommended_jobs_for_person(applicant_name, onto)
    
    if not recommendations:
        return "No suitable jobs found"
    
    # Ambil top 5 jobs dari semua categories
    all_jobs = []
    for jobs in recommendations.values():
        all_jobs.extend(jobs)
    
    return all_jobs[:5]
```

### Use Case 2: Bulk Analysis
```python
onto = load_reasoned_ontology()

person_class = onto["Person"]
persons = list(person_class.instances())

results = []
for person in persons:
    fit_categories = get_person_fit_categories(person.name, onto)
    results.append({
        'name': person.name,
        'fit_count': len(fit_categories),
        'categories': fit_categories
    })

# Sort by fit count
results.sort(key=lambda x: x['fit_count'], reverse=True)
```

### Use Case 3: Export to JSON
```python
import json

onto = load_reasoned_ontology()

def export_recommendations_to_json(output_file="recommendations.json"):
    person_class = onto["Person"]
    persons = list(person_class.instances())
    
    data = {}
    for person in persons:
        recommendations = get_recommended_jobs_for_person(person.name, onto)
        data[person.name] = recommendations
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Exported to {output_file}")

export_recommendations_to_json()
```

---

## 🎓 Understanding the Rules

Rules menggunakan **OWL 2 Restrictions** untuk define criteria:

```turtle
:HighFitForAnalyticalRoles a owl:Class ;
    owl:equivalentClass [ a owl:Class ;
        owl:intersectionOf (
            :Person
            [ owl:onProperty :hasOpennessScore ; 
              owl:someValuesFrom [ owl:onDatatype xsd:decimal ; 
                                  owl:withRestrictions ( [ xsd:minInclusive "4.0"^^xsd:decimal ] ) ] ]
            ...
        )
    ] .
```

**Artinya:**
- Class `HighFitForAnalyticalRoles` equivalent dengan
- Intersection (AND) dari:
  - Individual adalah `Person`
  - DAN punya `hasOpennessScore` ≥ 4.0
  - DAN punya `hasConscientiousnessScore` ≥ 4.0
  - DAN punya `hasNeuroticismScore` ≤ 2.5

Reasoner otomatis classify individual yang memenuhi semua kriteria!

---

## 📞 Support

Untuk pertanyaan atau issues, check:
1. Validasi Big Five scores (harus ada & valid)
2. Run reasoner dengan `-v` flag untuk verbose output
3. Check reasoner logs untuk error details

---

## ✨ Next Steps

1. **Tune Thresholds:** Adjust score thresholds di rules
2. **Add More Categories:** Tambah kategori fit baru
3. **Integrate to Web App:** Load ontology di Flask/FastAPI
4. **Add Weights:** Weight different traits differently per job
5. **Machine Learning:** Combine dengan ML untuk dynamic thresholds

---

**Happy Reasoning! 🚀**
