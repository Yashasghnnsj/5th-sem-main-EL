# 📊 Gemini API Usage - Complete Task & Service List

## 🎯 Overview
Your project uses **Gemini API** in **3 main endpoints** that consume API quota.

---

## 🔴 **ACTIVE ENDPOINTS USING GEMINI API**

### **1️⃣ Disease Detection** (Image Analysis)
**Endpoint**: `POST /api/analyze-image`
**Model**: `gemini-3-pro-preview` (Vision)
**Capability**: Vision - Analyzes crop images
**Use Case**: Farmer uploads crop photo → AI identifies disease

**What it does**:
- Takes image file from farmer
- Sends to Gemini Vision API
- Returns disease name, symptoms, treatment options, economic impact
- **Quota Impact**: HIGH (each image = API call + tokens for response)

**Response Fields**:
- `disease_name` - Common name (e.g., "Leaf Blast")
- `scientific_name` - Latin name (e.g., "Magnaporthe grisea")
- `confidence_score` - 0-100%
- `symptoms` - List of disease symptoms
- `biological_triggers` - Cause explanation
- `remedial_organic` - Organic treatments
- `remedial_chemical` - Chemical treatments
- `economic_impact_inr` - Loss estimate in ₹/acre

**Quota Cost**: HIGH ⚠️
- Each request uses ~500-1000+ input tokens (image processing)
- High daily limit usage

---

### **2️⃣ Market Analysis** (Text + Search)
**Endpoint**: `POST /api/market-data`
**Model**: `gemini-3-pro-preview` (Text + Search Grounding)
**Capability**: Text generation + Web search
**Use Case**: Real-time agricultural market analysis & price predictions

**What it does**:
- Takes crop name and region
- Calls MSPFetcher for current prices
- **Sends prompt to Gemini** with:
  - Current MSP (Minimum Support Price)
  - Price trend analysis
  - Market sentiment
- Receives AI market analysis
- Extracts web sources if available
- **Quota Impact**: MEDIUM (text generation only)

**Parameters**:
```
crop: "Paddy" (default)
region: "Karnataka" (default)
```

**Response**:
- `analysis` - AI-generated market commentary
- `sources` - Web references (news, data)
- `msp_data` - Live pricing
- `kpis` - Market indicators
- `price_history` - 180-day price trend
- `timestamp` - When data was fetched

**Quota Cost**: MEDIUM ⚠️
- Each request uses ~200-500 input tokens (prompt)
- Daily calls add up

---

### **3️⃣ Chat / Vani AI** (Conversational)
**Endpoint**: `POST /api/chat`
**Model**: `gemini-3-pro-preview` (Text)
**Capability**: Multi-turn conversational AI
**Use Case**: Farmer asks questions → Vani AI agricultural advisor responds

**What it does**:
- Accepts chat messages from farmer
- Maintains conversation history
- Sends to Gemini with system prompt (Vani AI persona)
- Returns agricultural advice
- **Quota Impact**: MEDIUM-HIGH (every message = API call)

**System Prompt**:
```
You are Vani AI, a wise, patient, and scientifically accurate 
agricultural advisor from the University of Agricultural Sciences, Dharwad.
```

**Conversation Flow**:
1. Farmer asks: "How to prevent leaf blast?"
2. Message sent to Gemini with history
3. Vani AI responds with expert advice
4. Response stored in chat history
5. Next message includes full context

**Quota Cost**: MEDIUM ⚠️
- Each message uses tokens for:
  - New message text
  - Full chat history
  - System prompt
- Cumulative with conversation length

---

## 📋 Other Files Using Gemini (Testing/Utility)

### Testing Files (May have been used)
- `backend/test_gemini.py` - Test Vision/Text models
- `backend/test_old_sdk.py` - SDK compatibility tests
- `backend/verify_flash.py` - Model verification
- `backend/verify_models.py` - List available models
- `backend/list_models.py` - Model enumeration

**These are utility/debug files** - not active in production

---

## 📊 **QUOTA BREAKDOWN**

### Daily Quota Limits (Free Tier)
| Metric | Limit | Status |
|--------|-------|--------|
| Input Tokens/Day | Limited | ❌ EXCEEDED |
| Requests/Day | Limited | ❌ EXCEEDED |
| Requests/Minute | 15 | ❌ EXCEEDED |
| Tokens/Minute | Limited | ❌ EXCEEDED |

### Usage Pattern
```
Each day, quota consumed by:
├── Image Analysis (Disease Detection) - HIGH usage
│   └── ~500-1000 tokens per image
├── Market Analysis - MEDIUM usage
│   └── ~200-500 tokens per analysis
└── Chat Messages - MEDIUM usage
    └── ~100-300 tokens per message (+ history)
```

---

## ⚠️ **YOUR QUOTA STATUS**

**Current Error**: `429 You exceeded your current quota`

**Affected Endpoints**:
- ❌ `/api/analyze-image` - Cannot use Vision model
- ❌ `/api/market-data` - Cannot use Text model
- ❌ `/api/chat` - Cannot use Text model

**Reset Options**:
1. Wait 24 hours (free tier daily reset)
2. Upgrade to paid tier (higher limits)
3. Create new API key (fresh quota)
4. Use mock responses (no quota consumption)

---

## 🔧 **WHICH SERVICES WILL BE AFFECTED**

| Service | Uses Gemini | Status | Impact |
|---------|-------------|--------|--------|
| Disease Detection | ✅ YES | ❌ DOWN | Can't analyze crop images |
| Market Hub | ✅ YES | ❌ DOWN | Can't get market analysis |
| Vani AI Chat | ✅ YES | ❌ DOWN | Can't chat with AI advisor |
| Settings | ❌ NO | ✅ WORKS | Settings fully functional |
| Crop Encyclopedia | ❌ NO | ✅ WORKS | Crop data loads fine |
| Weather Risk | ❌ NO | ✅ WORKS | Disease risk calculated |
| MSP Fetcher | ❌ NO | ✅ WORKS | Price data loads |

---

## 💡 **SERVICES STILL WORKING**

### ✅ No Gemini Required
- **Settings Backend** (7 endpoints) - 100% functional
- **Crop Encyclopedia** - Loads all crop data
- **Weather/Disease Risk Calculator** - Real-time calculations
- **MSP Price Data** - Government APMC data
- **Cultivation Advisory** - Seasonal guidance

### ❌ Gemini API Required
- **Disease Detection** - Vision AI model
- **Market Analysis** - Text generation + search
- **Vani AI Chat** - Conversational assistant

---

## 📈 **ESTIMATED API USAGE**

### Typical Daily Usage (Before Quota Hit)
```
Morning (8 AM):
- 1 market analysis call = ~300 tokens
- 5 chat messages (5 turns) = ~500 tokens total

Afternoon (12 PM):
- 3 disease detection calls = ~2000 tokens
- 10 chat messages = ~1000 tokens

Evening (6 PM):
- 2 more disease detections = ~1500 tokens
- 3 market analyses = ~900 tokens
- 5 more chat messages = ~500 tokens

TOTAL: ~6700 tokens/day (could exceed free tier)
```

---

## 🔑 **API KEY CONFIGURATION**

**Location**: `backend/.env`
**Key Name**: `GOOGLE_API_KEY`
**Status**: Currently set but quota exceeded

**Configuration Code** (app.py, line 40-46):
```python
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("CRITICAL: GOOGLE_API_KEY is missing from .env")
else:
    genai.configure(api_key=API_KEY)
```

---

## 🚀 **RECOMMENDATION**

### **Short Term** (Next hour)
✅ Implement mock responses for Disease Detection
- Lets you test UI without API calls
- No quota consumption
- Returns realistic test data

### **Medium Term** (This week)
✅ Optimize API calls
- Cache results where possible
- Batch requests
- Use rate limiting on frontend

### **Long Term** (Upgrade)
✅ Switch to paid tier OR
✅ Use new API key OR
✅ Wait 24h for free tier reset

---

## 📞 **SUMMARY TABLE**

| Task/Service | Endpoint | Model | Cost | Status |
|--------------|----------|-------|------|--------|
| Disease Detection | /api/analyze-image | Vision | HIGH | ❌ DOWN |
| Market Analysis | /api/market-data | Text+Search | MEDIUM | ❌ DOWN |
| Vani AI Chat | /api/chat | Text | MEDIUM | ❌ DOWN |
| Settings Mgmt | /api/settings/* | None | FREE | ✅ UP |
| Crop Data | /api/crops | None | FREE | ✅ UP |
| Weather Risk | /api/crops | Cached | FREE | ✅ UP |

---

**Need Help?**
- To use mock responses: Say "implement mock disease detection"
- To check API status: Check Google AI Studio
- To upgrade: Visit ai.google.dev and add payment method

All info provided above so you understand exactly what's using your Gemini quota!
