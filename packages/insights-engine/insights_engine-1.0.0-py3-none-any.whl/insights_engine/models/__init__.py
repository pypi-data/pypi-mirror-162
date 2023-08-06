# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from insights_engine.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from insights_engine.model.add_filter_batch_input import AddFilterBatchInput
from insights_engine.model.add_filter_batch_output import AddFilterBatchOutput
from insights_engine.model.add_filter_input import AddFilterInput
from insights_engine.model.add_filter_output import AddFilterOutput
from insights_engine.model.add_members_input import AddMembersInput
from insights_engine.model.add_members_output import AddMembersOutput
from insights_engine.model.add_subscription_input import AddSubscriptionInput
from insights_engine.model.add_user_input import AddUserInput
from insights_engine.model.add_user_output import AddUserOutput
from insights_engine.model.create_group_input import CreateGroupInput
from insights_engine.model.create_group_output import CreateGroupOutput
from insights_engine.model.delete_batch_filter_output import DeleteBatchFilterOutput
from insights_engine.model.delete_filter_batch_input import DeleteFilterBatchInput
from insights_engine.model.delete_filter_input import DeleteFilterInput
from insights_engine.model.delete_filter_output import DeleteFilterOutput
from insights_engine.model.delete_group_members_input import DeleteGroupMembersInput
from insights_engine.model.delete_subscription_input import DeleteSubscriptionInput
from insights_engine.model.filter import Filter
from insights_engine.model.filter_out import FilterOut
from insights_engine.model.get_all_admin_groups_output import GetAllAdminGroupsOutput
from insights_engine.model.get_context_insights_input import GetContextInsightsInput
from insights_engine.model.get_context_insights_output import GetContextInsightsOutput
from insights_engine.model.get_filter_output import GetFilterOutput
from insights_engine.model.get_group_admins_output import GetGroupAdminsOutput
from insights_engine.model.get_group_insights_output import GetGroupInsightsOutput
from insights_engine.model.get_group_members_ouput import GetGroupMembersOuput
from insights_engine.model.get_user_insights_output import GetUserInsightsOutput
from insights_engine.model.get_user_output import GetUserOutput
from insights_engine.model.get_user_subscriptions_output import GetUserSubscriptionsOutput
from insights_engine.model.group_description import GroupDescription
from insights_engine.model.insight_payload import InsightPayload
from insights_engine.model.permission import Permission
from insights_engine.model.save_insight_input import SaveInsightInput
from insights_engine.model.subscription import Subscription
from insights_engine.model.teams_permission_value import TeamsPermissionValue
from insights_engine.model.unsave_insight_input import UnsaveInsightInput
from insights_engine.model.update_user_input import UpdateUserInput
from insights_engine.model.user import User
from insights_engine.model.user_out import UserOut
from insights_engine.model.window import Window
