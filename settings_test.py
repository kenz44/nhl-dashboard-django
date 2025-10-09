from nhl_dashboard.settings import *
DEBUG = False
DATABASES['default']['NAME'] = BASE_DIR / "db_test.sqlite"

ALLOWED_HOSTS = ['*']