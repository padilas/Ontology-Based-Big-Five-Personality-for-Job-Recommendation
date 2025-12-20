import streamlit as st
from owlready2 import *
import pandas as pd
import datetime

# --- CONFIG & LOAD ONTOLOGY ---
onto_kb = get_ontology("jobs.owl").load()
try:
    onto_res = get_ontology("results.owl").load()
except:
    onto_res = get_ontology("http://test.org/results.owl")

with onto_res:
    class Candidate(Thing): pass
    class has_score(DataProperty, Functional): range = [float]
    class applied_for(DataProperty, Functional): range = [str]
    class candidate_name(DataProperty, Functional): range = [str]

# --- HELPER FUNCTIONS ---
def get_all_jobs():
    return [j.name for j in onto_kb.JobOccupation.subclasses()]

def get_skills(job_name):
    job_class = onto_kb[job_name]
    h_skills = [p.value.name for p in job_class.is_a if isinstance(p, Restriction) and p.property == onto_kb.requiresHardSkill]
    s_skills = [p.value.name for p in job_class.is_a if isinstance(p, Restriction) and p.property == onto_kb.requiresSoftSkill]
    return h_skills, s_skills

# --- UI SISTEM ---
st.set_page_config(page_title="RecruitAI - Ontology System", layout="wide")
menu = st.sidebar.selectbox("Menu", ["Pendaftar", "Rekruter (Admin)"])

# ==========================================
# SIDE 1: PENDAFTAR
# ==========================================
if menu == "Pendaftar":
    st.title("📝 Form Pendaftaran Kerja")
    
    with st.form("form_pendaftaran"):
        nama = st.text_input("Nama Lengkap")
        job_list = get_all_jobs()
        posisi = st.selectbox("Pilih Posisi yang Dilamar", job_list)
        
        
        h_req, s_req = get_skills(posisi)
        
        st.subheader("Skill Check")
        col1, col2 = st.columns(2)
        with col1:
            user_h = [st.checkbox(s, key=f"h_{s}") for s in h_req]
        with col2:
            user_s = [st.checkbox(s, key=f"s_{s}") for s in s_req]
            
        st.subheader("Personality Test (30 Soal)")
        st.info("Skala 1 (Sangat Tidak Setuju) sampai 5 (Sangat Setuju)")
        
        
        scores = []
        for i in range(1, 31):
            s = st.select_slider(f"Pertanyaan {i}: Saya merasa senang...", options=[1, 2, 3, 4, 5], key=f"q{i}")
            scores.append(s)
            
        submitted = st.form_submit_button("Kirim Lamaran")
        
        if submitted:
            # --- LOGIKA HITUNG (Backend) ---
            
            total_skill_req = len(h_req) + len(s_req)
            user_skill_count = sum(user_h) + sum(user_s)
            skill_score = (user_skill_count / total_skill_req * 100) if total_skill_req > 0 else 0
            
            p_score = (sum(scores) / 150) * 100 
            
            final_score = (0.6 * skill_score) + (0.4 * p_score)
            
            # --- SIMPAN KE ONTOLOGI BARU (Persistence) ---
            with onto_res:
                new_cand = Candidate(nama.replace(" ", "_"))
                new_cand.candidate_name = nama
                new_cand.applied_for = posisi
                new_cand.has_score = float(final_score)
            onto_res.save("results.owl")
            
            st.success(f"Terima kasih {nama}! Data Anda telah disimpan ke Result Ontology.")
            st.balloons()

# ==========================================
# SIDE 2: REKRUTER
# ==========================================
elif menu == "Rekruter (Admin)":
    st.title("📊 Dashboard Rekruter")
    st.subheader("Leaderboard Kandidat")

    data = []
    for c in onto_res.Candidate.instances():
        data.append({
            "Nama": c.candidate_name,
            "Posisi": c.applied_for,
            "Skor Akhir": c.has_score
        })
    
    if data:
        df = pd.DataFrame(data)
        # Sort berdasarkan skor tertinggi
        df = df.sort_values(by="Skor Akhir", ascending=False)
        
        # Leaderboard 10% terbaik
        top_n = max(1, int(len(df) * 0.1))
        df_top = df.head(top_n)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write("Semua Kandidat")
            st.dataframe(df, use_container_width=True)
        with col2:
            st.success(f"Top 10% ( {top_n} Orang )")
            st.table(df_top)
            
        st.bar_chart(df.set_index("Nama")["Skor Akhir"])
    else:
        st.warning("Belum ada pendaftar di Result Ontology.")