import pandas as pd

# === 1️⃣ Baca file CSV ===
df = pd.read_csv("All_Job_Families.csv")

# === 2️⃣ Base URI Ontologi kamu ===
base_uri = "http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/untitled-ontology-23/"

# === 3️⃣ Header TTL ===
ttl_lines = [
    "@prefix : <http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/untitled-ontology-23/> .",
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
    "@prefix xml: <http://www.w3.org/XML/1998/namespace> .",
    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
    "@base <http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/untitled-ontology-23/> .",
    "",
    "<http://www.semanticweb.org/asyifafadhilah/ontologies/2025/10/untitled-ontology-23> rdf:type owl:Ontology .",
    "",
    # === Definisi kelas ===
    ":JobOccupation rdf:type owl:Class .",
    ":JobField rdf:type owl:Class .",
    "",
    # === Definisi object property ===
    ":groupedBy rdf:type owl:ObjectProperty ;",
    "    rdfs:domain :JobOccupation ;",
    "    rdfs:range :JobField .",
    ""
]

# === 4️⃣ Tambahkan individual JobField ===
job_fields = df["Job Family"].drop_duplicates()

for field in job_fields:
    field_id = field.strip().replace(" ", "_").replace("/", "_")
    ttl_lines.append(f":{field_id} rdf:type :JobField .")

ttl_lines.append("")

# === 5️⃣ Tambahkan individual JobOccupation dan relasinya ===
for _, row in df.iterrows():
    occ = row["Occupation"].strip().replace(" ", "_").replace("/", "_")
    field = row["Job Family"].strip().replace(" ", "_").replace("/", "_")
    ttl_lines.append(f":{occ} rdf:type :JobOccupation ;")
    ttl_lines.append(f"    :groupedBy :{field} .")
    ttl_lines.append("")

# === 6️⃣ Simpan file TTL ===
with open("jobs_converted.ttl", "w", encoding="utf-8") as f:
    f.write("\n".join(ttl_lines))

print("✅ Selesai! File 'jobs_converted.ttl' siap diimport ke Protégé.")
