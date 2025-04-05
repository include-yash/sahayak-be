import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

DATAGOV_API_KEY = os.getenv("DATAGOV_API_KEY")
DATAGOV_API_URL = "https://api.data.gov.in/resource/ee18c9d9-7f5b-4b13-acf7-5e368e91a598"  # IGNOAPS dataset
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

async def scrape_schemes_from_website() -> list:
    """
    Scrape schemes from socialjustice.gov.in as a fallback or supplement.
    """
    url = "https://socialjustice.gov.in/schemes"
    headers = {"User-Agent": "Mozilla/5.0"}  # To avoid blocking
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Scraping failed: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        schemes = []
        
        # Extract scheme details (adjust selectors based on site structure)
        scheme_blocks = soup.select(".scheme-item")  # Hypothetical selector; inspect site for actual
        if not scheme_blocks:
            # Fallback: extract any paragraph or list items
            scheme_blocks = soup.select("p, li")
        
        for block in scheme_blocks[:10]:  # Limit to 10 for simplicity
            text = block.get_text(strip=True)
            if "senior" in text.lower() or "old age" in text.lower() or "elderly" in text.lower():
                schemes.append({
                    "scheme_name": text[:50] + "..." if len(text) > 50 else text,
                    "state": "All India",  # Default; adjust if state-specific
                    "description": text,
                    "eligibility": "Senior citizens (assumed)"
                })
        
        return schemes

async def summarize_with_gemini(text: str) -> str:
    """
    Summarize text using Gemini API.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Summarize the following text in a concise paragraph:\n\n{text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return "Summary unavailable due to API error."

async def get_senior_citizen_schemes() -> list:
    """
    Fetch schemes from Data.gov.in and supplement with scraped data, then summarize.
    """
    schemes = []

    # Try Data.gov.in API
    if DATAGOV_API_KEY:
        params = {"api-key": DATAGOV_API_KEY, "format": "json", "limit": 100}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(DATAGOV_API_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    schemes.extend([
                        {
                            "scheme_name": record.get("scheme_name", "Unknown"),
                            "state": record.get("state_ut", "N/A"),
                            "description": "Old Age Pension Scheme" if "pension" in record.get("scheme_name", "").lower() else "General Welfare",
                            "eligibility": "Senior citizens aged 60+"
                        }
                        for record in records
                    ])
        except Exception as e:
            print(f"Data.gov.in error: {str(e)}")

    # Scrape additional data if needed
    scraped_schemes = await scrape_schemes_from_website()
    schemes.extend(scraped_schemes)

    # Summarize descriptions with Gemini
    for scheme in schemes:
        scheme["summary"] = await summarize_with_gemini(scheme["description"])

    # Fallback mock data if no schemes found
    if not schemes:
        print("No schemes found. Using mock data.")
        schemes = [
            {
                "scheme_name": "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
                "state": "All India",
                "description": "Monthly pension for senior citizens below poverty line.",
                "eligibility": "Age 60+, Below Poverty Line",
                "summary": "Monthly pension for seniors below poverty line."
            }
        ]

    return schemes