import requests
import os

class TripAdvisorService:
    def __init__(self):
        self.api_key = os.getenv("T_API_KEY")
        self.host = os.getenv("HOST")
        self.base_url = f"https://{self.host}/api/v1/hotels"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host
        }

    def get_geo_id(self, city):
        url = f"{self.base_url}/searchDestination"
        querystring = {"query": city}

        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            print(f"Geo ID response for {city}: {data}")
            
            if data.get("status") and data.get("data"):
                first = data["data"][0]
                return {
                    "dest_id": first["dest_id"]
                }
            else:
                print(f"No Geo ID found for {city}")
                return None
                
        except Exception as e:
            print(f"Error fetching Geo ID: {e}")
            return None

    def get_hotels(self, geo_id, check_in, check_out):
        url = f"{self.base_url}/searchHotels"
        querystring = {
            "dest_id": geo_id,
            "arrival_date": check_in,
            "departure_date": check_out,
            "search_type": "city",
            "pageNumber": "1",
            "sort": "rating",
            "currency": "USD"
        }

        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            raw = response.json()
            print(f"Hotels response: {raw}")

            basic_hotels = self.clean_hotels(raw, limit=5)

            if not basic_hotels:
                print("No hotels found in API, using mock data")
                return self.get_mock_hotels()

            hotels_with_urls = self.fetch_all_hotel_details(
            basic_hotels, check_in, check_out
            )

            return hotels_with_urls
            
        except Exception as e:
            print(f"Error fetching hotels: {e}")
            return self.get_mock_hotels()
        

    def clean_hotels(self, raw, limit=5):
        cleaned = []

        hotels = raw.get("data", {}).get("hotels", [])
        for h in hotels[:limit]:
            prop = h.get("property", {})

            cleaned.append({
                "name": prop.get("name"),
                "rating": prop.get("reviewScore"),
                "image": (prop.get("photoUrls") or [None])[0],
                "hotel_id": prop.get("id")
            })

        return cleaned
    
    def get_hotel_details(self, hotel_id, check_in, check_out):
        url = f"{self.base_url}/getHotelDetails"
        params = {
            "hotel_id": hotel_id,
            "arrival_date": check_in,
            "departure_date": check_out
        }

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            booking_url = data.get("data", {}).get("url")

            return {
                "hotel_id": hotel_id,
                "booking_url": booking_url
            }

        except Exception as e:
            print(f"Error fetching hotel details: {e}")
            return None

    

    def fetch_all_hotel_details(self, hotels, check_in, check_out):
        detailed_list = []

        for h in hotels:
            details = self.get_hotel_details(h["hotel_id"], check_in, check_out)

            booking_url = details.get("booking_url") if details else "https://www.tripadvisor.com"

            detailed_list.append({
                **h,
                "booking_url": booking_url
            })

        return detailed_list

    def get_mock_hotels(self):
        return [
            {
                "name": "Grand Hotel Example",
                "rating": 4.5,
                "image": "https://via.placeholder.com/150/6366f1/ffffff?text=Hotel1",
                "priceLevel": "$$",
                "booking_url": "https://www.tripadvisor.com"
            },
            {
                "name": "City Center Inn",
                "rating": 4.0,
                "image": "https://via.placeholder.com/150/6366f1/ffffff?text=Hotel2",
                "priceLevel": "$$$",
                "booking_url": "https://www.tripadvisor.com"
            },
            {
                "name": "Budget Stay Hotel",
                "rating": 4.2,
                "image": "https://via.placeholder.com/150/6366f1/ffffff?text=Hotel3",
                "priceLevel": "$",
                "booking_url": "https://www.tripadvisor.com"
            }
        ]
    
