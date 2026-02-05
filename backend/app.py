from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from model.recommender import Recommender
from services.tripadvisor import TripAdvisorService
from services.openai_service import OpenAIService
from datetime import datetime, timedelta

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
print(f"Loading env from: {env_path}")
print(f"T_API_KEY loaded: {bool(os.getenv('T_API_KEY'))}")
print(f"HOST loaded: {bool(os.getenv('HOST'))}")
print(f"OPENAI_API_KEY loaded: {bool(os.getenv('OPENAI_API_KEY'))}")

app = Flask(__name__)
CORS(app)

model_path = os.path.join(os.path.dirname(__file__), 'model/destinai_model.pkl')
dataset_path = os.path.join(os.path.dirname(__file__), 'model/destinai_final_dataset.csv')

try:
    recommender = Recommender(model_path, dataset_path)
except Exception as e:
    print(f"Failed to load recommender: {e}")
    recommender = None

tripadvisor = TripAdvisorService()
openai_service = OpenAIService()

@app.route('/')
def home():
    return jsonify({"message": "DestinAI Backend is running!"})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    if recommender is None:
        return jsonify({"error": "Recommender model not available"}), 500
    
    try:
        data = request.json
        preferences = data.get('preferences', {})

        recommendations = recommender.get_recommendations(preferences)
        
        if not recommendations:
            return jsonify({"error": "No recommendations found"}), 404
            
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/plan', methods=['POST'])
def plan():
    try:
        data = request.json
        city_name = data.get('city')
        user_input = data.get('userInput', "")
        preferences = data.get('preferences', {})
        
        if not city_name:
             return jsonify({"error": "City name is required"}), 400

        duration = data.get('duration', 5)
        start_date_str = data.get('startDate', datetime.now().strftime('%Y-%m-%d'))
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = start_date + timedelta(days=int(duration))
            end_date_str = end_date.strftime('%Y-%m-%d')
        except:
            start_date_str = datetime.now().strftime('%Y-%m-%d')
            end_date_str = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')

        itinerary = openai_service.get_itinerary(
            city_name, preferences, duration, start_date_str, end_date_str, user_input
        )
        
        geo = tripadvisor.get_geo_id(city_name)
        hotels = None

        if geo and "dest_id" in geo:
            hotels = tripadvisor.get_hotels(geo["dest_id"], start_date_str, end_date_str)
        else:
            print("Geo ID not found, using mock hotels")
            hotels = tripadvisor.get_mock_hotels()
            
        response = {
            "city": city_name,
            "itinerary": itinerary,
            "hotels": hotels
        }
        
        return jsonify(response)

    except Exception as e:
        print(f"Error in plan endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/lucky', methods=['GET'])
def lucky():
    if recommender is None:
        return jsonify({"error": "Recommender model not available"}), 500
    
    try:

        random_city_data = recommender.get_random_city()
        if not random_city_data:
            return jsonify({"error": "Could not select a random city"}), 500
            
        city_name = random_city_data['city']
        country = random_city_data['country']

        description = openai_service.get_city_brief(city_name)
        
        return jsonify({
            "id": int(random_city_data['details'].get('id', 0)) if 'id' in random_city_data['details'] else 0,
            "name": city_name,
            "country": country,
            "desc": description,
            "image": random_city_data['details'].get('city_photo', "")
        })

    except Exception as e:
        print(f"Error in lucky endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/review', methods=['POST'])
def review():
    try:
        data = request.json
        rating = data.get('rating')
        comment = data.get('comment', '')
        city = data.get('city', 'Unknown')
        
        if not rating:
             return jsonify({"error": "Rating is required"}), 400

        reviews_file = os.path.join(os.path.dirname(__file__), 'reviews.csv')
        file_exists = os.path.isfile(reviews_file)
        
        import csv
        with open(reviews_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'city', 'rating', 'comment'])
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, city, rating, comment])
            
        return jsonify({"message": "Review saved successfully"})

    except Exception as e:
        print(f"Error in review endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
