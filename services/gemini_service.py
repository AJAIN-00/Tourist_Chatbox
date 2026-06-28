import os
import time
import requests

# Gemini REST API endpoint
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"

# Setup system instruction prompt
SYSTEM_INSTRUCTION = (
    "You are a professional Tamil Nadu tourist guide. "
    "Answer only tourism questions about Chennai, Coimbatore, and Kanyakumari. "
    "Provide history, travel tips, entry fees, best visiting time, nearby attractions, and suggested itineraries. "
    "Politely redirect unrelated questions back to tourism."
)

# Models to try in order (most capable first)
MODELS_TO_TRY = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest",
    "gemini-2.0-flash",
]


def call_gemini_api(api_key, model, message, system_instruction=None, retries=3):
    """Call Gemini REST API with retry logic for rate limiting."""
    url = GEMINI_API_BASE.format(model)
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    body = {
        "contents": [
            {"role": "user", "parts": [{"text": message}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048
        }
    }

    if system_instruction:
        body["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    for attempt in range(retries):
        try:
            response = requests.post(
                url, headers=headers, params=params, json=body, timeout=30
            )

            if response.status_code == 429:
                # Rate limited — wait and retry
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Rate limited on {model} (attempt {attempt+1}). Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            if response.status_code == 404:
                # Model not found — stop retrying this model
                raise requests.exceptions.HTTPError(
                    f"Model {model} not found", response=response
                )

            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise  # Don't retry 404
            if attempt == retries - 1:
                raise
            time.sleep(1)
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(1)

    raise Exception(f"Rate limit exceeded for model {model} after {retries} attempts.")


def chat_with_gemini(message, session_id=None):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "Hello! I am your Tamil Nadu Tourist Guide. "
            "(Note: The Gemini API key is not configured. Please add your GEMINI_API_KEY to environment variables.)\n\n"
            "I can help you explore Marina Beach in Chennai, Isha Yoga Center in Coimbatore, or "
            "Vivekananda Rock Memorial in Kanyakumari. What details can I share with you?"
        )

    last_error = None
    for model in MODELS_TO_TRY:
        try:
            print(f"Trying model: {model}")
            result = call_gemini_api(api_key, model, message, SYSTEM_INSTRUCTION)
            print(f"Success with model: {model}")
            return result
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == 404:
                print(f"Model {model} not found, trying next...")
                continue
            elif status == 429:
                print(f"Rate limit on {model}, trying next model...")
                last_error = "rate_limit"
                continue
            elif status == 400:
                print(f"Bad request on {model}: {e.response.text}")
                last_error = "bad_request"
                continue
            last_error = str(status)
            continue
        except Exception as e:
            print(f"Error with {model}: {str(e)[:100]}")
            last_error = str(e)[:100]
            continue

    # All models failed — return friendly message
    if last_error == "rate_limit":
        return (
            "⚠️ The AI guide is temporarily busy due to high traffic. "
            "Please wait a moment and try again. In the meantime, here are some highlights:\n\n"
            "🏖️ **Chennai**: Marina Beach, Fort St. George, Kapaleeshwarar Temple\n"
            "🧘 **Coimbatore**: Isha Yoga Center, Adiyogi Statue, Marudhamalai Temple\n"
            "🌊 **Kanyakumari**: Vivekananda Rock Memorial, Thiruvalluvar Statue, Sunrise/Sunset views"
        )

    return (
        "⚠️ The AI guide is temporarily unavailable. Please try again in a moment.\n\n"
        "🏖️ **Chennai**: Marina Beach, Fort St. George, Kapaleeshwarar Temple\n"
        "🧘 **Coimbatore**: Isha Yoga Center, Adiyogi Statue, Marudhamalai Temple\n"
        "🌊 **Kanyakumari**: Vivekananda Rock Memorial, Thiruvalluvar Statue, Sunrise/Sunset views"
    )


def generate_itinerary_prompt(city, days):
    return (
        f"Generate a detailed {days}-day trip itinerary for the city of {city}, Tamil Nadu. "
        "Include local places, a realistic time schedule (morning, afternoon, evening), "
        "popular local food suggestions (breakfast, lunch, dinner), and estimated cost per day. "
        "Return the output in Markdown format."
    )


def generate_itinerary_ai(city, days):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return get_fallback_itinerary(city, days)

    system = "You are a professional travel itinerary planner for Tamil Nadu."
    prompt = generate_itinerary_prompt(city, days)

    for model in MODELS_TO_TRY:
        try:
            result = call_gemini_api(api_key, model, prompt, system)
            return result
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status in (404, 429, 400):
                continue
        except Exception:
            continue

    return get_fallback_itinerary(city, days)


def get_fallback_itinerary(city, days):
    city = city.title()
    days = int(days)

    itineraries = {
        "Chennai": {
            1: (
                "### 1-Day Chennai Itinerary\n"
                "- **06:00 AM**: Sunrise walk at **Marina Beach**.\n"
                "- **08:30 AM**: Breakfast at *Murugan Idli Shop* (Est: ₹150)\n"
                "- **09:30 AM**: Visit **Fort St George** museum. (Entry: ₹20)\n"
                "- **12:00 PM**: Lunch at *Annalakshmi Restaurant*. (Est: ₹400)\n"
                "- **02:30 PM**: Explore **Kapaleeshwarar Temple** in Mylapore.\n"
                "- **05:00 PM**: Visit **Valluvar Kottam** monument. (Entry: ₹10)\n"
                "- **08:00 PM**: Dinner at *Ratna Cafe*. (Est: ₹200)\n\n"
                "**Total Estimated Daily Cost**: ₹1,000 per person."
            ),
            2: (
                "### 2-Day Chennai Itinerary\n\n"
                "#### Day 1: Heritage & History\n"
                "- Marina Beach, Fort St George, Kapaleeshwarar Temple, Mylapore shopping.\n\n"
                "#### Day 2: Nature & Modern Highlights\n"
                "- Guindy National Park, Spencer Plaza, Elliot's Beach.\n\n"
                "**Total Estimated Cost**: ₹2,200 per person."
            ),
            3: (
                "### 3-Day Chennai Itinerary\n\n"
                "#### Day 1: Coastal & Colonial Heritage\n- Marina Beach, Fort St George, Valluvar Kottam.\n\n"
                "#### Day 2: Spiritual Mylapore & Wildlife\n- Kapaleeshwarar Temple, Guindy National Park.\n\n"
                "#### Day 3: Mahabalipuram Excursion\n- Shore Temple, Pancha Rathas (50 km away).\n\n"
                "**Total Estimated Cost**: ₹3,800 per person."
            )
        },
        "Coimbatore": {
            1: (
                "### 1-Day Coimbatore Itinerary\n"
                "- **08:00 AM**: Breakfast at *Sree Annapoorna*. (Est: ₹150)\n"
                "- **09:30 AM**: **Adiyogi Statue** & **Isha Yoga Center**.\n"
                "- **01:00 PM**: Lunch at *Haribhavanam Restaurant*. (Est: ₹300)\n"
                "- **03:00 PM**: **Marudhamalai Temple** hilltop.\n"
                "- **05:30 PM**: **VOC Park** stroll. (Entry: ₹20)\n"
                "- **08:00 PM**: Dinner at *Sri Anandhaas*. (Est: ₹180)\n\n"
                "**Total Estimated Daily Cost**: ₹850 per person."
            ),
            2: (
                "### 2-Day Coimbatore Itinerary\n\n"
                "#### Day 1: Spiritual & Hillside Beauty\n"
                "- Isha Yoga Center, Adiyogi Statue, Marudhamalai Temple.\n\n"
                "#### Day 2: Nature, Waterfalls & Science\n"
                "- Kovai Kutralam (Siruvani Waterfalls), Gedee Car Museum.\n\n"
                "**Total Estimated Cost**: ₹1,800 per person."
            ),
            3: (
                "### 3-Day Coimbatore Itinerary\n\n"
                "#### Day 1: Isha Foundation & Adiyogi\n- Dhyanalinga, Linga Bhairavi, Adiyogi Statue.\n\n"
                "#### Day 2: Foothills and Waterfalls\n- Kovai Kutralam, Marudhamalai Temple.\n\n"
                "#### Day 3: Anamalai Tiger Reserve Excursion\n- Day trip to Pollachi/Anamalai.\n\n"
                "**Total Estimated Cost**: ₹3,500 per person."
            )
        },
        "Kanyakumari": {
            1: (
                "### 1-Day Kanyakumari Itinerary\n"
                "- **05:30 AM**: Sunrise at **Kanyakumari Beach**.\n"
                "- **07:30 AM**: Breakfast at *Hotel Saravana Bhavan*. (Est: ₹120)\n"
                "- **08:30 AM**: Ferry to **Vivekananda Rock Memorial**. (₹70)\n"
                "- **12:00 PM**: Seafood lunch at *The Ocean Restaurant*. (Est: ₹350)\n"
                "- **02:30 PM**: **Gandhi Memorial**. (Free)\n"
                "- **05:00 PM**: Sunset at **Sunset Point**.\n"
                "- **08:00 PM**: Dinner at *Triveni Restaurant*. (Est: ₹200)\n\n"
                "**Total Estimated Daily Cost**: ₹950 per person."
            ),
            2: (
                "### 2-Day Kanyakumari Itinerary\n\n"
                "#### Day 1: Confluence & Monuments\n"
                "- Vivekananda Rock Memorial, Gandhi Memorial, Sunset Point.\n\n"
                "#### Day 2: Cultural Heritage & Temples\n"
                "- Kumari Amman Temple, Padmanabhapuram Palace.\n\n"
                "**Total Estimated Cost**: ₹2,000 per person."
            ),
            3: (
                "### 3-Day Kanyakumari Itinerary\n\n"
                "#### Day 1: Sunrise & Confluence Rocks\n- Kanyakumari Beach, Vivekananda Memorial, Sunset Point.\n\n"
                "#### Day 2: Palaces & Forts\n- Padmanabhapuram Palace, Vattakottai Fort.\n\n"
                "#### Day 3: Temples & Waterfalls\n- Suchindram Temple, Thirparappu Waterfalls.\n\n"
                "**Total Estimated Cost**: ₹3,200 per person."
            )
        }
    }

    return itineraries.get(city, {}).get(
        days,
        f"Itinerary for {city} ({days} days) is not available. Please try Chennai, Coimbatore, or Kanyakumari."
    )
