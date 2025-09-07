# Django IP Tracking: Security and Analytics

## 1. Overview

This project is a Django application designed to enhance web security and provide valuable analytics by tracking, logging, and analyzing incoming IP addresses. It implements a multi-layered approach that includes basic request logging, IP blacklisting, geolocation, rate limiting, and automated anomaly detection.

The goal is to build a robust system that can identify and block malicious actors, prevent abuse, and offer insights into user demographics, all while respecting user privacy and adhering to legal standards like GDPR and CCPA.

---

## 2. Features

*   **IP Request Logging**: Automatically logs the IP address, timestamp, requested path, and geolocation data for every incoming request using Django middleware.
*   **IP Blacklisting**: A system to block requests from known malicious IP addresses. Blocked IPs are stored in the database and can be managed via a custom Django command.
*   **IP Geolocation**: Enriches log data by mapping IP addresses to their country and city. Results are cached for 24 hours to improve performance and reduce external API calls.
*   **Rate Limiting**: Protects sensitive endpoints from brute-force attacks and abuse by enforcing request limits. It differentiates between authenticated (10 requests/minute) and anonymous users (5 requests/minute).
*   **Anomaly Detection**: A scheduled Celery task runs hourly to analyze logs and flag suspicious IPs based on high request volume or access to sensitive paths (`/admin`, `/login`).

---

## 3. Technologies & Libraries

*   **Backend**: Django
*   **Task Queue**: Celery (for asynchronous anomaly detection)
*   **In-Memory Store**: Redis (as a Celery message broker and for caching)
*   **Key Libraries**:
    *   `django-ratelimit`: For implementing request rate limiting.
    *   `requests`: For making calls to external geolocation APIs.

---

## 4. Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

*   Python 3.8+
*   Pip & Virtualenv
*   Redis Server

### Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/alx-backend-security.git
    cd alx-backend-security/ip_tracking
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to create a `requirements.txt` file if one doesn't exist: `pip freeze > requirements.txt`)*

4.  **Configure Settings**
    Open `settings.py` and make sure your `DATABASES`, `CACHES`, and `CELERY_BROKER_URL` are configured correctly.

    ```python
    # settings.py

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
        }
    }

    # Celery Configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    ```

5.  **Run Database Migrations**
    ```bash
    python manage.py makemigrations ip_tracking
    python manage.py migrate
    ```

6.  **Start the Services**
    You will need to run Redis, the Django development server, and the Celery services in separate terminal windows.

    *   **Terminal 1: Start Redis**
        ```bash
        redis-server
        ```

    *   **Terminal 2: Run the Django Server**
        ```bash
        python manage.py runserver
        ```

    *   **Terminal 3: Run the Celery Worker**
        ```bash
        celery -A your_project_name worker -l info
        ```

    *   **Terminal 4: Run the Celery Beat Scheduler** (for scheduled tasks)
        ```bash
        celery -A your_project_name beat -l info
        ```

---

## 5. Usage and How It Works

### IP Logging and Geolocation

The `ip_tracking/middleware.py` file contains the `IPLoggingAndBlockingMiddleware`. This middleware automatically intercepts every request to:
1.  Extract the client's IP address.
2.  Check if the IP is on the blacklist.
3.  Fetch and cache geolocation data (country, city).
4.  Save all this information to the `RequestLog` model.

### IP Blacklisting

To block an IP address, use the custom management command:
```bash
python manage.py block_ip 192.168.1.100
```
Any subsequent requests from this IP will receive a `403 Forbidden` response.

### Rate Limiting

Rate limiting is applied directly to views using a decorator. In `ip_tracking/views.py`, the `sensitive_login_view` is protected:
```python
from ratelimit.decorators import ratelimit

@ratelimit(group='authenticated', key='user_or_ip', rate='10/m', block=True)
@ratelimit(group='anonymous', key='ip', rate='5/m', block=True)
def sensitive_login_view(request):
    # ... view logic
```
If the request limit is exceeded, a `429 Too Many Requests` response is returned.

### Anomaly Detection

The Celery task defined in `ip_tracking/tasks.py` runs every hour. It analyzes the `RequestLog` table for two conditions:
1.  IPs that have made more than 100 requests in the past hour.
2.  IPs that have accessed sensitive paths like `/admin/` or `/login/`.

Flagged IPs are added to the `SuspiciousIP` table for review.

---

## 6. Project Structure

```
ip_tracking/
├── management/
│   └── commands/
│       └── block_ip.py     # Custom command to block an IP
├── migrations/             # Database migration files
├── __init__.py
├── admin.py
├── apps.py
├── middleware.py           # Core middleware for logging and blocking
├── models.py               # Database models (RequestLog, BlockedIP, SuspiciousIP)
├── tasks.py                # Celery tasks for anomaly detection
├── tests.py
└── views.py                # Views, including the rate-limited endpoint
```

---

## 7. Ethical and Legal Considerations

*   **Privacy & Compliance**: This project logs IP addresses, which can be considered personal data under GDPR/CCPA. Ensure your application has a clear privacy policy that informs users about this practice.
*   **Data Anonymization**: For better privacy, consider anonymizing or truncating IP addresses before long-term storage.
*   **Data Retention**: Implement a data retention policy to automatically delete old logs after a certain period.
*   **Transparency**: Be transparent with users about what data you collect and why. Provide opt-out mechanisms where appropriate.
