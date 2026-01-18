import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from msp_fetcher import MSPFetcher, get_msp_for_crop
from weather_disease_risk import WeatherDiseaseRiskCalculator, get_crop_disease_risks
from cultivation_advisor import CultivationAdvisor, get_cultivation_advisory
from pathlib import Path

# ---------------- Setup ----------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from datetime import datetime

# Settings storage location
SETTINGS_DIR = Path(__file__).parent / "settings"
SETTINGS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = SETTINGS_DIR / "user_settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "language": "EN",
    "crop_cluster": "All Karnataka",
    "notifications": True,
    "price_alerts": True,
    "theme": "light",
    "region": "Karnataka",
    "unit_preference": "metric",
    "crop_favorites": [],
    "last_updated": None
}

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Security: Load key from .env (Create a new key if you revoked the old one)
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("CRITICAL: GOOGLE_API_KEY is missing from .env")
else:
    genai.configure(api_key=API_KEY)

# Validated model names for this API Key
VISION_MODEL_NAME = "models/gemini-2.5-flash-lite" 
TEXT_MODEL_NAME = "models/gemini-2.5-flash-lite"
TTS_MODEL_NAME = "models/gemini-2.5-flash-preview-tts"  # Specialized for text-to-speech

# ============== Settings Management Functions ==============
def load_settings():
    """Load user settings from file, return defaults if not found"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save user settings to file"""
    try:
        # Remove timestamp before saving (will be regenerated on load)
        settings_to_save = {k: v for k, v in settings.items() if k != 'last_updated'}
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
        logger.info(f"Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return False

VANI_SYSTEM_PROMPT = """
You are Vani AI, a wise, patient, and scientifically accurate agricultural advisor from 
the University of Agricultural Sciences, Dharwad. 
Linguistic Style: Professional yet warm. Able to switch seamlessly between technical 
botanical terms and simple farmer-friendly metaphors.
Context: Provide situated advice based on Karnataka's agricultural landscape.
Always respond as Vani AI.
"""

# Images directory
IMAGES_DIR = Path(__file__).parent / "images"

# ============== Image Serving Endpoint ==============
@app.route("/api/image/<filename>", methods=["GET"])
def serve_image(filename):
    """Serve local images from the images directory"""
    try:
        return send_from_directory(IMAGES_DIR, filename)
    except Exception as e:
        return jsonify({"error": f"Image not found: {str(e)}"}), 404

# ---------------- Helper ----------------
def process_image(file):
    """Converts Flask file storage to Gemini-compatible blob"""
    return {
        "mime_type": file.mimetype,
        "data": file.read()
    }

# ---------------- Route 1: Image Scan ----------------
from local_inference_service import LocalInferenceService

# ---------------- Route 1: Image Scan (Hybrid: Local ViT + Gemini Enrichment) ----------------
@app.route("/api/analyze-image", methods=["POST"])
def analyze_image():
    print("--- Hybrid Scan Initiated: Local ViT + Gemini ---")
    
    if "image" not in request.files:
        return jsonify({"error": "Visual Uplink Failed: No Image"}), 400

    file = request.files["image"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    try:
        # 1. Save File Locally for ViT Inference
        file.save(temp_path)
        
        # 2. DETECT Disease using Local ViT Model
        detection_result = LocalInferenceService.predict(temp_path)
        detected_disease = detection_result["disease"]
        detected_crop = detection_result["crop"]
        confidence = detection_result["confidence"]
        
        print(f"Local ViT Detected: {detected_disease} on {detected_crop} ({confidence:.2f}%)")
        
        # 3. ENRICH with Gemini (Text Prompt Only - Cheaper & Faster)
        prompt = f"""
        You are an expert plant pathologist. 
        A local AI model has detected "{detected_disease}" on "{detected_crop}" with {confidence:.1f}% confidence.

        Task: Provide a detailed treatment and impact report for this specific disease.
        Return a STRICT JSON object using exactly these keys:
        {{
            "disease_name": "{detected_disease}",
            "scientific_name": "Latin Name of {detected_disease}",
            "confidence_score": {confidence},
            "symptoms": ["Common symptom 1", "Common symptom 2", "Distinctive sign"],
            "biological_triggers": "What causes this disease (fungus/bacteria/virus details)?",
            "remedial_chemical": ["Effective chemical fungicide/brand names"],
            "remedial_organic": ["Organic home remedy 1", "Bio-control agent"],
            "economic_impact_inr": "Estimated yield loss description and approx INR value per acre"
        }}
        """

        model = genai.GenerativeModel(TEXT_MODEL_NAME)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Parse and return
        print("Analysis Complete.")
        return jsonify(json.loads(response.text))

    except Exception as e:
        print(f"HYBRID SCAN FAILED: {str(e)}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500


# ---------------- Route 2: Market Data with Search Grounding ----------------
@app.route("/api/market-data", methods=["POST"])
def market_data():
    data = request.json or {}
    crop = data.get("crop", "Paddy")
    region = data.get("region", "Karnataka")
    
    # Fetch live MSP data
    msp_data = get_msp_for_crop(crop)
    if not msp_data:
        return jsonify({"error": f"MSP data not available for {crop}"}), 400
    
    # Get price history for trend visualization
    price_history = MSPFetcher.get_price_history(crop, days=180)
    
    # Calculate supply and demand indicators based on seasonal factors
    current_month = datetime.now().month
    supply_index = MSPFetcher._get_seasonal_multiplier(crop, current_month) * 100
    
    # Trend analysis
    if len(price_history) >= 2:
        latest_price = price_history[-1]["price"]
        previous_price = price_history[-5]["price"] if len(price_history) > 5 else price_history[0]["price"]
        trend_change = ((latest_price - previous_price) / previous_price) * 100
        
        if trend_change > 2:
            trend = "Bullish"
        elif trend_change < -2:
            trend = "Bearish"
        else:
            trend = "Stable"
    else:
        trend = "Stable"
        trend_change = 0
    
    # Forecast (simple extrapolation)
    forecast_percent = trend_change * 2.5  # Amplify trend for forecast
    
    prompt = f"""
    You are an agricultural market analyst. Provide a brief market analysis for {crop} in {region}.
    Focus on Karnataka APMC mandis (Hubli, Davanagere, Belagavi, Bangalore).
    
    Current MSP: {msp_data['msp']}
    Current trend: {trend} ({trend_change:+.1f}% change)
    
    Provide a concise 3-4 sentence analysis covering:
    1. Current market sentiment
    2. Key factors affecting prices
    3. Short-term outlook based on current data
    
    Be specific and actionable. Reference the live data provided.
    """

    try:
        # Use gemini-pro without search tools - provide market analysis from known data
        model = genai.GenerativeModel(TEXT_MODEL_NAME)
        response = model.generate_content(prompt)
        
        # Extract response text
        result_text = response.text if hasattr(response, 'text') else f"Market analysis for {crop}: Current MSP is {msp_data['msp']} with {trend} trend. Monitor weather patterns and supply conditions for price impacts."
        
        # Extract grounding sources if available
        sources = []
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                metadata = candidate.grounding_metadata
                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web'):
                            sources.append({
                                "title": chunk.web.title if hasattr(chunk.web, 'title') else "Source",
                                "uri": chunk.web.uri if hasattr(chunk.web, 'uri') else ""
                            })
        
        return jsonify({
            "analysis": result_text,
            "sources": sources,
            "crop": crop,
            "region": region,
            "msp_data": msp_data,
            "kpis": {
                "msp": msp_data["msp"],
                "supply_index": round(min(100, supply_index), 1),
                "trend": trend,
                "trend_percent": f"{trend_change:+.1f}%",
                "forecast_percent": f"{forecast_percent:+.1f}%"
            },
            "price_history": price_history,
            "timestamp": datetime.now().isoformat(),
            "live_updated": True
        })

    except Exception as e:
        logger.error(f"Error in market_data: {str(e)}", exc_info=True)
        # Return fallback with cached MSP data
        return jsonify({
            "analysis": f"Market analysis for {crop}: Current MSP is {msp_data['msp']}. Monitor market conditions and weather patterns for supply impacts.",
            "sources": [],
            "crop": crop,
            "region": region,
            "msp_data": msp_data,
            "kpis": {
                "msp": msp_data["msp"],
                "supply_index": 85,
                "trend": "Stable",
                "trend_percent": "0%",
                "forecast_percent": "0%"
            },
            "price_history": price_history if price_history else [],
            "timestamp": datetime.now().isoformat(),
            "note": "Using cached MSP data due to API error"
        }), 200


# ---------------- Route 3: Chat ----------------
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    history_raw = data.get("history", [])
    message = data.get("message", "")

    # Convert frontend history to Gemini format
    chat_history = []
    # Add System Context as the first turn if history is empty
    if not history_raw:
        chat_history.append({"role": "user", "parts": [VANI_SYSTEM_PROMPT]})
        chat_history.append({"role": "model", "parts": ["I am Vani AI, your agricultural advisor. How can I help you today?"]})
    
    for h in history_raw:
        role = "user" if h.get("role") == "user" else "model"
        chat_history.append({"role": role, "parts": [h.get("content", "")]})

    try:
        model = genai.GenerativeModel(TEXT_MODEL_NAME)
        chat_session = model.start_chat(history=chat_history)
        response = chat_session.send_message(message)
        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============== Text-to-Speech Endpoint ==============
@app.route("/api/text-to-speech", methods=["POST"])
def text_to_speech():
    """Convert text to speech - returns success to trigger browser TTS"""
    data = request.json or {}
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Simple endpoint that validates text and returns success
        # Frontend will handle the actual audio playback using Web Speech API
        logger.info(f"TTS request for text: {text[:50]}...")
        
        return jsonify({
            "success": True,
            "text": text,
            "message": "Ready to play audio"
        })
        
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------- Route 4: Crop Knowledge Database with Real-Time Intelligence ----------------
@app.route("/api/crops", methods=["GET"])
def get_crops():
    """Returns the complete crop registry for Karnataka with REAL-TIME data"""
    
    # Get current weather and season
    weather = WeatherDiseaseRiskCalculator.get_simulated_weather()
    current_month = datetime.now().month
    is_monsoon = current_month in [6, 7, 8, 9]
    is_summer = current_month in [3, 4, 5]
    
    # Base crop data with dynamic enrichment
    crops = [
        {
            "id": 1,
            "name": "Paddy",
            "scientific": "Oryza sativa",
            "variety": "Hybrid-4",
            "region": "Cauvery Basin",
            "cycle": "120 Days",
            "water": "High",
            "yield": "25q/acre",
            "image": "http://localhost:5000/api/image/paddy.png",
            "suitability": {
                "temperature": "25-35°C",
                "pH": "5.5-6.5",
                "elevation": "<1000m",
                "rainfall": "1000-1500mm"
            }
        },
        {
            "id": 2,
            "name": "Ragi",
            "scientific": "Eleusine coracana",
            "variety": "GPU-28",
            "region": "Dry Zone",
            "cycle": "110 Days",
            "water": "Low",
            "yield": "15q/acre",
            "image": "http://localhost:5000/api/image/ragi.png",
            "suitability": {
                "temperature": "20-30°C",
                "pH": "4.5-8.0",
                "elevation": "500-2000m",
                "rainfall": "500-1000mm"
            }
        },
        {
            "id": 3,
            "name": "Coffee",
            "scientific": "Coffea arabica",
            "variety": "Sln.795",
            "region": "Malnad Highlands",
            "cycle": "Perennial",
            "water": "Moderate",
            "yield": "800kg/acre",
            "image": "http://localhost:5000/api/image/coffee.png",
            "suitability": {
                "temperature": "15-24°C",
                "pH": "6.0-6.5",
                "elevation": "1000-1500m",
                "rainfall": "1500-2500mm"
            }
        },
        {
            "id": 4,
            "name": "Sugarcane",
            "scientific": "Saccharum officinarum",
            "variety": "Co-86032",
            "region": "Mandya Belt",
            "cycle": "12 Months",
            "water": "Very High",
            "yield": "40t/acre",
            "image": "http://localhost:5000/api/image/sugarcane.png",
            "suitability": {
                "temperature": "20-35°C",
                "pH": "6.5-7.5",
                "elevation": "<1000m",
                "rainfall": "1500-2500mm"
            }
        },
        {
            "id": 5,
            "name": "Tomato",
            "scientific": "Solanum lycopersicum",
            "variety": "Arka Rakshak",
            "region": "Kolar",
            "cycle": "135 Days",
            "water": "Moderate",
            "yield": "25-30t/acre",
            "image": "http://localhost:5000/api/image/tomato.png",
            "suitability": {
                "temperature": "20-25°C",
                "pH": "6.0-7.0",
                "elevation": "500-1500m",
                "rainfall": "600-1500mm"
            }
        },
        {
            "id": 6,
            "name": "Potato",
            "scientific": "Solanum tuberosum",
            "variety": "Kufri Jyoti",
            "region": "Hassan",
            "cycle": "90 Days",
            "water": "Moderate",
            "yield": "20t/acre",
            "image": "http://localhost:5000/api/image/potato.png",
            "suitability": {
                "temperature": "15-25°C",
                "pH": "5.0-6.5",
                "elevation": "800-2500m",
                "rainfall": "Low during maturity"
            }
        },
        {
            "id": 7,
            "name": "Maize",
            "scientific": "Zea mays",
            "variety": "Ganga Kaveri",
            "region": "Davangere",
            "cycle": "110 Days",
            "water": "Moderate",
            "yield": "30q/acre",
            "image": "http://localhost:5000/api/image/maize.png",
            "suitability": {
                "temperature": "21-30°C",
                "pH": "5.5-7.0",
                "elevation": "Up to 3000m",
                "rainfall": "500-750mm"
            }
        },
        {
            "id": 8,
            "name": "Capsicum",
            "scientific": "Capsicum annuum",
            "variety": "Indra",
            "region": "Chikballapur",
            "cycle": "150 Days",
            "water": "High",
            "yield": "40t/acre",
            "image": "http://localhost:5000/api/image/capsicum.png",
            "suitability": {
                "temperature": "18-25°C",
                "pH": "6.0-6.5",
                "elevation": "800-1500m",
                "rainfall": "Moderate"
            }
        },
        {
            "id": 9,
            "name": "Soybean",
            "scientific": "Glycine max",
            "variety": "JS 335",
            "region": "Bidar",
            "cycle": "100 Days",
            "water": "Moderate",
            "yield": "12q/acre",
            "image": "http://localhost:5000/api/image/soyabean.png",
            "suitability": {
                "temperature": "25-30°C",
                "pH": "6.0-7.0",
                "elevation": "Up to 2000m",
                "rainfall": "600-800mm"
            }
        },
        {
            "id": 10,
            "name": "Grape",
            "scientific": "Vitis vinifera",
            "variety": "Thompson Seedless",
            "region": "Vijayapura",
            "cycle": "Perennial",
            "water": "Moderate",
            "yield": "15t/acre",
            "image": "http://localhost:5000/api/image/grape.png",
            "suitability": {
                "temperature": "15-40°C",
                "pH": "6.5-8.0",
                "elevation": "300-900m",
                "rainfall": "Low humidity preferred"
            }
        },
        {
            "id": 11,
            "name": "Orange",
            "scientific": "Citrus reticulata",
            "variety": "Coorg Mandarin",
            "region": "Kodagu",
            "cycle": "Perennial",
            "water": "Moderate",
            "yield": "500 fruits/tree",
            "image": "http://localhost:5000/api/image/orange.png",
            "suitability": {
                "temperature": "10-35°C",
                "pH": "5.5-6.5",
                "elevation": "600-1200m",
                "rainfall": "1200-2500mm"
            }
        },
        {
            "id": 12,
            "name": "Apple",
            "scientific": "Malus domestica",
            "variety": "Royal Delicious",
            "region": "Himalayan Region",
            "cycle": "Perennial",
            "water": "Moderate",
            "yield": "10-15t/acre",
            "image": "http://localhost:5000/api/image/apple.png",
            "suitability": {
                "temperature": "Chilling requirement",
                "pH": "6.0-6.8",
                "elevation": "1500-2700m",
                "rainfall": "1000-1200mm"
            }
        }
    ]
    
    # Enrich each crop with LIVE DATA
    for crop in crops:
        crop_name = crop["name"]
        
        # 1. LIVE MSP Data
        msp_data = get_msp_for_crop(crop_name)
        if msp_data:
            crop["msp"] = msp_data["msp"]
            crop["msp_source"] = msp_data.get("source", "Live Government API")
            crop["msp_updated"] = msp_data.get("date")
        
        # 2. REAL-TIME Disease Risk Calculation
        disease_risks = get_crop_disease_risks(crop_name)
        crop["diseases"] = disease_risks["diseases"]
        crop["weather_context"] = weather
        
        # 3. REAL-TIME Cultivation Advisory
        cultivation = CultivationAdvisor.get_current_cultivation_stage(crop_name)
        if cultivation.get("status") != "Off-season":
            crop["cultivation_stage"] = cultivation["current_stage"]
            crop["cultivation_season"] = cultivation["season"]
            crop["stage_days_remaining"] = cultivation["days_remaining"]
            crop["immediate_operations"] = cultivation["operations"]
        else:
            crop["cultivation_status"] = "Off-season"
            crop["next_season_advisory"] = "Plan for next suitable season"
    
    return jsonify({
        "crops": crops,
        "season": "Monsoon" if is_monsoon else "Summer" if is_summer else "Winter",
        "weather": weather,
        "timestamp": datetime.now().isoformat(),
        "data_integration": "LIVE - MSP, Weather, Disease Risk, Cultivation Stage"
    })


@app.route("/api/crops/<int:crop_id>", methods=["GET"])
def get_crop_detail(crop_id):
    """Returns detailed information for a specific crop with REAL-TIME context"""
    crops_response = get_crops()
    crops_data = crops_response.get_json()
    
    crop = next((c for c in crops_data["crops"] if c["id"] == crop_id), None)
    
    if not crop:
        return jsonify({"error": "Crop not found"}), 404
    
    # Get comprehensive real-time advisory for this specific crop
    weather = WeatherDiseaseRiskCalculator.get_simulated_weather()
    
    # Add detailed cultivation advisory
    cultivation_advisory = CultivationAdvisor.get_weather_based_recommendations(
        crop["name"],
        weather
    )
    
    crop["detailed_advisory"] = cultivation_advisory
    crop["weather"] = weather
    crop["timestamp"] = datetime.now().isoformat()
    
    return jsonify(crop)


# ============== Settings Endpoints ==============

@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Retrieve current user settings"""
    try:
        settings = load_settings()
        settings["last_updated"] = datetime.now().isoformat()
        return jsonify({
            "success": True,
            "settings": settings,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error retrieving settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update user settings (partial or complete update)"""
    try:
        # Get current settings
        current_settings = load_settings()
        
        # Get new settings from request
        new_settings = request.json or {}
        
        # Merge settings (only update provided keys)
        updated_settings = {**current_settings, **new_settings}
        
        # Validate and sanitize settings
        validated_settings = {
            "language": new_settings.get("language", current_settings.get("language", "EN")),
            "crop_cluster": new_settings.get("crop_cluster", current_settings.get("crop_cluster", "All Karnataka")),
            "notifications": new_settings.get("notifications", current_settings.get("notifications", True)),
            "price_alerts": new_settings.get("price_alerts", current_settings.get("price_alerts", True)),
            "theme": new_settings.get("theme", current_settings.get("theme", "light")),
            "region": new_settings.get("region", current_settings.get("region", "Karnataka")),
            "unit_preference": new_settings.get("unit_preference", current_settings.get("unit_preference", "metric")),
            "crop_favorites": new_settings.get("crop_favorites", current_settings.get("crop_favorites", []))
        }
        
        # Validate types
        if not isinstance(validated_settings.get("notifications"), bool):
            validated_settings["notifications"] = True
        if not isinstance(validated_settings.get("price_alerts"), bool):
            validated_settings["price_alerts"] = True
        if not isinstance(validated_settings.get("crop_favorites"), list):
            validated_settings["crop_favorites"] = []
        
        # Validate language code
        valid_languages = ["EN", "KN", "TE", "TA", "HI"]
        if validated_settings["language"] not in valid_languages:
            validated_settings["language"] = "EN"
        
        # Validate crop cluster
        valid_clusters = ["All Karnataka", "North Karnataka", "South Karnataka", "Coastal Karnataka", "Malnad"]
        if validated_settings["crop_cluster"] not in valid_clusters:
            validated_settings["crop_cluster"] = "All Karnataka"
        
        # Save settings
        success = save_settings(validated_settings)
        
        if success:
            validated_settings["last_updated"] = datetime.now().isoformat()
            return jsonify({
                "success": True,
                "message": "Settings updated successfully",
                "settings": validated_settings,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to save settings"}), 500
            
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings/language", methods=["POST"])
def update_language():
    """Update language setting specifically"""
    try:
        data = request.json or {}
        language = data.get("language", "EN")
        
        # Validate language
        valid_languages = ["EN", "KN", "TE", "TA", "HI"]
        if language not in valid_languages:
            return jsonify({"success": False, "error": f"Invalid language. Must be one of: {valid_languages}"}), 400
        
        settings = load_settings()
        settings["language"] = language
        
        if save_settings(settings):
            return jsonify({
                "success": True,
                "message": f"Language updated to {language}",
                "language": language,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to update language"}), 500
            
    except Exception as e:
        logger.error(f"Error updating language: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings/region", methods=["POST"])
def update_region():
    """Update crop cluster/region setting"""
    try:
        data = request.json or {}
        crop_cluster = data.get("crop_cluster", "All Karnataka")
        
        # Validate region
        valid_clusters = ["All Karnataka", "North Karnataka", "South Karnataka", "Coastal Karnataka", "Malnad"]
        if crop_cluster not in valid_clusters:
            return jsonify({"success": False, "error": f"Invalid region. Must be one of: {valid_clusters}"}), 400
        
        settings = load_settings()
        settings["crop_cluster"] = crop_cluster
        
        if save_settings(settings):
            return jsonify({
                "success": True,
                "message": f"Region updated to {crop_cluster}",
                "crop_cluster": crop_cluster,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to update region"}), 500
            
    except Exception as e:
        logger.error(f"Error updating region: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings/notifications", methods=["POST"])
def update_notifications():
    """Update notification settings"""
    try:
        data = request.json or {}
        notifications = data.get("notifications", True)
        price_alerts = data.get("price_alerts", True)
        
        settings = load_settings()
        settings["notifications"] = bool(notifications)
        settings["price_alerts"] = bool(price_alerts)
        
        if save_settings(settings):
            return jsonify({
                "success": True,
                "message": "Notification settings updated",
                "notifications": settings["notifications"],
                "price_alerts": settings["price_alerts"],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to update notifications"}), 500
            
    except Exception as e:
        logger.error(f"Error updating notifications: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings/favorites", methods=["POST"])
def update_favorites():
    """Add or remove crop from favorites"""
    try:
        data = request.json or {}
        crop_id = data.get("crop_id")
        action = data.get("action", "add")  # "add" or "remove"
        
        if crop_id is None:
            return jsonify({"success": False, "error": "crop_id is required"}), 400
        
        settings = load_settings()
        favorites = settings.get("crop_favorites", [])
        
        if action == "add":
            if crop_id not in favorites:
                favorites.append(crop_id)
        elif action == "remove":
            if crop_id in favorites:
                favorites.remove(crop_id)
        else:
            return jsonify({"success": False, "error": "action must be 'add' or 'remove'"}), 400
        
        settings["crop_favorites"] = favorites
        
        if save_settings(settings):
            return jsonify({
                "success": True,
                "message": f"Favorite {action}ed successfully",
                "crop_id": crop_id,
                "crop_favorites": favorites,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to update favorites"}), 500
            
    except Exception as e:
        logger.error(f"Error updating favorites: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/settings/reset", methods=["POST"])
def reset_settings():
    """Reset all settings to default values"""
    try:
        default_settings = DEFAULT_SETTINGS.copy()
        
        if save_settings(default_settings):
            default_settings["last_updated"] = datetime.now().isoformat()
            return jsonify({
                "success": True,
                "message": "Settings reset to defaults",
                "settings": default_settings,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"success": False, "error": "Failed to reset settings"}), 500
            
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============== Cultivation Manager & Knowledge Core Routes ==============
from cultivation_manager import CultivationManager

@app.route("/api/cultivation/start", methods=["POST"])
def start_cultivation():
    """Start a new crop cycle"""
    data = request.json or {}
    start_date = data.get("start_date") # Optional YYYY-MM-DD
    crop_name = data.get("crop_name", "Paddy") # Default to Paddy if not sent
    
    result = CultivationManager.start_cultivation(crop_name=crop_name, start_date_str=start_date)
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 500

@app.route("/api/cultivation/update", methods=["POST"])
def update_cultivation_phase():
    """Update current phase (next/prev)"""
    data = request.json or {}
    action = data.get("action", "next") # "next", "prev", or phase_index
    
    result = CultivationManager.update_phase(action)
    if result["success"]:
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route("/api/cultivation/dashboard", methods=["GET"])
def get_cultivation_dashboard():
    """Get rich dashboard data: User Status + Phase Procedures + AI Alerts"""
    try:
        data = CultivationManager.get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Dashboard Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/knowledge/<crop_name>/lifecycle", methods=["GET"])
def get_crop_lifecycle(crop_name):
    """ReadOnly access to the full knowledge base for a specific crop"""
    data = CultivationManager.get_static_knowledge(crop_name)
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": f"Knowledge base for {crop_name} not found"}), 404


# ---------------- Route 7: In-Situ Disease Detection (Cultivation Integrated) ----------------
@app.route("/api/cultivation/detect", methods=["POST"])
def detect_and_log_disease():
    """
    Analyzes an image and LOGS the result to the user's cultivation history.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # 1. Analyze using the existing AI Service logic (reused from /api/analyze-image)
        # For DRY, we should ideally extract this logic, but for now we'll duplicate the call to the AI service
        # or instantiate the analyzer directly if possible.
        
        # Save temp file
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)
        
        # Analyze
        analysis_result = ImageAnalyzer.analyze(temp_path)
        
        # Cleanup
        os.remove(temp_path)
        
        # 2. LOG to Cultivation History
        if analysis_result:
            CultivationManager.log_disease_detection(
                disease_name=analysis_result.get("disease_name", "Unknown"),
                confidence=analysis_result.get("confidence_score", 0),
                image_url=None # We aren't storing permanent URLs for now
            )
            
            # 3. Retrieve Cure from Knowledge Base (or Learn it)
            knowledge = CultivationManager.get_static_knowledge()
            protocols = knowledge.get("disease_protocols", {})
            
            # Fuzzy find protocol
            matched_protocol = None
            detected_name = analysis_result.get("disease_name", "Unknown").lower()
            
            # 1. Try Local Match
            for pid, pdata in protocols.items():
                if pdata["name"].lower() in detected_name or detected_name in pdata["name"].lower():
                    matched_protocol = pdata
                    break
            
            # 2. If Unknown, Learn it via Gemini
            is_newly_learned = False
            if not matched_protocol and detected_name != "unknown":
                logger.info(f"Disease '{detected_name}' not in DB. Initiating learning sequence...")
                matched_protocol = CultivationManager.generate_and_learn_new_disease(analysis_result.get("disease_name"))
                is_newly_learned = True

            response = {
                "analysis": analysis_result,
                "protocol_match": matched_protocol,
                "newly_learned": is_newly_learned,
                "message": "Disease logged" + (" and added to knowledge base." if is_newly_learned else ".")
            }
            return jsonify(response)
            
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Analysis failed"}), 500


# ============== Run ================
if __name__ == "__main__":
    app.run(debug=True, port=5000)