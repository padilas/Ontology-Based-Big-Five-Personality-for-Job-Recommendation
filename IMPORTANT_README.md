# IMPORTANT: File Structure & Safety

## 🔒 PROTECTED FILES (NEVER MODIFY DIRECTLY)
- `jobs_clean.ttl` - **MASTER FILE** - Original ontology structure
- `jobs_clean copy.ttl` - **BACKUP** - Restore source

## 📝 WORKING FILES (Modified by app)
- `jobs_with_scores.owl` - Active working file (OWL format)
- `jobs_with_scores.ttl` - Viewing file (Turtle format, sync dari .owl)

## 🔄 How It Works

```
jobs_clean.ttl (MASTER - NEVER TOUCH)
       ↓ (first time only)
jobs_with_scores.owl (WORKING)
       ↓ (auto sync)
jobs_with_scores.ttl (VIEWING)
```

### First Run
1. App checks if `jobs_with_scores.owl` exists
2. If NOT exists → Convert `jobs_clean.ttl` → `jobs_with_scores.owl`
3. Load and work with `jobs_with_scores.owl`

### Every Save
1. Save to `jobs_with_scores.owl` (OWL/XML format)
2. Auto-sync to `jobs_with_scores.ttl` (Turtle format for easy viewing)
3. `jobs_clean.ttl` stays UNTOUCHED

## 🚨 If jobs_clean.ttl Gets Deleted/Corrupted

### Restore Command:
```powershell
Copy-Item "jobs_clean copy.ttl" -Destination "jobs_clean.ttl" -Force
```

Or manually:
1. Copy `jobs_clean copy.ttl`
2. Paste and rename to `jobs_clean.ttl`

## 📊 Score Components Saved

When adding applicant, these scores are calculated and saved:
- `hasAgreeablenessScore` (Big Five)
- `hasConscientiousnessScore` (Big Five)
- `hasExtraversionScore` (Big Five)
- `hasNeuroticismScore` (Big Five)
- `hasOpennessScore` (Big Five)
- `hasCategoryFitScore` (20% weight)
- `hasSkillMatchScore` (35% weight)
- `hasExperienceScore` (20% weight)
- `hasWeightedScore` (Total 100%)

## 🎯 File Usage

| File | Purpose | Modified By | Format |
|------|---------|-------------|--------|
| jobs_clean.ttl | Master template | Manual only | Turtle |
| jobs_clean copy.ttl | Backup | Manual only | Turtle |
| jobs_with_scores.owl | Active data | App (auto) | OWL/XML |
| jobs_with_scores.ttl | View results | App (sync) | Turtle |
| jobs.owl | Legacy/fallback | - | OWL/XML |

## ⚠️ Why This Structure?

1. **Owlready2 issue**: Saving to Turtle format can corrupt files
2. **Safety**: Keep master file separate from working files  
3. **Compatibility**: OWL format is most reliable for owlready2
4. **Viewing**: TTL format is easier to read for humans

## 🔧 If You Need to Reset Everything

```powershell
# Restore master
Copy-Item "jobs_clean copy.ttl" -Destination "jobs_clean.ttl" -Force

# Delete working files (they'll be regenerated)
Remove-Item "jobs_with_scores.owl" -Force
Remove-Item "jobs_with_scores.ttl" -Force
```

Next run will start fresh from `jobs_clean.ttl`
