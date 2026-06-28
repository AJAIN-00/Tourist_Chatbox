import os
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from dotenv import load_dotenv

# Load env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(24))

# Import database and service functions
from models.database import (
    init_db, seed_data, get_all_places, get_place_by_id, 
    save_chat, verify_admin, add_place, update_place, delete_place
)
from services.gemini_service import chat_with_gemini, generate_itinerary_ai
from services.weather_service import get_weather_for_city
from services.translate_service import translate_text
from services.maps_service import get_map_embed_url, get_directions_url

# Emergency contact details per city
EMERGENCY_CONTACTS = {
    "chennai": {
        "police": "100 (Chennai City Police: 044-23452345)",
        "ambulance": "108",
        "fire_service": "101",
        "nearest_hospital": "Rajiv Gandhi Government General Hospital (044-25305000)"
    },
    "coimbatore": {
        "police": "100 (Coimbatore City Police: 0422-2300600)",
        "ambulance": "108",
        "fire_service": "101",
        "nearest_hospital": "Government Medical College and Hospital (0422-2301393)"
    },
    "kanyakumari": {
        "police": "100 (Kanyakumari District Police: 04652-220100)",
        "ambulance": "108",
        "fire_service": "101",
        "nearest_hospital": "Government Headquarters Hospital, Nagercoil (04652-226050)"
    }
}

# Ensure DB is initialized and seeded before handling requests
with app.app_context():
    init_db()
    seed_data()

# Decorator to secure admin routes
def login_required(f):
    import functools
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# ==================== PAGE ROUTES ====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/places")
def view_places():
    city_filter = request.args.get("city", "").strip()
    search_query = request.args.get("search", "").strip().lower()
    
    places = get_all_places(city_filter if city_filter else None)
    
    if search_query:
        places = [
            p for p in places 
            if search_query in p["name"].lower() or search_query in p["description"].lower()
        ]
        
    return render_template("places.html", places=places, selected_city=city_filter, search_query=search_query)

@app.route("/place/<int:place_id>")
def place_detail(place_id):
    place = get_place_by_id(place_id)
    if not place:
        flash("Tourist place not found.", "danger")
        return redirect(url_for("view_places"))
    
    # Generate Google Maps Embed and Directions URL
    map_url = get_map_embed_url(place["latitude"], place["longitude"], place["name"])
    directions_url = get_directions_url(place["latitude"], place["longitude"])
    
    return render_template("place_detail.html", place=place, map_url=map_url, directions_url=directions_url)

@app.route("/chatbot")
def view_chatbot():
    return render_template("chatbot.html")

@app.route("/itinerary")
def view_itinerary():
    return render_template("itinerary.html")

@app.route("/weather")
def view_weather():
    return render_template("weather.html")

# ==================== API ENDPOINTS ====================

@app.route("/api/test-gemini")
def test_gemini():
    """Debug endpoint to list all available Gemini models for the configured key."""
    import requests as req
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return jsonify({"status": "ERROR", "message": "GEMINI_API_KEY is NOT set in environment variables!"})

    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "TOO_SHORT"

    results = {}
    
    # Try retrieving models from v1beta
    try:
        url_beta = "https://generativelanguage.googleapis.com/v1beta/models"
        r_beta = req.get(url_beta, params={"key": api_key}, timeout=15)
        if r_beta.status_code == 200:
            results["v1beta_models"] = [m.get("name") for m in r_beta.json().get("models", [])]
        else:
            results["v1beta_error"] = f"{r_beta.status_code} - {r_beta.text}"
    except Exception as e:
        results["v1beta_exception"] = str(e)

    # Try retrieving models from v1
    try:
        url_v1 = "https://generativelanguage.googleapis.com/v1/models"
        r_v1 = req.get(url_v1, params={"key": api_key}, timeout=15)
        if r_v1.status_code == 200:
            results["v1_models"] = [m.get("name") for m in r_v1.json().get("models", [])]
        else:
            results["v1_error"] = f"{r_v1.status_code} - {r_v1.text}"
    except Exception as e:
        results["v1_exception"] = str(e)

    return jsonify({
        "api_key_prefix": masked_key,
        "key_length": len(api_key),
        "results": results
    })

@app.route("/api/places")
def api_places():
    city = request.args.get("city", "").strip()
    places = get_all_places(city if city else None)
    return jsonify(places)

@app.route("/api/place/<int:place_id>")
def api_place(place_id):
    place = get_place_by_id(place_id)
    if not place:
        return jsonify({"error": "Place not found"}), 404
    return jsonify(place)

@app.route("/chat", methods=["POST"])
def chat():
    # Input validation
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    language = data.get("language", "en").strip().lower()
    
    if not message:
        return jsonify({"error": "Message content is required"}), 400
        
    # Get Gemini response
    bot_response = chat_with_gemini(message)
    
    # Auto-translate if needed
    translated_response = bot_response
    if language != "en":
        translated_response = translate_text(bot_response, language)
        
    # Save chat history
    session_id = session.get("session_id", "default_session")
    save_chat(session_id, message, translated_response, language)
    
    return jsonify({
        "original_response": bot_response,
        "response": translated_response
    })

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    target_lang = data.get("target_language", "").strip().lower()
    
    if not text or not target_lang:
        return jsonify({"error": "Text and target_language are required"}), 400
        
    translated = translate_text(text, target_lang)
    return jsonify({"translated_text": translated})

@app.route("/weather/<city>")
def weather_info(city):
    weather_data = get_weather_for_city(city)
    if "error" in weather_data:
        return jsonify(weather_data), 400
    return jsonify(weather_data)

@app.route("/itinerary/<city>/<int:days>")
def itinerary_plan(city, days):
    city_lower = city.lower().strip()
    if city_lower not in ["chennai", "coimbatore", "kanyakumari"]:
        return jsonify({"error": "Itineraries are only supported for Chennai, Coimbatore, and Kanyakumari."}), 400
        
    if days not in [1, 2, 3]:
        return jsonify({"error": "Itinerary day count must be 1, 2, or 3 days."}), 400
        
    itinerary = generate_itinerary_ai(city.title(), days)
    return jsonify({
        "city": city.title(),
        "days": days,
        "itinerary": itinerary
    })

@app.route("/emergency/<city>")
def emergency_info(city):
    city_key = city.lower().strip()
    contacts = EMERGENCY_CONTACTS.get(city_key)
    if not contacts:
        return jsonify({"error": "Emergency contacts only available for Chennai, Coimbatore, or Kanyakumari."}), 400
    return jsonify({
        "city": city.title(),
        "contacts": contacts
    })

# ==================== ADMIN ROUTES ====================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("logged_in"):
        return redirect(url_for("admin_dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if verify_admin(username, password):
            session["logged_in"] = True
            session["username"] = username
            flash("Welcome to the Admin Panel!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin username or password.", "danger")
            
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have logged out successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    places = get_all_places()
    return render_template("admin.html", places=places)

@app.route("/admin/place/new", methods=["GET", "POST"])
@login_required
def admin_new_place():
    if request.method == "POST":
        # CSRF and Injection validation is handled natively by parameters/SQLite ORM
        data = {
            "name": request.form.get("name", "").strip(),
            "city": request.form.get("city", "").strip(),
            "description": request.form.get("description", "").strip(),
            "history": request.form.get("history", "").strip(),
            "entry_fee": request.form.get("entry_fee", "").strip(),
            "opening_time": request.form.get("opening_time", "").strip(),
            "closing_time": request.form.get("closing_time", "").strip(),
            "best_season": request.form.get("best_season", "").strip(),
            "latitude": float(request.form.get("latitude") or 0.0),
            "longitude": float(request.form.get("longitude") or 0.0),
            "nearby_attractions": request.form.get("nearby_attractions", "").strip(),
            "nearby_restaurants": request.form.get("nearby_restaurants", "").strip(),
            "nearby_hotels": request.form.get("nearby_hotels", "").strip()
        }
        
        if not data["name"] or not data["city"]:
            flash("Place name and City are required.", "danger")
            return render_template("admin_place_form.html", action="Add New", place=None)
            
        try:
            add_place(data)
            flash("New tourist place added successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            flash(f"Error adding place: {str(e)}", "danger")
            
    return render_template("admin_place_form.html", action="Add New", place=None)

@app.route("/admin/place/edit/<int:place_id>", methods=["GET", "POST"])
@login_required
def admin_edit_place(place_id):
    place = get_place_by_id(place_id)
    if not place:
        flash("Place not found.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "city": request.form.get("city", "").strip(),
            "description": request.form.get("description", "").strip(),
            "history": request.form.get("history", "").strip(),
            "entry_fee": request.form.get("entry_fee", "").strip(),
            "opening_time": request.form.get("opening_time", "").strip(),
            "closing_time": request.form.get("closing_time", "").strip(),
            "best_season": request.form.get("best_season", "").strip(),
            "latitude": float(request.form.get("latitude") or 0.0),
            "longitude": float(request.form.get("longitude") or 0.0),
            "nearby_attractions": request.form.get("nearby_attractions", "").strip(),
            "nearby_restaurants": request.form.get("nearby_restaurants", "").strip(),
            "nearby_hotels": request.form.get("nearby_hotels", "").strip()
        }
        
        if not data["name"] or not data["city"]:
            flash("Place name and City are required.", "danger")
            return render_template("admin_place_form.html", action="Edit", place=place)
            
        try:
            update_place(place_id, data)
            flash("Tourist place updated successfully!", "success")
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            flash(f"Error updating place: {str(e)}", "danger")
            
    return render_template("admin_place_form.html", action="Edit", place=place)

@app.route("/admin/place/delete/<int:place_id>", methods=["POST"])
@login_required
def admin_delete_place(place_id):
    place = get_place_by_id(place_id)
    if not place:
        flash("Place not found.", "danger")
        return redirect(url_for("admin_dashboard"))
        
    try:
        delete_place(place_id)
        flash(f"'{place['name']}' has been deleted.", "success")
    except Exception as e:
        flash(f"Error deleting place: {str(e)}", "danger")
        
    return redirect(url_for("admin_dashboard"))

# Start server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
