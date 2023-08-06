"""
App's base definitions
"""

# Django
from django.apps import AppConfig


class MemberAuditSecureGroupsConfig(AppConfig):
    """
    MemberAuditSecureGroupsConfig
    """

    name = "memberaudit_securegroups"
    label = "memberaudit_securegroups"
    verbose_name = "Member Audit Secure Groups Integration"
