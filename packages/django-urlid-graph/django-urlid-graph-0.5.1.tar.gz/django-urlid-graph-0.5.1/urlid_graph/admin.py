from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from urlid_graph.models import ElementConfig, Entity, JobLog, LogStep, ObjectRepository, SavedGraph


class JobLogAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "description", "current", "progress", "eta",
        "duration", "created", "updated",
    )
    search_fields = ("id", "name", "description")
    readonly_fields = ("progress", "eta", "current_step", "last_updated_at")
    list_filter = ("name",)

    def current(self, instance):
        url = reverse(f"admin:urlid_graph_logstep_add").replace("add/", "") + f"?job__id={instance.id}"
        return format_html(f'{instance.current_step} (<a href="{url}">list</a>)')
    current.description = "Current step"

    def created(self, instance):
        return instance.created_at.strftime("%Y-%m-%d %H:%M:%S %Z")

    def updated(self, instance):
        return instance.created_at.strftime("%Y-%m-%d %H:%M:%S %Z")

    def duration(self, instance):
        if instance.last_updated_at is None:
            return None
        if instance.current_step == "complete":
            return instance.last_updated_at - instance.created_at
        else:
            return timezone.now() - instance.created_at


class LogStepAdmin(admin.ModelAdmin):
    list_display = ("id", "job_id", "created_at", "action", "step", "message", "done", "total")
    search_fields = ("job__id", "action", "step", "message")
    list_filter = ("action", "step")

    def job_id(self, instance):
        if instance.id:
            return instance.job.id
        return "-"

    job_id.short_description = "Job ID"


class EntityAdmin(admin.ModelAdmin):
    pass


class ElementConfigAdmin(admin.ModelAdmin):
    pass


class ObjectRepositoryAdmin(admin.ModelAdmin):
    pass


class SavedGraphAdmin(admin.ModelAdmin):
    pass


admin.site.register(JobLog, JobLogAdmin)
admin.site.register(LogStep, LogStepAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(ElementConfig, ElementConfigAdmin)
admin.site.register(ObjectRepository, ObjectRepositoryAdmin)
admin.site.register(SavedGraph, SavedGraphAdmin)
