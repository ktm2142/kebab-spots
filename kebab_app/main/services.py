from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from django.core.cache import cache


class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="KebabSpots/1.0 (rghnmju@gmail.com)")

    def get_coordinates(self, address):
        # Спробуємо отримати результат з кешу
        cache_key = f"geocode_{address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            location = self.geolocator.geocode(address)
            if location:
                result = (location.latitude, location.longitude)
                # Зберігаємо результат в кеші на 1 день
                cache.set(cache_key, result, 86400)
                return result
        except (GeocoderTimedOut, GeocoderServiceError):
            # Обробка помилок геокодування
            pass

        return None
