class PermissionHelper:
    """Вспомогательный класс для удобного доступа к правам в шаблонах и не только в них."""

    class PermissionRule:
        """
        Правило применения права доступа.
        Определяет, какие действия можно совершать с объектом при наличии этого права.
        Предполагается, что все правила взаимно дополняют друг друга, т.е. действие разрешается,
        если есть хотя бы одно правило, разрешающее его.
        """
        def __init__(self, permission, object_id, allowed_actions):
            self.permission = permission
            self.object_id = object_id
            self.allowed_actions = allowed_actions

    class AnyPermissionRule:
        def __init__(self, permissions, object_id, allowed_actions):
            self.permissions = permissions
            self.object_id = object_id
            self.allowed_actions = allowed_actions

    def __init__(self, user):
        self._permission_rules = {
            self.PermissionRule('main.plan_trips', 'trip', ['add', 'edit']),
            self.PermissionRule('main.plan_trips', 'trip_schedule', ['edit', 'view']),
            self.PermissionRule('main.plan_trips', 'trip_media', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.delete_trips', 'trip', ['delete']),
            self.PermissionRule('main.manage_trip_status', 'trip_status', ['edit']),
            self.PermissionRule('main.manage_trip_tourists', 'trip_tourists', ['edit', 'view']),
            self.PermissionRule('main.manage_trip_tourists', 'trip_inbox_data', ['edit', 'view']),
            self.PermissionRule('main.print_client_contracts', 'client_contracts', ['edit', 'view']),
            self.PermissionRule('main.print_client_contracts', 'trip_tourists', ['view']),
            self.PermissionRule('main.print_trip_reports', 'trip_reports', ['view']),
            self.PermissionRule('main.print_trip_reports', 'trip_tourists', ['view']),
            self.PermissionRule('main.manage_trip_staff', 'trip_staff', ['edit', 'view']),
            self.PermissionRule('main.manage_trip_accommodation', 'trip_accommodation', ['edit', 'view']),
            self.PermissionRule('main.view_trip_accommodation', 'trip_accommodation', ['view']),
            self.PermissionRule('main.manage_routes', 'route', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_hotels', 'hotel', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_hotels', 'hotel', ['delete']),
            self.PermissionRule('main.manage_hotel_bookings', 'hotel_booking', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_cities', 'city', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_cities', 'city', ['delete']),
            self.PermissionRule('main.manage_restaurants', 'restaurant', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_restaurants', 'restaurant', ['delete']),
            self.PermissionRule('main.manage_suppliers', 'supplier', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_suppliers', 'supplier', ['delete']),
            self.PermissionRule('main.manage_supplier_accounts', 'supplier_account', ['add', 'delete', 'view']),
            self.PermissionRule('main.manage_services', 'service', ['add', 'edit', 'view']),
            self.PermissionRule('main.manage_services', 'service_label', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_services', 'service', ['delete']),
            self.PermissionRule('main.delete_services', 'service_label', ['delete']),
            self.PermissionRule('main.manage_clients', 'client', ['add', 'edit', 'view']),
            self.PermissionRule('main.delete_clients', 'client', ['delete']),
            self.PermissionRule('main.export_clients', 'client', ['export']),
            self.PermissionRule('main.manage_coupons', 'promo_code', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_coupons', 'certificate', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_workers', 'worker', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_guide_accounts', 'guide_account', ['add', 'delete', 'view']),
            self.AnyPermissionRule(['main.plan_trips', 'main.manage_trip_status'], 'trip_summary_or_status', ['edit']),
            self.AnyPermissionRule(['main.manage_hotels', 'main.manage_hotel_bookings'], 'hotel_list', ['view']),
            self.AnyPermissionRule([
                'main.manage_hotels', 'main.manage_hotel_bookings', 'main.manage_cities',
                'main.manage_restaurants', 'main.manage_suppliers', 'main.manage_services'
            ], 'directory', ['view']),
            self.PermissionRule('main.manage_employees', 'agency_employee', ['add', 'edit', 'delete', 'view']),
            self.PermissionRule('main.manage_money_statistics', 'trip_money', ['view']),
        }
        self._permissions = {'add': {}, 'edit': {}, 'delete': {}, 'view': {}, 'export': {}}
        for permission_rule in self._permission_rules:
            self.process_permission(user, permission_rule)
        # Добавляем служебную переменную - может ли пользователь добавлять хоть что-то
        self._permissions['add']['something'] = any(self.permissions['add'].values())

    @property
    def permissions(self):
        return self._permissions

    def process_permission(self, user, permission_rule):
        if isinstance(permission_rule, self.AnyPermissionRule):
            has_perm = any(user.has_perm(x) for x in permission_rule.permissions)
        else:
            has_perm = user.has_perm(permission_rule.permission)
        for action in permission_rule.allowed_actions:
            permission_group = self._permissions[action]
            permission_group[permission_rule.object_id] = has_perm or \
                permission_group.get(permission_rule.object_id, False)

    def may_add(self, object_id):
        return self.permissions['add'].get(object_id, False)

    def may_edit(self, object_id):
        return self.permissions['edit'].get(object_id, False)

    def may_delete(self, object_id):
        return self.permissions['delete'].get(object_id, False)

    def may_view(self, object_id):
        return self.permissions['view'].get(object_id, False)

    def may_export(self, object_id):
        return self.permissions['export'].get(object_id, False)
