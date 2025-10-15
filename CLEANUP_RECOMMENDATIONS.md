# 🧹 Code Cleanup Recommendations

## 🗑️ **Safe to Delete (60+ files)**

---

## 1. **Test Scripts (38 files)** - Delete All ✅

These were created for debugging and testing. They served their purpose and can be removed:

```bash
# Database inspection scripts (9 files)
rm check_api_status.py
rm check_contextual_embeddings.py
rm check_db_now.py
rm check_db.py
rm check_novi.py
rm show_all_records.py
rm show_database_data.py
rm verify_traits.py
rm find_missing_traits.py

# Sync testing scripts (8 files)
rm sync_troy_dance.py
rm sync_yelp_full.py
rm test_sync_directly.py
rm test_unified_sync.py
rm test_city_to_zip_sync.py
rm test_user_friendly_sync.py
rm test_multi_source_api.py
rm debug_yelp_sync.py

# RAG testing scripts (5 files)
rm test_hybrid_rag_endpoint.py
rm test_rag_endpoints_quick.py
rm test_rag_services_direct.py
rm test_simple_rag.py
rm test_contextual_search.py

# Search fix testing (4 files)
rm test_basketball_fix.py
rm test_basketball_search.py
rm test_swim_search.py
rm test_swim_troy.py

# API testing scripts (6 files)
rm test_eventbrite_api.py
rm test_eventbrite_oauth.py
rm test_yelp_api.py
rm test_v1beta_search.py
rm test_unified_integration.py
rm test_updated_parallel_ai.py

# Debug scripts (3 files)
rm debug_parallel_ai.py
rm explore_eventbrite_endpoints.py
rm fix_console_errors.py

# Setup scripts (1 file)
rm create_unified_tables.py

# Build scripts (1 file - keep the other)
rm build_vector_index.py  # Duplicate of build_embeddings_simple.py
```

**Total:** 38 test/debug scripts can be deleted

---

## 2. **Unused Services (6 files)** - Consider Removing ⚠️

These services are imported by `sync.py` but `sync.py` itself might be deprecated:

```bash
# Check if these are used:
app/services/nlp_parser.py        # Not imported anywhere
app/services/simple_nlp.py         # Only used by old sync
app/services/llm_parser.py         # Only used by old sync
app/services/ai_agent.py           # Only used by old sync
app/services/parallel_ai_client.py # Only used by old sync
app/services/simple_ai.py          # Only used by old sync
app/services/eventbrite_oauth_client.py  # Not used
```

**Recommendation:** Delete if old `sync.py` is not being used

---

## 3. **Old Documentation (12 files)** - Archive or Delete 📚

Historical or superseded documentation:

```bash
# Historical summaries
rm CHROMADB_SUCCESS_SUMMARY.md
rm DEPRECATION_FIX_SUMMARY.md
rm SYNC_STATUS_SUMMARY.md
rm SEMANTIC_THRESHOLD_UPDATE.md

# Outdated guides
rm CHROMADB_RAG_SETUP.md         # Covered in newer docs
rm SIMPLE_RAG_WITHOUT_VECTORS.md # Outdated approach
rm EVENTBRITE_ALTERNATIVES.md    # Not needed
rm FRONTEND_UPDATES.md           # Historical
rm LLM_SETUP.md                  # Covered in main docs
rm YELP_FREE_TIER_INFO.md        # Covered in API_KEYS_SETUP.md

# Redundant guides
rm DATA_AGGREGATION_FLOW.md      # Covered in other docs
rm DATABASE_SCHEMA.md            # Auto-generated from models
```

**Total:** 12 old documentation files

---

## 4. **Unused Endpoint Files** - Already Deleted ✅

```
✅ app/api/v1/endpoints/events.py - DELETED
✅ app/api/v1/endpoints/sync.py - DELETED
✅ app/api/v1/endpoints/nlp.py - Never existed (removed from imports)
```

---

## 5. **Empty Directories** - Delete ✅

```bash
rm -r app/mcp/handlers/  # Empty directory
```

---

## 📊 **Cleanup Impact:**

### **Before Cleanup:**
```
Root directory: 90+ files
Test scripts: 38 files
Services: 17 files
Docs: 45+ files
Total: 150+ files
```

### **After Cleanup:**
```
Root directory: ~30 files (production)
Test scripts: 1 file (hallucination test)
Services: 11 files (active only)
Docs: ~15 files (current/useful)
Total: ~60 files
Reduction: 60% fewer files! ✅
```

---

## 🎯 **Cleanup Commands:**

### **Quick Cleanup (38 test files):**
```bash
cd C:\code\ActivityGuide

# Delete all test_* files except hallucination test
Get-ChildItem -Filter "test_*.py" | Where-Object {$_.Name -ne "test_ai_hallucination_fix.py"} | Remove-Item

# Delete all check_* files
Get-ChildItem -Filter "check_*.py" | Remove-Item

# Delete all debug_* files
Get-ChildItem -Filter "debug_*.py" | Remove-Item

# Delete other temp scripts
Remove-Item sync_troy_dance.py, sync_yelp_full.py, show_*.py, verify_traits.py, find_missing_traits.py, fix_console_errors.py, create_unified_tables.py, explore_*.py, build_vector_index.py
```

### **Medium Cleanup (+old docs):**
```bash
# Also remove old documentation
Remove-Item CHROMADB_SUCCESS_SUMMARY.md, DEPRECATION_FIX_SUMMARY.md, SYNC_STATUS_SUMMARY.md, SEMANTIC_THRESHOLD_UPDATE.md, CHROMADB_RAG_SETUP.md, SIMPLE_RAG_WITHOUT_VECTORS.md, EVENTBRITE_ALTERNATIVES.md, FRONTEND_UPDATES.md, LLM_SETUP.md, YELP_FREE_TIER_INFO.md, DATA_AGGREGATION_FLOW.md, DATABASE_SCHEMA.md
```

### **Deep Cleanup (+unused services):**
```bash
# Also remove unused services (if sync.py not used)
Remove-Item app/services/nlp_parser.py, app/services/simple_nlp.py, app/services/llm_parser.py, app/services/ai_agent.py, app/services/parallel_ai_client.py, app/services/simple_ai.py, app/services/eventbrite_oauth_client.py

# Remove empty directory
Remove-Item -Recurse app/mcp/handlers/
```

---

## ⚠️ **Before Deleting:**

1. **Commit current changes first:**
   ```bash
   git add -A
   git commit -m "Before cleanup - saving current state"
   ```

2. **Create a cleanup branch:**
   ```bash
   git checkout -b cleanup-unused-code
   ```

3. **Run cleanup commands**

4. **Test everything still works:**
   ```bash
   python test_ai_hallucination_fix.py
   curl http://localhost:8000/health
   ```

5. **If works, merge:**
   ```bash
   git checkout development
   git merge cleanup-unused-code
   ```

6. **If breaks, easy rollback:**
   ```bash
   git checkout development
   git branch -D cleanup-unused-code
   ```

---

## 📋 **Summary:**

**Unused Code Found:**
- 🗑️ 38 test/debug scripts
- 🗑️ 12 old documentation files
- 🗑️ 6-7 unused service files
- 🗑️ 1 empty directory
- **Total:** ~60 files can be removed (60% reduction!)

**Cleanup Benefits:**
- ✅ Cleaner project structure
- ✅ Easier to navigate
- ✅ Faster Git operations
- ✅ Less confusion about which files are active
- ✅ Smaller repository size

**Risk:** Low (all test/temp files, can restore from Git if needed)

---

**Ready to clean up? I can run the cleanup commands for you!**

