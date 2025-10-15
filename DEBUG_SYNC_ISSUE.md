# 🔍 Debug: Empty Location Parameter Issue

## ❌ **Current Error:**

```
Yelp API error: '400 Bad Request' for url 
'...?location=&categories=...'
               ↑
          Empty location!
```

---

## 🔍 **Debug Logging Added:**

Now when you sync, console will show:

```
✅ ZIP codes determined: ['48374', '48375', '48377'] (count: 3)
🚀 Triggering background sync with 3 ZIP codes: ['48374', '48375', '48377']
🔍 Background sync starting with ZIP codes: ['48374', '48375', '48377'], sources: [...]
📞 Calling sync_all_sources with 3 ZIP codes: ['48374', '48375']...
```

**This will show us WHERE the ZIP codes are getting lost!**

---

## 🎯 **How to Test:**

**Send a valid request from browser/Postman:**

```http
POST http://localhost:8000/api/v1/ai-orchestration/multi-source/sync
Content-Type: application/json

{
  "city": "Novi",
  "state": "MI",
  "sources": ["yelp"]
}
```

---

## 📊 **Expected Console Output:**

**Good (Working):**
```
✅ ZIP codes determined: ['48374', '48375', '48377'] (count: 3)
🚀 Triggering background sync with 3 ZIP codes: ['48374', '48375', '48377']
🔍 Background sync starting with ZIP codes: ['48374', '48375', '48377']
📞 Calling sync_all_sources with 3 ZIP codes: ['48374', '48375', '48377']
✅ Yelp API call: location=48374&categories=...
```

**Bad (What you're seeing):**
```
❌ ERROR: No ZIP codes provided to background sync! zip_codes=None
OR
❌ ERROR: No ZIP codes provided to background sync! zip_codes=[]
```

---

## 🔧 **Possible Causes:**

### **1. Request Body is Empty/Invalid**
```json
{}  ← No city or zip_codes
```

### **2. Geocoding Failing Silently**
```
City: "InvalidCity"
Geocoding: Fails
Fallback: Also fails
Result: zip_codes = None
```

### **3. Background Task Not Receiving Parameters**
```python
background_tasks.add_task(_run_multi_source_sync, zip_codes=None)
↑ Wrong parameters passed
```

---

## ✅ **Next Steps:**

1. **Check console logs** when you make a request
2. Look for the debug messages (🔍 🚀 📞)
3. See at which step ZIP codes disappear
4. That will tell us the exact issue

---

**Try syncing Novi now and check the console for the debug messages!**

