import time
import timeago
import datetime
from packaging import version
from kabaret import flow
from libreflow.baseflow.users import (
    User as BaseUser,
    UserProfile as BaseUserProfile,
)
from libreflow.utils.flow.values import MultiOSParam


class UserProfile(BaseUserProfile):

    working_dir = flow.Computed(cached=True).ui(hidden=True)

    def compute_child_value(self, child_value):
        if child_value is self.working_dir:
            user = self.root().project().get_user()
            wd = user.working_dir.get()

            if wd is None:
                site = self.root().project().get_current_site()
                wd = site.user_working_dir.get()
            
            self.working_dir.set(wd)
        else:
            super(UserProfile, self).compute_child_value(child_value)


class User(BaseUser):

    last_visit                   = flow.Computed()
    libreflow_version            = flow.Computed().ui(label='libreflow')
    project_version              = flow.Computed().ui(label='libreflow.rouge')
    working_dir                  = MultiOSParam()

    _last_visit                  = flow.IntParam(0)
    _last_libreflow_used_version = flow.Param(None)
    _last_project_used_version   = flow.Param(None)

    def compute_child_value(self, child_value):
        if child_value is self.last_visit:
            if self._last_visit.get() == 0:
                self.last_visit.set('never')
            else:
                last_connection = datetime.datetime.fromtimestamp(
                    self._last_visit.get()
                )
                now = datetime.datetime.now()
                self.last_visit.set(timeago.format(last_connection, now))
        elif child_value is self.libreflow_version:
            requiered_version = version.parse(
                self.root().project().admin.project_settings.libreflow_version.get()
            )
            user_current_version = self._last_libreflow_used_version.get()

            if not user_current_version:
                self.libreflow_version.set('Unknown')
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    self.libreflow_version.set(
                        '%s (!)' % str(user_current_version)
                    )
                else:
                    self.libreflow_version.set(
                        '%s' % str(user_current_version)
                    )
        elif child_value is self.project_version:
            requiered_version = version.parse(
                self.root().project().admin.project_settings.project_version.get()
            )
            user_current_version = self._last_project_used_version.get()

            if not user_current_version:
                self.project_version.set('Unknown')
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    self.project_version.set(
                        '%s (!)' % str(user_current_version)
                    )
                else:
                    self.project_version.set(
                        '%s' % str(user_current_version)
                    )
