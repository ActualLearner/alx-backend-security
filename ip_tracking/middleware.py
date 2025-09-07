from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
import requests


class IPLoggingAndBlockingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_geolocation(self, ip):
        """Fetches geolocation data for a given IP, with caching."""
        cache_key = f"geolocation_{ip}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            # Using a free, no-key-required API for this example
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
            response.raise_for_status()
            data = response.json()

            geo_data = {
                "country": data.get("country"),
                "city": data.get("city"),
            }
            # Cache for 24 hours (86400 seconds)
            cache.set(cache_key, geo_data, 86400)
            return geo_data
        except requests.RequestException:
            # If the API fails, return None and don't cache
            return None

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP X_FORWARDED_FOR')

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        if not ip_address:
            return self.get_response(request)

        # check if it's blacklisted before logging
        if ip_address and BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP address is blocked.")

        # Get geolocation data
        geo_data = self.get_geolocation(ip_address)
        country = geo_data.get("country") if geo_data else None
        city = geo_data.get("city") if geo_data else None

        # Log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            country=country,
            city=city
        )

        response = self.get_response(request)
        return response
