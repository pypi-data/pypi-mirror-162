from kabaret import flow
from libreflow.baseflow.site import WorkingSite as BaseWorkingSite
from libreflow.utils.flow.values import MultiOSParam


class WorkingSite(BaseWorkingSite):

    with flow.group('User local workspace'):
        enable_user_workspace = flow.BoolParam(False)
        user_working_dir      = MultiOSParam()
    with flow.group('Package'):
        delivery_dir          = MultiOSParam()

    visible_tasks         = flow.OrderedStringSetParam()
