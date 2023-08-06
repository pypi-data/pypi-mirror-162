from typing import Tuple

from django.apps import apps as django_apps
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin as BaseSimpleHistoryAdmin


class SimpleHistoryAdmin(BaseSimpleHistoryAdmin):

    history_list_display: Tuple[str, ...] = ("dashboard", "change_message")
    object_history_template = "edc_model_admin/admin/object_history.html"
    object_history_form_template = "edc_model_admin/admin/object_history_form.html"

    save_as = False
    save_as_continue = False

    def change_message(self, obj):
        log_entry_model_cls = django_apps.get_model("admin.logentry")
        log_entry = (
            log_entry_model_cls.objects.filter(
                action_time__gte=obj.modified, object_id=str(obj.id)
            )
            .order_by("action_time")
            .first()
        )
        if log_entry:
            return format_html(log_entry.get_change_message())
        return None

    change_message.short_description = "Change Message"

    def dashboard(self, obj):
        if callable(self.view_on_site):
            return format_html('<A href="{}">Dashboard</A>', self.view_on_site(obj))
        return None
