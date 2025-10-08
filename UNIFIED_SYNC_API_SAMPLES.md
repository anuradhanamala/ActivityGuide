# 🔄 Unified Sync API Request Samples

Complete collection of API request examples for the unified sync endpoint.

## 📍 **Endpoint**

```
POST /api/v1/unified/sync/trigger
```

---

## 🧪 **Sample Requests**

### **1. Simplest Request (No Parameters)**

#### **cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger"
```

#### **PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger" -Method POST
```

#### **Python (requests):**
```python
import requests

response = requests.post("http://localhost:8000/api/v1/unified/sync/trigger")
print(response.json())
```

#### **Python (httpx - async):**
```python
import httpx
import asyncio

async def sync():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/v1/unified/sync/trigger")
        return response.json()

result = asyncio.run(sync())
print(result)
```

#### **Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48104", "48105", "48108"],
  "sources": "all"
}
```

---

### **2. Sync Specific ZIP Codes**

#### **cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48085"
```

#### **PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48085" -Method POST
```

#### **Python (requests):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/unified/sync/trigger",
    params={
        "zip_codes": ["48083", "48084", "48085"]
    }
)
print(response.json())
```

#### **JavaScript (fetch):**
```javascript
const response = await fetch(
  'http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084',
  { method: 'POST' }
);
const data = await response.json();
console.log(data);
```

#### **Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084", "48085"],
  "sources": "all"
}
```

---

### **3. Sync Specific Sources Only**

#### **cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?sources=yelp&sources=eventbrite"
```

#### **PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?sources=yelp&sources=eventbrite" -Method POST
```

#### **Python (requests):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/unified/sync/trigger",
    params={
        "sources": ["yelp", "eventbrite"]
    }
)
print(response.json())
```

#### **Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48104", "48105", "48108"],
  "sources": ["yelp", "eventbrite"]
}
```

---

### **4. Sync Specific ZIP Codes AND Sources**

#### **cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&sources=yelp"
```

#### **PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&sources=yelp" -Method POST
```

#### **Python (requests):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/unified/sync/trigger",
    params={
        "zip_codes": ["48083"],
        "sources": ["yelp"]
    }
)
print(response.json())
```

#### **Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083"],
  "sources": ["yelp"]
}
```

---

### **5. Multiple ZIP Codes and Multiple Sources**

#### **cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48104&zip_codes=48105&sources=yelp&sources=eventbrite&sources=google_places"
```

#### **PowerShell:**
```powershell
$uri = "http://localhost:8000/api/v1/unified/sync/trigger?" +
       "zip_codes=48083&zip_codes=48084&zip_codes=48104&" +
       "sources=yelp&sources=eventbrite&sources=google_places"

Invoke-WebRequest -Uri $uri -Method POST
```

#### **Python (requests):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/unified/sync/trigger",
    params={
        "zip_codes": ["48083", "48084", "48104", "48105"],
        "sources": ["yelp", "eventbrite", "google_places"]
    }
)
print(response.json())
```

#### **Response:**
```json
{
  "message": "Sync triggered successfully",
  "status": "started",
  "zip_codes": ["48083", "48084", "48104", "48105"],
  "sources": ["yelp", "eventbrite", "google_places"]
}
```

---

## 📊 **Check Sync Status**

### **Get Recent Sync Logs:**

#### **cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/unified/sync/status"
```

#### **PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/status" -Method GET | Select-Object -ExpandProperty Content
```

#### **Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/v1/unified/sync/status")
print(response.json())
```

#### **Response:**
```json
{
  "recent_syncs": [
    {
      "source": "all",
      "sync_type": "full",
      "status": "success",
      "events_processed": 150,
      "events_created": 75,
      "events_updated": 75,
      "started_at": "2025-10-07T19:00:00",
      "completed_at": "2025-10-07T19:05:00",
      "duration_seconds": 300,
      "errors": []
    }
  ],
  "last_sync": { /* ... */ }
}
```

---

## 🌐 **Using Swagger UI (Browser)**

### **Step 1:** Open browser to:
```
http://localhost:8000/docs
```

### **Step 2:** Find the endpoint:
```
POST /api/v1/unified/sync/trigger
```

### **Step 3:** Click "Try it out"

### **Step 4:** Enter parameters:
```
zip_codes: 48083
sources: yelp
```

### **Step 5:** Click "Execute"

---

## 📦 **Using Postman**

### **Request Setup:**
```
Method: POST
URL: http://localhost:8000/api/v1/unified/sync/trigger

Params:
  Key: zip_codes | Value: 48083
  Key: zip_codes | Value: 48084
  Key: sources   | Value: yelp
  Key: sources   | Value: eventbrite

Headers:
  Content-Type: application/json
```

---

## 🔄 **Real-World Examples**

### **Example 1: Sync Troy, MI**
```powershell
# Sync all Yelp data for Troy area
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48084&zip_codes=48085" -Method POST
```

### **Example 2: Sync Ann Arbor**
```powershell
# Sync all sources for Ann Arbor
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48104&zip_codes=48105" -Method POST
```

### **Example 3: Quick Yelp Sync**
```powershell
# Just sync Yelp for one ZIP code
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&sources=yelp" -Method POST
```

### **Example 4: Full Michigan Sync**
```powershell
# Sync multiple cities
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083&zip_codes=48104&zip_codes=48009&zip_codes=48326" -Method POST
```

---

## 📊 **Available Source Values**

Use these values for the `sources` parameter:

```
eventbrite
yelp
google_places
ticketmaster
meetup
recreation_gov
ymca
boys_girls_club
openstreetmap
```

---

## 🎯 **Quick Reference Card**

```
┌─────────────────────────────────────────────────────────────┐
│  UNIFIED SYNC API - QUICK REFERENCE                        │
├─────────────────────────────────────────────────────────────┤
│  Endpoint: POST /api/v1/unified/sync/trigger               │
│                                                             │
│  Parameters (all optional):                                │
│    • zip_codes: ["48083", "48084"]                        │
│    • sources: ["yelp", "eventbrite"]                      │
│                                                             │
│  Simplest Call:                                            │
│    POST /api/v1/unified/sync/trigger                      │
│                                                             │
│  Response:                                                 │
│    {                                                        │
│      "message": "Sync triggered successfully",            │
│      "status": "started",                                  │
│      "zip_codes": [...],                                  │
│      "sources": [...]                                     │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ **One-Liner for PowerShell:**

```powershell
# Copy and paste this entire line:
cd C:\code\ActivityGuide; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000
```

---

## 🎯 **Summary**

**To run the app:**
1. Navigate to project: `cd C:\code\ActivityGuide`
2. Activate venv: `.\venv\Scripts\Activate.ps1`
3. Start backend: `uvicorn app.main:app --reload --port 8000`

**To test sync:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/unified/sync/trigger?zip_codes=48083" -Method POST
```

That's it! 🚀
