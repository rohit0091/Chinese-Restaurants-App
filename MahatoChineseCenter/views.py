import os
from django.http import JsonResponse
from django.db import connection

INSTANCE_NAME = os.environ.get("INSTANCE_NAME", "web")


def health_live(request):
    """
    Liveness probe — just confirms the Python/Gunicorn process is alive.
    CloudSentinel uses this to know the container process hasn't crashed.
    Returns 200 immediately — no DB query.
    """
    return JsonResponse({"status": "UP", "service": "MahatoChineseFastFood", "instance": INSTANCE_NAME}, status=200)


def health_ready(request):
    """
    Readiness probe — confirms the app AND its database are ready to serve traffic.
    CloudSentinel monitors this URL every 5 seconds.
    Returns 200 if DB responds, 503 if DB is down (removes replica from Nginx pool).
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({
            "status": "UP",
            "service": "MahatoChineseFastFood",
            "database": "connected",
            "instance": INSTANCE_NAME
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": "DOWN",
            "service": "MahatoChineseFastFood",
            "error": str(e),
            "instance": INSTANCE_NAME
        }, status=503)


def health_check(request):
    """Legacy endpoint — kept for backward compatibility."""
    return health_ready(request)


def app_info(request):
    """
    Legacy/Dashboard test endpoint — returns instance identifier for traffic testing.
    """
    return JsonResponse({"status": "UP", "service": "MahatoChineseFastFood", "instance": INSTANCE_NAME}, status=200)

