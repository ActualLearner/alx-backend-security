from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP


class IPLoggingAndBlockingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP X_FORWARDED_FOR')

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # check if it's blacklisted before logging
        if ip_address and BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP address is blocked.")

            # Log the request
        if ip_address:
            RequestLog.objects.create(
                ip_address=ip_address,
                path=request.path
            )

        response = self.get_response(request)
        return response
