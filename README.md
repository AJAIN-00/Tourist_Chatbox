# 🏛️ Tamil Nadu Smart Tourist Guide

A production-ready, feature-rich Flask web application helping tourists explore the historical and cultural highlights of **Chennai**, **Coimbatore**, and **Kanyakumari**. Built with a sleek **Glassmorphism Dark/Light UI**, Google Gemini AI, live weather dashboards, automatic maps integration, multilingual translations, and a secure admin management portal.

---

## ✨ Key Features

1. **🗺️ Interactive Sights Catalog**:
   - Detailed profiles for 15 curated tourist locations (5 per city) with description, history, ticket prices, timings, best season, and geolocation coordinates.
   - Dynamic search box and city-based filtering (Chennai, Coimbatore, Kanyakumari).
   
2. **🤖 AI Smart Guide (Gemini API)**:
   - Interactive chatbot offering historical facts, travel recommendations, and packing advice.
   - Built-in suggestion chips for quick questioning.
   - **Voice Input** support (using browser Speech Recognition).
   - Dynamic **Multilingual Translation** support (English, Tamil, Hindi, French) via LibreTranslate.

3. **📅 AI-Powered Itinerary Planner**:
   - Generates customized multi-day travel schedules based on selected cities and trip durations.
   - Export option to download the plan as a clean, print-friendly **PDF**.

4. **🌦️ Real-Time Weather Dashboard**:
   - Live weather metrics fetched via the OpenWeatherMap API for Chennai, Coimbatore, and Kanyakumari.
   - Contextual travel warnings and packing tips based on current conditions.
   
5. **📞 Integrated Safety & Contacts**:
   - Instant access to state tourist helplines, police, ambulance, and nearest local hospitals for each city.

6. **📱 QR Code Sharing**:
   - Generates a scan-ready QR code for each sight, allowing tourists to instantly open guide pages on their mobile devices.

7. **🔐 Secure Admin Portal**:
   - Full CRUD capability (Create, Read, Update, Delete) to manage attractions database records.
   - Secure login mechanism using SHA-256 hashed password credentials.

---

## 🛠️ Technology Stack

- **Backend**: Python Flask 3.0+
- **Database**: SQLite (structured `tourism.db` with auto-seeding)
- **AI Engine**: Google Gemini Pro API (`google-generativeai`)
- **APIs Integrated**:
  - OpenWeatherMap API (Weather data)
  - Google Maps Embed API (Maps previews & routing directions)
  - LibreTranslate API (Multilingual translation engine)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 (Custom Glassmorphic theme + Light/Dark mode), Bootstrap 5

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Clone and Setup
Open your terminal and run the following:

```bash
# Clone the repository
git clone https://github.com/AJAIN-00/Tourist_Chatbox.git
cd Tourist_Chatbox

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (use `.env.example` as a template) and add your API keys:

```ini
SECRET_KEY=your_flask_secret_key
GEMINI_API_KEY=your_google_gemini_api_key
OPENWEATHER_API_KEY=your_open_weather_map_api_key
```

### 4. Run the Application
Start the Flask development server:

```bash
python app.py
```
Visit **`http://127.0.0.1:5000`** in your browser!

*Note: The SQLite database (`tourism.db`) will automatically initialize and seed itself with the 15 tourist locations on the first run.*

---

## 🔐 Admin Panel Access

- **Route**: `/admin/login`
- **Default Username**: `admin`
- **Default Password**: `admin123`

*(Password is securely stored as a SHA-256 hash in the database. Credentials can be customized in `models/database.py`)*

---

## 🌐 Production Deployment

The project is pre-configured for one-click deployment on **Render** using the provided `render.yaml` and `Procfile`.

1. Push your repository to GitHub.
2. Link your GitHub account to **Render**.
3. Create a new **Blueprint Instance** and select your `Tourist_Chatbox` repository.
4. Set the required Environment Variables (`GEMINI_API_KEY`, `OPENWEATHER_API_KEY`, etc.) in the Render dashboard.

---

## 📂 Project Structure

```
├── models/
│   └── database.py        # Database schema, CRUD methods, and seed data
├── services/
│   ├── gemini_service.py    # AI Chatbot & Itinerary generation service
│   ├── maps_service.py      # Google Maps embed url generation
│   ├── translate_service.py # LibreTranslate integration
│   └── weather_service.py   # OpenWeatherMap API wrapper
├── static/
│   ├── css/style.css        # Glassmorphism dark/light design system
│   └── js/main.js           # Interactive JS (Dark mode, QR code, Speech, Itinerary export)
├── templates/               # UI HTML layouts
├── .gitignore
├── app.py                   # Main Flask routes and core app setup
├── Procfile                 # Production WSGI server command
├── render.yaml              # Render deployment configuration
└── requirements.txt         # Required Python packages
```
