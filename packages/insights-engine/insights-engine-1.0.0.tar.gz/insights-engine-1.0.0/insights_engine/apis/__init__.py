
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.filter_api import FilterApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from insights_engine.api.filter_api import FilterApi
from insights_engine.api.groups_api import GroupsApi
from insights_engine.api.insights_api import InsightsApi
from insights_engine.api.metrics_api import MetricsApi
from insights_engine.api.save_api import SaveApi
from insights_engine.api.subscriptions_api import SubscriptionsApi
from insights_engine.api.user_api import UserApi
