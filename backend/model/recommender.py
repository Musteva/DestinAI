import pandas as pd
import joblib
import os
import re
import numpy as np

class Recommender:
    def __init__(self, model_path, dataset_path):
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.model = None
        self.dataset = None
        self.MONTH_MAP = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        self.load_resources()

    def load_resources(self):
        try:
            self.model = joblib.load(self.model_path)
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

        try:
            self.dataset = pd.read_csv(self.dataset_path)
            self.dataset.dropna(subset=['city'], inplace=True)
            self.dataset = self.dataset.reset_index(drop=True)
            print(f"Dataset loaded from {self.dataset_path}")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            raise

    def clean_and_parse_list(self, raw_string):
        if pd.isna(raw_string):
            return set()
        cleaned = re.sub(r'[\[\]""]', '', str(raw_string))
        items = {item.strip() for item in cleaned.split(',') if item.strip()}
        return items

    def map_months(self, month_num_list):
        return [self.MONTH_MAP.get(month, month) for month in month_num_list]

    def get_recommendations(self, preferences, n_recommendations=5):

        raw_duration = preferences.get('ideal_durations', ['Shorttrip'])

        if isinstance(raw_duration, str):
             raw_duration = [raw_duration]
        
        valid_durations = {"Shorttrip", "Longtrip"}

        mapped_duration = []
        for d in raw_duration:
            d_str = str(d).replace("'", "").replace('"', "")
            if d_str in valid_durations:
                mapped_duration.append(d_str)
            elif d_str in ["Week", "Short"]:
                mapped_duration.append("Shorttrip")
            elif d_str in ["2Weeks", "10Days", "Long"]:
                mapped_duration.append("Longtrip")

        if not mapped_duration:
             mapped_duration = ["Shorttrip"]

        duration_str = str(mapped_duration).replace("'", '"')

        months_str = str(preferences.get('best_months', [])).replace("'", '"')

        pref_df_data = {
            'ideal_durations': [duration_str],
            'budget_levl': [int(preferences.get('budget_levl', 2))],
            'culture': [int(preferences.get('culture', 0))],
            'adventure': [int(preferences.get('adventure', 0))],
            'nature': [int(preferences.get('nature', 0))],
            'beaches': [int(preferences.get('beaches', 0))],
            'nightlife': [int(preferences.get('nightlife', 0))],
            'cuisine': [int(preferences.get('cuisine', 0))],
            'wellness': [int(preferences.get('wellness', 0))],
            'urban': [int(preferences.get('urban', 0))],
            'seclusion': [int(preferences.get('seclusion', 0))],
            'best_months': [months_str]
        }

        new_preference = pd.DataFrame(pref_df_data)

        try:
            transformed_preference = self.model.named_steps['preprocessor'].transform(new_preference)
            distances, indices = self.model.named_steps['classifier'].kneighbors(
                transformed_preference,
                n_neighbors=n_recommendations
            )

            train_cities = self.model.named_steps['classifier'].train_cities
            
            recommendations = []
            
            for i in range(n_recommendations):
                rec_index = indices[0][i]
                rec_city_name = train_cities[rec_index]
                rec_city_distance = distances[0][i]

                city_data = self.dataset.iloc[rec_index]

                details_dict = city_data.to_dict()
                for k, v in details_dict.items():
                    if pd.isna(v):
                        details_dict[k] = None

                rec_obj = {
                    "city": rec_city_name,
                    "distance": float(rec_city_distance),
                    "details": details_dict
                }
                recommendations.append(rec_obj)
                
            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            raise

    def get_random_city(self):

        if self.dataset is None or self.dataset.empty:
            return None

        random_row = self.dataset.sample(n=1).iloc[0]
        city_full = random_row['city']

        parts = city_full.split(',')
        country = parts[-1].strip() if len(parts) > 1 else ""
        
        return {
            "city": city_full,
            "country": country,
            "details": random_row.to_dict()
        }
