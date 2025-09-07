from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import RequestLog, SuspiciousIP

HIGH_REQUEST_THRESHOLD = 100
SENSITIVE_PATHS = ['/admin/', '/login/']


@shared_task
def detect_suspicious_ips():
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1. Find IPs with high request volume
    high_volume_ips = RequestLog.objects.filter(timestamp__gte=one_hour_ago) \
        .values('ip_address') \
        .annotate(request_count=Count('id')) \
        .filter(request_count__gt=HIGH_REQUEST_THRESHOLD)

    for item in high_volume_ips:
        ip = item['ip_address']
        count = item['request_count']
        reason = f"High request volume: {count} requests in the last hour."
        SuspiciousIP.objects.update_or_create(
            ip_address=ip,
            defaults={'reason': reason}
        )

    # 2. Find IPs accessing sensitive paths
    for path in SENSITIVE_PATHS:
        sensitive_access_ips = RequestLog.objects.filter(
            timestamp__gte=one_hour_ago,
            path__startswith=path
        ).values_list('ip_address', flat=True).distinct()

        for ip in sensitive_access_ips:
            reason = f"Accessed sensitive path: {path}."
            SuspiciousIP.objects.update_or_create(
                ip_address=ip,
                defaults={'reason': reason}
            )

    return "Anomaly detection task completed."
