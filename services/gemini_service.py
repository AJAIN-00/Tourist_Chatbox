import os
from google import genai
from google.genai import types

# Setup system instruction prompt
SYSTEM_INSTRUCTION = (
    "You are a professional Tamil Nadu tourist guide. "
    "Answer only tourism questions about Chennai, Coimbatore, and Kanyakumari. "
    "Provide history, travel tips, entry fees, best visiting time, nearby attractions, and suggested itineraries. "
    "Politely redirect unrelated questions back to tourism."
)

def chat_with_gemini(message, session_id=None):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return (
            "Hello! I am your Tamil Nadu Tourist Guide. "
            "(Note: The Gemini API key is not configured. Please add your GEMINI_API_KEY in the .env file. "
            "Here is some local guide info instead!)\n\n"
            "I can help you explore Marina Beach in Chennai, Isha Yoga Center in Coimbatore, or "
            "Vivekananda Rock Memorial in Kanyakumari. What details can I share with you?"
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Try fallback model
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                )
            )
            return response.text
        except Exception as e2:
            print(f"Fallback model also failed: {e2}")
            return f"Error communicating with AI guide: {str(e)}"


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

    try:
        client = genai.Client(api_key=api_key)
        prompt = generate_itinerary_prompt(city, days)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional travel itinerary planner for Tamil Nadu.",
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini itinerary error: {e}")
        try:
            client = genai.Client(api_key=api_key)
            prompt = generate_itinerary_prompt(city, days)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a professional travel itinerary planner for Tamil Nadu.",
                )
            )
            return response.text
        except Exception as e2:
            print(f"All Gemini models failed for itinerary: {e2}")
            return f"Failed to generate itinerary using AI: {str(e)}\n\n---\n\n" + get_fallback_itinerary(city, days)


def get_fallback_itinerary(city, days):
    # Dynamic mock itineraries for Chennai, Coimbatore, Kanyakumari
    city = city.title()
    days = int(days)

    itineraries = {
        "Chennai": {
            1: (
                "### 1-Day Chennai Itinerary\n"
                "- **06:00 AM - 08:00 AM**: Start your day with a beautiful sunrise walk at **Marina Beach**, the longest natural urban beach in India.\n"
                "- **08:30 AM**: Head to *Murugan Idli Shop* for a delicious traditional breakfast of fluffy idlis, crispy dosas, and filter coffee. (Est: ₹150)\n"
                "- **09:30 AM - 11:30 AM**: Visit **Fort St George** and explore the museum showcasing colonial British history. (Entry: ₹20)\n"
                "- **12:00 PM - 02:00 PM**: Enjoy a grand South Indian Thali lunch at *Annalakshmi Restaurant*. (Est: ₹400)\n"
                "- **02:30 PM - 04:30 PM**: Visit the ancient **Kapaleeshwarar Temple** in Mylapore, exploring its colorful architecture.\n"
                "- **05:00 PM - 07:00 PM**: Relax at **Valluvar Kottam** monument, learning about the philosopher Thiruvalluvar. (Entry: ₹10)\n"
                "- **08:00 PM**: Dinner at *Ratna Cafe* trying their famous sambar-idli. (Est: ₹200)\n\n"
                "**Total Estimated Daily Cost**: ₹1,000 per person."
            ),
            2: (
                "### 2-Day Chennai Itinerary\n\n"
                "#### Day 1: Heritage & History\n"
                "- **Morning**: Sunrise walk at **Marina Beach**, breakfast at *Ratna Cafe*, followed by visiting **Fort St George**.\n"
                "- **Afternoon**: Traditional lunch at *Saravana Bhavan*, followed by **Kapaleeshwarar Temple** and shopping in Mylapore.\n"
                "- **Evening**: Sunsets at **Valluvar Kottam** and beach-side snacks.\n\n"
                "#### Day 2: Nature & Modern Highlights\n"
                "- **Morning**: Explore the peaceful wildlife at **Guindy National Park** and Chennai Snake Park. (Entry: ₹20)\n"
                "- **Afternoon**: Enjoy lunch at *Prems Graama Bhojanam* (millet-based feast), followed by shopping at Spencer Plaza or Express Avenue.\n"
                "- **Evening**: Walk along Elliot's Beach in Besant Nagar and enjoy dinner at *Thalappakatti Biryani*.\n\n"
                "**Total Estimated Cost**: ₹2,200 per person."
            ),
            3: (
                "### 3-Day Chennai Itinerary\n\n"
                "#### Day 1: Coastal & Colonial Heritage\n"
                "- **Activities**: Marina Beach, Fort St George, Valluvar Kottam. Dinner at *Saravana Bhavan*.\n\n"
                "#### Day 2: Spiritual Mylapore & Wildlife\n"
                "- **Activities**: Kapaleeshwarar Temple, Mylapore market walks, Guindy National Park. Dinner at *Annalakshmi*.\n\n"
                "#### Day 3: Excursion to Mahabalipuram (Nearby)\n"
                "- **Activities**: Take a scenic ECR drive to Mahabalipuram (50 km from Chennai). Visit the Shore Temple, Pancha Rathas, and Arjuna's Penance.\n"
                "- **Food**: Seafood lunch at *Seashore Garden Restaurant* in Mahabalipuram.\n\n"
                "**Total Estimated Cost**: ₹3,800 per person."
            )
        },
        "Coimbatore": {
            1: (
                "### 1-Day Coimbatore Itinerary\n"
                "- **08:00 AM**: Traditional breakfast of Ghee Roast Dosa at *Sree Annapoorna*. (Est: ₹150)\n"
                "- **09:30 AM - 12:30 PM**: Visit the magnificent 112-foot **Adiyogi Statue** and the serene **Isha Yoga Center**. Enjoy the peaceful atmosphere and meditatiative halls.\n"
                "- **01:00 PM - 02:30 PM**: Traditional Kovai lunch at *Haribhavanam Restaurant*. (Est: ₹300)\n"
                "- **03:00 PM - 05:00 PM**: Climb the hill to the sacred **Marudhamalai Temple** dedicated to Lord Murugan.\n"
                "- **05:30 PM - 07:30 PM**: Relax and walk around the bustling **VOC Park**. (Entry: ₹20)\n"
                "- **08:00 PM**: Enjoy dinner at *Sri Anandhaas* tasting parotta and vegetable korma. (Est: ₹180)\n\n"
                "**Total Estimated Daily Cost**: ₹850 per person."
            ),
            2: (
                "### 2-Day Coimbatore Itinerary\n\n"
                "#### Day 1: Spiritual & Hillside Beauty\n"
                "- **Morning**: Visit **Isha Yoga Center** and **Adiyogi Statue**. Breakfast at local cafe.\n"
                "- **Afternoon**: Lunch at *Sree Annapoorna*, followed by visiting the beautiful hilltop **Marudhamalai Temple**.\n"
                "- **Evening**: Stroll at **VOC Park** and local street shopping.\n\n"
                "#### Day 2: Nature, Waterfalls & Science\n"
                "- **Morning**: Drive to the picturesque **Kovai Kutralam** (Siruvani Waterfalls) and bathe in its sweet waters. (Entry/bus: ₹50)\n"
                "- **Afternoon**: Enjoy lunch at *Sri Gowrishankar*, then visit the vintage car museum **Gedee Car Museum**.\n"
                "- **Evening**: Walk and shop in the RS Puram area. Enjoy Coimbatore-style street food (Kalaan/Mushroom).\n\n"
                "**Total Estimated Cost**: ₹1,800 per person."
            ),
            3: (
                "### 3-Day Coimbatore Itinerary\n\n"
                "#### Day 1: Isha Foundation & Adiyogi\n"
                "- **Activities**: Detailed tour of Dhyanalinga, Linga Bhairavi, and Adiyogi Statue.\n\n"
                "#### Day 2: Foothills and Waterfalls\n"
                "- **Activities**: Kovai Kutralam falls, Marudhamalai Temple, VOC Park. Dinner at *Haribhavanam*.\n\n"
                "#### Day 3: Nilgiri Foothills / Anamalai Tiger Reserve Excursion\n"
                "- **Activities**: Take a day trip to Pollachi/Anamalai Tiger Reserve or Ooty toy train at Mettupalayam (40 km away).\n\n"
                "**Total Estimated Cost**: ₹3,500 per person."
            )
        },
        "Kanyakumari": {
            1: (
                "### 1-Day Kanyakumari Itinerary\n"
                "- **05:30 AM - 06:30 AM**: Witness the spectacular ocean sunrise at **Kanyakumari Beach**.\n"
                "- **07:30 AM**: Breakfast of idli-vada at *Hotel Saravana Bhavan*. (Est: ₹120)\n"
                "- **08:30 AM - 11:30 AM**: Take a ferry ride to **Vivekananda Rock Memorial** and the majestic **Thiruvalluvar Statue**. (Ferry/Entry: ₹70)\n"
                "- **12:00 PM - 02:00 PM**: Enjoy fresh seafood lunch at *The Ocean Restaurant* overlooking the coast. (Est: ₹350)\n"
                "- **02:30 PM - 04:00 PM**: Visit the historic **Gandhi Memorial** where his ashes were kept. (Free)\n"
                "- **05:00 PM - 07:00 PM**: Spend your evening watching the sun set completely over the water at **Sunset Point**.\n"
                "- **08:00 PM**: Walk the seaside local bazaar and enjoy dinner at *Triveni Restaurant*. (Est: ₹200)\n\n"
                "**Total Estimated Daily Cost**: ₹950 per person."
            ),
            2: (
                "### 2-Day Kanyakumari Itinerary\n\n"
                "#### Day 1: Confluence & Monuments\n"
                "- **Morning**: Sunrise view, ferry ride to **Vivekananda Rock Memorial** & **Thiruvalluvar Statue**.\n"
                "- **Afternoon**: Gandhi Memorial Mandapam, lunch, and resting.\n"
                "- **Evening**: Panoramic sunset at **Sunset Point** and local bazaar shopping.\n\n"
                "#### Day 2: Cultural Heritage & Temples\n"
                "- **Morning**: Visit the ancient **Kumari Amman Temple** followed by breakfast.\n"
                "- **Afternoon**: Take a short trip to the historic wooden architecture of *Padmanabhapuram Palace* (35 km away). (Entry: ₹50)\n"
                "- **Evening**: Walk on the Kanyakumari shoreline, buying unique colored sands and seashells.\n\n"
                "**Total Estimated Cost**: ₹2,000 per person."
            ),
            3: (
                "### 3-Day Kanyakumari Itinerary\n\n"
                "#### Day 1: Sunset, Sunrise & The Confluence Rocks\n"
                "- **Activities**: Sunrise at Kanyakumari Beach, Vivekananda Memorial, Gandhi Memorial, Sunset Point.\n\n"
                "#### Day 2: Palaces & Forts\n"
                "- **Activities**: Visit Padmanabhapuram Palace and Vattakottai Fort (a circular seaside fort with amazing ocean breezes).\n\n"
                "#### Day 3: Local Temples & Waterfalls\n"
                "- **Activities**: Visit the Suchindram Thanumalayan Temple (famous for musical pillars) and Courtallam Falls (if in season) or Thirparappu Waterfalls.\n\n"
                "**Total Estimated Cost**: ₹3,200 per person."
            )
        }
    }

    return itineraries.get(city, {}).get(days, f"Itinerary for {city} ({days} days) is not available. Please try Chennai, Coimbatore, or Kanyakumari.")
