import os

from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()

# Mangum wraps Django ASGI for Lambda
_mangum_handler = Mangum(application)


def handler(event, context):
    # If the event contains a "manage" key, run a Django management command
    # e.g. invoke with {"manage": "migrate"} or {"manage": "seed_posts"}
    if "manage" in event:
        from django.core.management import call_command
        call_command(event["manage"])
        return {"statusCode": 200, "body": f"Command '{event['manage']}' completed"}

    return _mangum_handler(event, context)
