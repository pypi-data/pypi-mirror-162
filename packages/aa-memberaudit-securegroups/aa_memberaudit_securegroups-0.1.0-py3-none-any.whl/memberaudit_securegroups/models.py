"""
The models
"""

# Standard Library
import datetime

# Third Party
import humanize

# Django
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

# Member Audit
from memberaudit.models import Character, CharacterAsset, General, SkillSet

# Alliance Auth (External Libs)
from eveuniverse.models import EveType


class SingletonModel(models.Model):
    """
    SingletonModel
    """

    class Meta:
        """
        Model meta definitions
        """

        abstract = True

    def delete(self, *args, **kwargs):
        """
        delete action
        :param args:
        :param kwargs:
        :return:
        """

        pass

    def set_cache(self):
        """
        Setting cache
        :return:
        """

        cache.set(self.__class__.__name__, self)

    def save(self, *args, **kwargs):
        """
        save action
        :param args:
        :param kwargs:
        :return:
        """

        self.pk = 1
        super().save(*args, **kwargs)

        self.set_cache()

    @classmethod
    def load(cls):
        """
        Get cache
        :return:
        """

        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)

            if not created:
                obj.set_cache()

        return cache.get(cls.__name__)


class BaseFilter(models.Model):
    """
    BaseFilter
    """

    description = models.CharField(
        max_length=500,
        help_text=_("The filter description that is shown to end users."),
    )  # this is what is shown to the user

    class Meta:
        """
        Model meta definitions
        """

        abstract = True

    def __str__(self):
        """
        Model stringified name
        :return:
        """

        return f"{self.name}: {self.description}"

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return "Compliance"

    def process_filter(self, user: User):
        """
        This is the check run against a users characters
        :param user:
        :return:
        """

        raise NotImplementedError("Please Create a filter!")


class ActivityFilter(BaseFilter):
    """
    ActivityFilter
    """

    inactivity_threshold = models.PositiveIntegerField(
        help_text=_("Maximum allowable inactivity, in <strong>days</strong>."),
    )

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return f"Activity [days={self.inactivity_threshold}]"

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        threshold_date = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=self.inactivity_threshold)

        return (
            Character.objects.owned_by_user(user=user)
            .filter(
                Q(online_status__last_login__gt=threshold_date)
                | Q(online_status__last_logout__gt=threshold_date),
            )
            .count()
            > 0
        )


class AgeFilter(BaseFilter):
    """
    AgeFilter
    """

    age_threshold = models.PositiveIntegerField(
        help_text=_("Minimum allowable age, in <strong>days</strong>."),
    )

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return f"Member Audit Age [days={self.age_threshold}]"

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        threshold_date = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(days=self.age_threshold)

        return (
            Character.objects.owned_by_user(user=user)
            .filter(
                details__birthday__lt=threshold_date,
            )
            .count()
            > 0
        )


class AssetFilter(BaseFilter):
    """
    AssetFilter
    """

    assets = models.ManyToManyField(
        EveType,
        help_text=_("User must possess <strong>one</strong> of the selected assets."),
    )

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return "Member Audit Asset"

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        characters = Character.objects.owned_by_user(user=user)

        return (
            CharacterAsset.objects.filter(
                character__in=characters, eve_type__in=self.assets.all()
            ).count()
            > 0
        )


class ComplianceFilter(BaseFilter, SingletonModel):
    """
    ComplianceFilter
    """

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        is_compliant = General.compliant_users().filter(pk=user.pk).exists()

        return is_compliant


class SkillPointFilter(BaseFilter):
    """
    SkillPointFilter
    """

    skill_point_threshold = models.PositiveBigIntegerField(
        help_text=_("Minimum allowable skillpoints."),
    )

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return (
            "Member Audit Skill Points "
            f"[sp={humanize.intword(self.skill_point_threshold)}]"
        )

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        return (
            Character.objects.owned_by_user(user=user)
            .filter(
                skillpoints__total__gt=self.skill_point_threshold,
            )
            .count()
            > 0
        )


class SkillSetFilter(BaseFilter):
    """
    SkillSetFilter
    """

    skill_sets = models.ManyToManyField(
        SkillSet,
        help_text=_(
            "Users must possess all of the skills in <strong>one</strong> of the "
            "selected skillsets."
        ),
    )

    @property
    def name(self):
        """
        Filter name
        :return:
        """

        return "Member Audit Skill Set"

    def process_filter(self, user: User):
        """
        Processing filter
        :param user:
        :return:
        """

        characters = Character.objects.owned_by_user(user=user)

        for character in characters:
            for check in character.skill_set_checks.filter(
                skill_set__in=self.skill_sets.all()
            ):
                if check.failed_required_skills.count() == 0:
                    return True

        return False
