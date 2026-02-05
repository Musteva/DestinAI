import requests
import os
import re

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_itinerary(self, city, preferences, duration, start_date, end_date, user_input=""):
        print(f"DEBUG: Requesting itinerary for {city}, Duration: {duration} days")

        prompt = f"""
You are an expert travel planner. Create a detailed day-by-day itinerary for a trip to **{city}** for exactly **{duration} days**.

STRICT RULES:
1. You MUST generate an itinerary for ALL {duration} days.
2. Format each day strictly as: "Day X: Title of the day".
3. Under each day, provide exactly 3 bullet points for activities.
4. STRICT ACTIVITY FORMAT: "- [Time]: [Activity Name] - [Brief Description]"
   Example: "- Morning: Visit the Louvre - Explore the world's largest art museum."
5. Do not put the "Time" on its own line. It must be on the same line as the activity.
6. Do NOT output JSON, Python lists, or Markdown code blocks. Just plain text.

User Preferences:
- Adventures: {preferences.get('adventure', False)}
- Culture: {preferences.get('culture', False)}
- Relaxation: {preferences.get('nature', False)}
- Nightlife: {preferences.get('nightlife', False)}
- Budget: {preferences.get('budget', 'medium')}
- Date Range: {start_date} -> {end_date}

User's Dream Holiday Description: "{user_input}"
        """.strip()

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "You are an expert travel adviser. Output strictly formatted plain text."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            print("DEBUG: Received response from OpenAI. Parsing...")
            parsed = self._parse_itinerary(content)
            print(f"DEBUG: Parsed {len(parsed) if parsed else 0} days.")
            return parsed
            
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return None

    def _parse_itinerary(self, text):
        itinerary = []
        current_day = None

        day_pattern = re.compile(r"Day\s+(\d+)\s*[:|-]\s*(.*)", re.IGNORECASE)

        activity_pattern = re.compile(r"^[-*]\s*(?:(?:\*\*)?(.+?)(?:\*\*)?)\s*:\s*(?:(?:\*\*)?(.+?)(?:\*\*)?)(?:\s+-\s+(.+))?$", re.IGNORECASE)

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            day_match = day_pattern.search(line)
            if day_match:
                if current_day:
                    itinerary.append(current_day)
                
                day_num = day_match.group(1)
                day_title = day_match.group(2).strip().replace("**", "").replace('": [', '').replace('"', '').replace(":", "")
                
                current_day = {
                    "day": day_num,
                    "title": day_title,
                    "activities": []
                }
                continue

            if current_day and (line.startswith("-") or line.startswith("*") or (len(line)>1 and line[0].isdigit() and line[1]=='.')):

                clean_line = re.sub(r"^[-*0-9.]+\s*", "", line)

                title = ""
                time_val = "Anytime"
                desc = ""

                if ":" in clean_line:
                    parts = clean_line.split(":", 1)
                    potential_time = parts[0].strip().replace("*", "")

                    if len(potential_time) < 20:
                        time_val = potential_time
                        remainder = parts[1].strip()
                    else:
                        remainder = clean_line
                else:
                    remainder = clean_line

                if " - " in remainder:
                    title_desc = remainder.split(" - ", 1)
                    title = title_desc[0].strip().replace("**", "")
                    desc = title_desc[1].strip()
                elif ": " in remainder:
                    title_desc = remainder.split(": ", 1)
                    title = title_desc[0].strip().replace("**", "")
                    desc = title_desc[1].strip()
                else:
                    title = remainder.strip().replace("**", "")
                    desc = ""

                if not title:
                    continue

                current_day["activities"].append({
                    "time": time_val,
                    "title": title,
                    "desc": desc
                })

        if current_day:
            itinerary.append(current_day)

        if not itinerary:
            return {"raw_text": text}
            
        return itinerary

    def get_city_brief(self, city):

        prompt = f"Write a short, inspiring 2-sentence description of {city} that would make a traveler want to visit immediately."
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an enthusiastic travel copywriter."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100
        }

        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error fetching city brief: {e}")
            return f"Discover the beauty of {city}!"
