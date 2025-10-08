# 🍽️ How to Create Yelp API Key

Complete step-by-step guide to get your Yelp Fusion API key for ActivityGuide.

## 📋 **Step-by-Step Instructions**

### **Step 1: Go to Yelp Fusion**
Open your browser and go to:
```
https://www.yelp.com/developers/v3/manage_app
```

Or start here:
```
https://fusion.yelp.com/
```

### **Step 2: Create a Yelp Account** (if you don't have one)
- Click "Sign Up" or "Log In"
- Use your email or Google/Facebook account
- Verify your email address

### **Step 3: Create a New App**
1. Once logged in, go to: https://www.yelp.com/developers/v3/manage_app
2. Click **"Create New App"** button
3. Fill out the form:

```
App Name: ActivityGuide
Industry: Education & Social Services
Company: Your Company Name (or "Personal Project")
Contact Email: your_email@example.com

Description:
"ActivityGuide is a family activity discovery platform that helps parents find 
kid-friendly activities, classes, and venues in their area. We use the Yelp API 
to discover family-friendly businesses, museums, playgrounds, and activity centers."

What Yelp APIs will you use?
☑ Fusion (Business Search, Reviews)

Will you display Yelp reviews?
☐ Yes  ☑ No (optional)

By checking this box, I agree to Yelp's Terms of Use and Display Requirements
☑ I agree
```

4. Click **"Create New App"** button

### **Step 4: Get Your API Key**
After creating the app, you'll see:
- **App Name:** ActivityGuide
- **Client ID:** (a long string)
- **API Key:** (a long string starting with letters/numbers)

**Copy the API Key** - it looks like:
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
(~140 characters long)
```

### **Step 5: Add to Your `.env` File**
Open your `.env` file and update the Yelp API key:

```bash
# Open .env in notepad
notepad .env
```

Find the line:
```env
YELP_API_KEY=your_yelp_api_key
```

Replace with your actual key:
```env
YELP_API_KEY=your_actual_api_key_here_140_characters_long
```

Save and close the file.

---

## ⚡ **Quick Command (Windows)**

Run this command in your terminal:
```powershell
# This will open the Yelp developer page
Start-Process "https://www.yelp.com/developers/v3/manage_app"
```

---

## 🔑 **API Key Details**

### **What You Get (Free Tier):**
- ✅ **500 API calls per day**
- ✅ **25,000 API calls per month**
- ✅ No credit card required
- ✅ Access to all Fusion API endpoints

### **Rate Limits:**
- 5 requests per second
- Resets daily at midnight UTC

### **Available Endpoints:**
```
✅ Business Search
✅ Business Details
✅ Business Reviews
✅ Phone Search
✅ Business Match
✅ Autocomplete
```

---

## 🧪 **Test Your Yelp API Key**

After adding the key to `.env`, run this test:

```bash
python test_yelp_api.py
```

Or use this quick test:

```powershell
python -c "
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.api_clients import YelpClient

async def test():
    client = YelpClient()
    if not client.api_key:
        print('[ERROR] Yelp API key not found in .env')
        return
    
    print(f'Testing Yelp API...')
    print(f'API Key: {client.api_key[:20]}...')
    
    results = await client.search_businesses(
        location='Ann Arbor, MI',
        categories=['museums', 'playgrounds', 'kids_activities']
    )
    
    print(f'Found {len(results)} businesses')
    for i, biz in enumerate(results[:5], 1):
        print(f'{i}. {biz.get(\"title\", \"No name\")}')

asyncio.run(test())
"
```

---

## 📊 **What Yelp API Gives You**

### **For ActivityGuide:**
```
✅ Kids activity centers
✅ Museums
✅ Playgrounds  
✅ Trampoline parks
✅ Gyms & sports centers
✅ Dance studios
✅ Martial arts schools
✅ Music schools
✅ Art studios
✅ Swimming pools
✅ Bowling alleys
✅ Movie theaters
✅ Libraries
✅ Restaurants (kid-friendly)
```

### **Data You Get:**
- Business name
- Address & location
- Phone number
- Rating & review count
- Price level ($ to $$$$)
- Photos
- Hours of operation
- Categories/tags

---

## 🔧 **Troubleshooting**

### **Issue: "403 Forbidden"**
**Solution:** API key is invalid or not activated yet
- Wait 5 minutes after creating the app
- Make sure you copied the entire key
- Check for extra spaces in `.env` file

### **Issue: "429 Too Many Requests"**
**Solution:** You hit the rate limit
- Free tier: 500 calls/day, 25,000/month
- Wait until next day or upgrade

### **Issue: "401 Unauthorized"**
**Solution:** API key format is wrong
- Make sure it's in the format: `Bearer YOUR_KEY`
- Check your code uses: `Authorization: Bearer {api_key}`

---

## 💡 **Best Practices**

### **1. Cache Results**
```python
# Don't call API repeatedly for same location
# Use Redis or database caching
```

### **2. Batch Requests**
```python
# Search multiple categories in one call
categories = "museums,playgrounds,kids_activities,trampoline"
```

### **3. Use Location Efficiently**
```python
# Use latitude/longitude instead of address when possible
# More accurate and faster
```

### **4. Filter Results**
```python
# Add filters to reduce API calls
params = {
    "location": "Ann Arbor, MI",
    "categories": "kids_activities",
    "radius": 40000,  # 25 miles in meters
    "limit": 50
}
```

---

## 📝 **Example API Call**

```python
import httpx

async def search_yelp_kids_activities():
    api_key = "YOUR_YELP_API_KEY"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    params = {
        "location": "Ann Arbor, MI",
        "categories": "playgrounds,museums,kids_activities,trampoline",
        "sort_by": "rating",
        "limit": 50
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.yelp.com/v3/businesses/search",
            headers=headers,
            params=params
        )
        
        data = response.json()
        businesses = data.get("businesses", [])
        
        for biz in businesses:
            print(f"Name: {biz['name']}")
            print(f"Address: {biz['location']['address1']}")
            print(f"Rating: {biz['rating']} ({biz['review_count']} reviews)")
            print(f"Category: {biz['categories'][0]['title']}")
            print()
```

---

## 🌐 **Useful Links**

- **Create App:** https://www.yelp.com/developers/v3/manage_app
- **API Documentation:** https://docs.developer.yelp.com/
- **Rate Limits:** https://docs.developer.yelp.com/docs/fusion-rate-limiting
- **Category List:** https://www.yelp.com/developers/documentation/v3/category_list
- **Support:** https://www.yelp.com/developers/support

---

## ✅ **Checklist**

- [ ] Created Yelp account
- [ ] Created app on Yelp Fusion
- [ ] Copied API key
- [ ] Added to `.env` file
- [ ] Tested API key
- [ ] Verified results

---

## 🎯 **Next Steps After Setup**

1. **Test the Yelp API:**
   ```bash
   python test_yelp_api.py
   ```

2. **Run unified sync:**
   ```bash
   python -c "
   from app.services.unified_sync_service import unified_sync_service
   from app.core.database import get_db
   import asyncio
   
   async def sync():
       db = next(get_db())
       result = await unified_sync_service.sync_all_sources(db, ['48104'])
       print(result)
   
   asyncio.run(sync())
   "
   ```

3. **Search for activities:**
   ```bash
   curl "http://localhost:8000/api/v1/unified/search?city=Ann%20Arbor&categories=family&limit=20"
   ```

---

## 💰 **Pricing**

### **Free Tier (What You Get):**
- 500 calls/day
- 25,000 calls/month
- All API features
- No credit card required

### **If You Need More:**
Contact Yelp for enterprise pricing at:
https://www.yelp.com/developers/v3/pricing

But 500/day should be plenty for most use cases! 🎉
