"""
Admin pages
"""

# Third Party
import humanize

# Django
from django.contrib import admin

# Memberaudit Securegroups
from memberaudit_securegroups.models import (
    ActivityFilter,
    AgeFilter,
    AssetFilter,
    ComplianceFilter,
    SkillPointFilter,
    SkillSetFilter,
)


class SingletonModelAdmin(admin.ModelAdmin):
    """
    Prevents Django admin users deleting the singleton or adding extra rows.
    """

    actions = None  # Removes the default delete action.

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return self.model.objects.all().count() == 0


@admin.register(ActivityFilter)
class ActivityFilterAdmin(admin.ModelAdmin):
    """
    ActivityFilterAdmin
    """

    list_display = ("description", "_inactivity_threshold")

    def _inactivity_threshold(self, obj):
        return f"{obj.inactivity_threshold:d} days"


@admin.register(AgeFilter)
class AgeFilterAdmin(admin.ModelAdmin):
    """
    AgeFilterAdmin
    """

    list_display = ("description", "_age_threshold")

    def _age_threshold(self, obj):
        return f"{obj.age_threshold:d} days"


@admin.register(AssetFilter)
class AssetFilterAdmin(admin.ModelAdmin):
    """
    AssetFilterAdmin
    """

    list_display = ("description",)
    filter_horizontal = ("assets",)


@admin.register(ComplianceFilter)
class ComplianceFilterAdmin(SingletonModelAdmin):
    """
    ComplianceFilterAdmin
    """

    list_display = ("description",)


@admin.register(SkillPointFilter)
class SkillPointFilterAdmin(admin.ModelAdmin):
    """
    SkillPointFilterAdmin
    """

    list_display = ("description", "_skill_point_threshold")

    def _skill_point_threshold(self, obj):
        return f"{humanize.intword(obj.skill_point_threshold)} skill points"


@admin.register(SkillSetFilter)
class SkillSetFilterAdmin(admin.ModelAdmin):
    """
    SkillSetFilterAdmin
    """

    list_display = ("description",)
    filter_horizontal = ("skill_sets",)
