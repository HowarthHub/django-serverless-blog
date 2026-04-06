import os

from django.core.asgi import get_asgi_application
from mangum import Mangum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

application = get_asgi_application()

# AWS Lambda handler — API Gateway routes requests through this
handler = Mangum(application)
