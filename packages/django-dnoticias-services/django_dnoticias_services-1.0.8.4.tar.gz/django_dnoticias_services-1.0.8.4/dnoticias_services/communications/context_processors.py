from django.conf import settings


def firebase_configuration() -> dict:
    return {
        "fjs_token_url": settings.NOTIFICATIONS_CREATE_TOKEN_API_URL,
        "fjs_site_domain": settings.NOTIFICATIONS_APPLICATION_DOMAIN,
        "fjs_api_key": settings.FIREBASE_JS_API_KEY,
        "fjs_auth_domain": settings.FIREBASE_JS_AUTH_DOMAIN,
        "fjs_project_id": settings.FIREBASE_JS_PROJECT_ID,
        "fjs_storage_bucket": settings.FIREBASE_JS_STORAGE_BUCKET,
        "fjs_messaging_sender_id": settings.FIREBASE_JS_MESSAGING_SENDER_ID,
        "fjs_app_id": settings.FIREBASE_JS_APP_ID,
        "fjs_measurement_id": settings.FIREBASE_JS_MEASUREMENT_ID,
        "fjs_public_vapid_key": settings.FIREBASE_JS_PUBLIC_VAPID_KEY,
        "fjs_token_cookie_expiration": settings.FIREBASE_JS_TOKEN_COOKIE_EXPIRATION_MINUTES
    }
