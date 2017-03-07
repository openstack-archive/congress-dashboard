from horizon.test.settings import *  # noqa
from openstack_dashboard.test.settings import *  # noqa

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS.append('congress_dashboard')
