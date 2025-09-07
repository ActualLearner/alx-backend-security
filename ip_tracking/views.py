from django.http import HttpResponse
from ratelimit.decorators import ratelimit


@ratelimit(group='authenticated', key='user_or_ip', rate='10/m', block=True)
@ratelimit(group='anonymous', key='ip', rate='5/m', block=True)
def sensitive_login_view(request):
    return HttpResponse("This is a sensitive view for logging in.")

# You will also need to create a urls.py in your app and include it in your project's urls.py
# ip_tracking/urls.py
# from django.urls import path
# from .views import sensitive_login_view
# urlpatterns = [
#     path('login/', sensitive_login_view, name='sensitive_login'),
# ]
