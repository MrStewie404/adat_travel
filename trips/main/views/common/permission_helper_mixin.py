from main.business_logic.permission_helper import PermissionHelper


class PermissionHelperMixin:
    permission_helper = None

    def dispatch(self, request, *args, **kwargs):
        self.permission_helper = PermissionHelper(request.user)
        return super().dispatch(request, *args, **kwargs)
