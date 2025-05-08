import os
import requests
from dotenv import load_dotenv

load_dotenv()

class RouteService:
    def __init__(self):
        self.api_key = os.getenv('ORS_API_KEY')
        self.base_url = "https://api.openrouteservice.org/v2"

    def get_route(self, start_point, end_point):
        """Расчёт маршрута через OpenRouteService"""
        url = f"{self.base_url}/directions/driving-car"
        headers = {"Authorization": self.api_key}
        params = {
            "start": f"{start_point[1]},{start_point[0]}",  # lon,lat
            "end": f"{end_point[1]},{end_point[0]}"
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()