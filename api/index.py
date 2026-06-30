import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

# Run migrations on every cold start — /tmp is wiped between instances
from django.core.management import call_command
try:
    call_command('migrate', '--run-syncdb', verbosity=0)
except Exception:
    pass
