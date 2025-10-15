# 🎯 Centralized Categories System

## ✅ **Categories Now Managed in ONE Place!**

**File:** `app/core/categories.py`

All activity categories are now centralized and automatically mapped to each source!

---

## 🎉 **What Changed:**

### **Before (Scattered):**
```
❌ Yelp categories in: app/services/api_clients.py (line 125)
❌ Google categories in: app/services/api_clients.py (line 260)
❌ Eventbrite categories in: app/services/api_clients.py (line 42)
```

**Problem:**
- Hard to maintain (3 places to update)
- Inconsistent across sources
- Easy to miss a source when adding categories

---

### **After (Centralized):**
```
✅ ALL categories in: app/core/categories.py
✅ One source of truth
✅ Automatic mapping to each source
```

**Benefits:**
- ✅ Add once, works everywhere
- ✅ Consistent across all sources
- ✅ Easy to maintain
- ✅ Self-documenting

---

## 📋 **Current Categories (18 types):**

| Activity Type | Yelp | Google Places | Eventbrite |
|---------------|------|---------------|------------|
| Museums | `museums` | `museum` | `family` |
| Playgrounds | `playgrounds` | `park` | `family` |
| Amusement Parks | `amusementparks` | `amusement_park` | `family` |
| Gyms | `gyms` | `gym` | `sports-fitness` |
| Sports | `sportclubs` | `sports_complex` | `sports-fitness` |
| Fitness | `fitness` | `gym` | `sports-fitness` |
| Dance | `dance_schools,dancestudio` | `school` | `performing-arts` |
| Aquatic | `swimmingpools,aquariums` | `aquarium` | `sports-fitness` |
| Basketball | `basketball` | `sports_complex` | `sports-fitness` |
| Soccer | `soccer` | `sports_complex` | `sports-fitness` |
| Martial Arts | `martialarts,karate` | `gym` | `sports-fitness` |
| Music | `musiclessons,musicvenues` | `school` | `music` |
| Art | `artclasses,artmuseums` | `art_gallery` | `performing-arts` |
| Theater | `theater,performingarts` | `performing_arts_theater` | `performing-arts` |
| Science | `sciencemuseums` | `museum` | `science-tech` |
| Parks | `parks` | `park` | `family` |
| Indoor Play | `indoorplaycenter,trampoline` | `amusement_park` | `family` |
| Outdoor Activities | `active,climbing,hiking` | `park` | `sports-fitness` |

---

## 🚀 **Default Search Categories:**

When you sync without specifying categories, we search for:

**10 Default Activity Types:**
1. Museums
2. Playgrounds
3. Amusement Parks
4. Gyms
5. Sports
6. Fitness
7. Dance
8. Aquatic
9. Parks
10. Indoor Play

**Automatically translates to:**

**Yelp:** 13 categories
```
museums,playgrounds,amusementparks,gyms,sportclubs,fitness,
dance_schools,dancestudio,swimmingpools,aquariums,parks,
indoorplaycenter,trampoline
```

**Google Places:** 7 types
```
museum|park|amusement_park|gym|sports_complex|school|aquarium
```

**Eventbrite:** 3 categories
```
family,sports-fitness,performing-arts
```

---

## 🔧 **How to Add New Categories:**

### **Step 1: Add to ActivityType Enum**

**File:** `app/core/categories.py`

```python
class ActivityType(Enum):
    # ... existing ...
    BOWLING = "bowling"  # NEW
    ROCK_CLIMBING = "rock_climbing"  # NEW
```

---

### **Step 2: Add Source Mappings**

```python
YELP_CATEGORIES = {
    # ... existing ...
    ActivityType.BOWLING: "bowling",
    ActivityType.ROCK_CLIMBING: "climbing",
}

GOOGLE_PLACES_TYPES = {
    # ... existing ...
    ActivityType.BOWLING: "bowling_alley",
    ActivityType.ROCK_CLIMBING: "gym",
}

EVENTBRITE_CATEGORIES = {
    # ... existing ...
    ActivityType.BOWLING: "sports-fitness",
    ActivityType.ROCK_CLIMBING: "sports-fitness",
}
```

---

### **Step 3: Add to Defaults (Optional)**

```python
DEFAULT_ACTIVITY_TYPES = [
    # ... existing ...
    ActivityType.BOWLING,  # NEW
    ActivityType.ROCK_CLIMBING,  # NEW
]
```

---

### **Step 4: Done!**

**That's it!** All sources now automatically use the new categories:
- ✅ Yelp will search for "bowling"
- ✅ Google will search for "bowling_alley"
- ✅ Eventbrite will search for "sports-fitness"

**No need to modify 3 different places!** 🎉

---

## 💡 **Usage Examples:**

### **Example 1: Sync with Default Categories**

```bash
POST /api/v1/ai-orchestration/multi-source/sync
{
  "city": "Troy",
  "state": "MI"
}
```

**Automatically uses:**
- Yelp: 13 categories (museums, playgrounds, gyms, dance, etc.)
- Google: 7 types (museum, park, gym, etc.)
- Eventbrite: 3 categories (family, sports-fitness, performing-arts)

---

### **Example 2: Sync with Custom Categories**

```python
# In your code
from app.core.categories import ActivityType, CategoryMapper

# Get specific categories
activity_types = [
    ActivityType.BASKETBALL,
    ActivityType.SOCCER,
    ActivityType.DANCE
]

yelp_cats = CategoryMapper.get_yelp_categories(activity_types)
# Returns: "basketball,soccer,dance_schools,dancestudio"

google_types = CategoryMapper.get_google_places_types(activity_types)
# Returns: "sports_complex|school"
```

---

## 📊 **Benefits:**

### **Before Centralization:**
```
To add "Bowling":
1. Edit app/services/api_clients.py line 125 (Yelp)
2. Edit app/services/api_clients.py line 260 (Google)
3. Edit app/services/api_clients.py line 42 (Eventbrite)
Total: 3 places to update ❌
```

### **After Centralization:**
```
To add "Bowling":
1. Edit app/core/categories.py (one file, one place)
   - Add to enum
   - Add to 3 mappings (all in same file)
Total: 1 file ✅
```

---

## 🎯 **Quick Reference:**

**File:** `app/core/categories.py`

**Current Activity Types:** 18  
**Current Yelp Categories:** 13+  
**Current Google Types:** 7+  
**Current Eventbrite Categories:** 3+  

**To add new activity:**
1. Add to `ActivityType` enum
2. Add to `YELP_CATEGORIES` dict
3. Add to `GOOGLE_PLACES_TYPES` dict
4. Add to `EVENTBRITE_CATEGORIES` dict
5. Optional: Add to `DEFAULT_ACTIVITY_TYPES`

**To view current categories:**
```bash
python app/core/categories.py
```

---

## ✅ **Summary:**

**Before:** Categories scattered in 3 places  
**Now:** All categories in `app/core/categories.py`  

**Impact:**
- ✅ Single source of truth
- ✅ Easier to maintain
- ✅ Consistent across sources
- ✅ Self-documenting
- ✅ Add once, works everywhere

**Your category system is now professional and maintainable!** 🎉

